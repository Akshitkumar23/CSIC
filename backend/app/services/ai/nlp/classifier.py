"""Local Statistical Intent Classifier and Evaluation Metrics for CSIC.

Provides a fast, CPU-compatible TF-IDF + Logistic Regression / Softmax classifier
operating 100% offline with zero external AI API calls.

Supports scikit-learn when installed, with an integrated NumPy-based
TF-IDF + Softmax linear classifier fallback.
"""
from dataclasses import dataclass, field
import logging
import math
import re
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from backend.app.services.ai.nlp.dataset import TRAIN_DATA, TEST_DATA
from backend.app.services.ai.nlp.preprocessor import TextPreprocessor, EntityExtractor

logger = logging.getLogger("csic.ai.nlp")


@dataclass
class IntentPrediction:
    """Structured result of a local intent classification."""
    raw_query: str
    normalized_query: str
    intent: str
    confidence: float
    is_low_confidence: bool
    is_hinglish: bool
    entities: Dict[str, Any]
    probabilities: Dict[str, float] = field(default_factory=dict)


class NumpyTfidfClassifier:
    """CPU-compatible pure NumPy TF-IDF feature extractor + Softmax linear classifier."""

    def __init__(self, ngram_range: Tuple[int, int] = (1, 2), max_features: int = 1500) -> None:
        self.ngram_range = ngram_range
        self.max_features = max_features
        self.vocab: Dict[str, int] = {}
        self.idf_: np.ndarray = np.array([])
        self.classes_: List[str] = []
        self.W: np.ndarray = np.array([])  # shape: (n_features, n_classes)
        self.b: np.ndarray = np.array([])  # shape: (n_classes,)
        self.fitted: bool = False

    def _extract_ngrams(self, text: str) -> List[str]:
        """Extract word and character boundary n-grams."""
        words = re.findall(r"\b[a-z0-9_]+\b", text.lower())
        tokens: List[str] = []

        # Word n-grams
        min_n, max_n = self.ngram_range
        for n in range(min_n, max_n + 1):
            for i in range(len(words) - n + 1):
                tokens.append(" ".join(words[i:i + n]))

        # Sub-word char 3-grams for typo resilience
        for w in words:
            if len(w) >= 3:
                for j in range(len(w) - 2):
                    tokens.append(f"__char_{w[j:j+3]}__")

        return tokens

    def fit(self, texts: List[str], labels: List[str], epochs: int = 250, lr: float = 0.25, reg: float = 0.001) -> "NumpyTfidfClassifier":
        """Train TF-IDF vocabulary and Softmax classifier via gradient descent."""
        # 1. Build vocabulary and document frequency
        df: Dict[str, int] = {}
        n_docs = len(texts)

        for text in texts:
            unique_tokens = set(self._extract_ngrams(text))
            for tok in unique_tokens:
                df[tok] = df.get(tok, 0) + 1

        # Select top features
        sorted_tokens = sorted(df.items(), key=lambda x: x[1], reverse=True)[:self.max_features]
        self.vocab = {tok: idx for idx, (tok, _) in enumerate(sorted_tokens)}

        # 2. Compute smooth IDF: ln((1 + N) / (1 + df)) + 1
        n_features = len(self.vocab)
        self.idf_ = np.zeros(n_features, dtype=np.float32)
        for tok, idx in self.vocab.items():
            self.idf_[idx] = math.log((1 + n_docs) / (1 + df[tok])) + 1.0

        # 3. Vectorize training documents
        X = self._transform_matrix(texts)

        # 4. Map class labels
        self.classes_ = sorted(list(set(labels)))
        class_to_idx = {c: idx for idx, c in enumerate(self.classes_)}
        n_classes = len(self.classes_)
        y = np.array([class_to_idx[lbl] for lbl in labels], dtype=np.int32)

        # One-hot encoding of y
        Y_onehot = np.zeros((n_docs, n_classes), dtype=np.float32)
        Y_onehot[np.arange(n_docs), y] = 1.0

        # 5. Initialize weights and bias
        np.random.seed(42)
        self.W = np.random.randn(n_features, n_classes).astype(np.float32) * 0.01
        self.b = np.zeros(n_classes, dtype=np.float32)

        # 6. Gradient Descent with Momentum
        v_W = np.zeros_like(self.W)
        v_b = np.zeros_like(self.b)
        momentum = 0.9

        for epoch in range(epochs):
            # Forward pass: logits = X @ W + b
            logits = np.dot(X, self.W) + self.b
            # Softmax
            exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
            probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)

            # Backward pass (Cross-Entropy Gradient)
            grad_logits = (probs - Y_onehot) / n_docs
            grad_W = np.dot(X.T, grad_logits) + reg * self.W
            grad_b = np.sum(grad_logits, axis=0)

            # Update with momentum
            v_W = momentum * v_W + lr * grad_W
            v_b = momentum * v_b + lr * grad_b
            self.W -= v_W
            self.b -= v_b

        self.fitted = True
        return self

    def _transform_matrix(self, texts: List[str]) -> np.ndarray:
        """Convert a list of raw text strings to L2-normalized TF-IDF matrix."""
        n_docs = len(texts)
        n_features = len(self.vocab)
        X = np.zeros((n_docs, n_features), dtype=np.float32)

        for doc_idx, text in enumerate(texts):
            tokens = self._extract_ngrams(text)
            tf: Dict[int, float] = {}
            for tok in tokens:
                if tok in self.vocab:
                    idx = self.vocab[tok]
                    tf[idx] = tf.get(idx, 0.0) + 1.0

            # Sublinear TF scaling: 1 + ln(count)
            for idx, count in tf.items():
                X[doc_idx, idx] = (1.0 + math.log(count)) * self.idf_[idx]

            # L2 normalization
            norm = np.linalg.norm(X[doc_idx])
            if norm > 0:
                X[doc_idx] /= norm

        return X

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        """Predict calibrated probability distribution over all classes."""
        if not self.fitted:
            raise ValueError("Classifier is not fitted yet.")
        X = self._transform_matrix(texts)
        logits = np.dot(X, self.W) + self.b
        exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
        return exp_logits / np.sum(exp_logits, axis=1, keepdims=True)


class LocalIntentClassifier:
    """Production-grade local intent classifier combining text normalization, statistical model, and entities."""

    def __init__(self, confidence_threshold: float = 0.38) -> None:
        self.confidence_threshold = confidence_threshold
        self.model: Any = None
        self.classes: List[str] = []
        self._is_sklearn: bool = False
        self._train_and_initialize()

    def _train_and_initialize(self) -> None:
        """Train model using either scikit-learn (if available) or NumPy classifier."""
        texts = [d["text"] for d in TRAIN_DATA]
        normalized_texts = [TextPreprocessor.apply_phrase_normalization(t) for t in texts]
        labels = [d["intent"] for d in TRAIN_DATA]

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
            from sklearn.pipeline import Pipeline

            pipeline = Pipeline([
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1)),
                ("clf", LogisticRegression(C=5.0, max_iter=1000, random_state=42)),
            ])
            pipeline.fit(normalized_texts, labels)
            self.model = pipeline
            self.classes = list(pipeline.named_steps["clf"].classes_)
            self._is_sklearn = True
            logger.info("LocalIntentClassifier initialized using scikit-learn pipeline.")
        except Exception as e:
            # Fall back cleanly to self-contained NumPy classifier
            np_clf = NumpyTfidfClassifier(ngram_range=(1, 2), max_features=1200)
            np_clf.fit(normalized_texts, labels, epochs=300, lr=0.3, reg=0.0005)
            self.model = np_clf
            self.classes = np_clf.classes_
            self._is_sklearn = False
            logger.info("LocalIntentClassifier initialized using built-in NumPy engine: %s", e)

    def classify(self, text: str) -> IntentPrediction:
        """Classify student utterance into intent, extract entities, and compute confidence."""
        is_hinglish = TextPreprocessor.detect_hinglish(text)
        normalized = TextPreprocessor.apply_phrase_normalization(text)
        entities = EntityExtractor.extract_all(text)

        # Predict probability distribution
        if self._is_sklearn:
            probs = self.model.predict_proba([normalized])[0]
        else:
            probs = self.model.predict_proba([normalized])[0]

        best_idx = int(np.argmax(probs))
        best_intent = self.classes[best_idx]
        confidence = float(probs[best_idx])

        prob_dict = {cls_name: round(float(prob), 4) for cls_name, prob in zip(self.classes, probs)}

        # Rule-guided boost for explicit keyword signals
        lower = text.lower()
        if re.search(r"\b(passing marks|passing criteria|detention rule|condonation criteria|refund policy|attendance policy|examination code|code of conduct)\b", lower):
            best_intent = "policy_lookup"
            confidence = max(confidence, 0.92)
        elif re.search(r"\b(holiday|circular|announcement|notices?)\b", lower):
            best_intent = "notices"
            confidence = max(confidence, 0.90)
        elif re.search(r"\b(how many lectures have i attended|total classes attended|attended so far|did i attend)\b", lower):
            best_intent = "attendance_lookup"
            confidence = max(confidence, 0.92)
        elif re.search(r"\b(that subject|in that subject|this subject|in this one|usme|what about cs\s*40[1-4]|and in)\b", lower) and not re.search(r"\b(attendance in|marks in)\b", lower):
            best_intent = "follow_up"
            confidence = max(confidence, 0.90)
        elif re.search(r"\b(classes|lectures|bunk|miss|safe bunks)\b", lower) and re.search(r"\b(how many|kitni|need|padengi|can i|recover)\b", lower):
            best_intent = "academic_calculation"
            confidence = max(confidence, 0.88)
        elif re.search(r"\b(timetable|schedule|class timings)\b", lower) or re.search(r"\baaj (kaun|kaunsi)\b", lower):
            best_intent = "timetable"
            confidence = max(confidence, 0.90)
        elif re.search(r"\b(fees?|invoice|dues|balance|fine)\b", lower) and re.search(r"\b(balance|pending|pay|baki|kitni)\b", lower):
            best_intent = "fee_status"
            confidence = max(confidence, 0.90)
        elif re.search(r"\b(hello|hi|hey|namaste|good morning|who are you|what can you do|help me)\b", lower):
            best_intent = "greeting"
            confidence = max(confidence, 0.90)
        elif re.search(r"\b(marks|grade|sgpa|cgpa|gpa|score|results?)\b", lower):
            best_intent = "marks_explanation"
            confidence = max(confidence, 0.90)

        is_low_conf = confidence < self.confidence_threshold
        if is_low_conf:
            best_intent = "low_confidence"

        return IntentPrediction(
            raw_query=text,
            normalized_query=normalized,
            intent=best_intent,
            confidence=round(confidence, 4),
            is_low_confidence=is_low_conf,
            is_hinglish=is_hinglish,
            entities=entities,
            probabilities=prob_dict,
        )

    def evaluate(self, test_set: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Evaluate classifier accuracy, precision, recall, and F1 on the benchmark test set."""
        dataset = test_set or TEST_DATA
        total = len(dataset)
        if total == 0:
            return {"total": 0, "accuracy": 0.0}

        y_true = [d["intent"] for d in dataset]
        y_pred = []

        per_class_tp: Dict[str, int] = {c: 0 for c in self.classes}
        per_class_fp: Dict[str, int] = {c: 0 for c in self.classes}
        per_class_fn: Dict[str, int] = {c: 0 for c in self.classes}

        correct = 0
        for sample in dataset:
            pred = self.classify(sample["text"])
            pred_intent = pred.intent
            true_intent = sample["intent"]
            y_pred.append(pred_intent)

            is_match = (pred_intent == true_intent) or (true_intent == "out_of_domain" and pred_intent in ("out_of_domain", "low_confidence"))
            if is_match:
                correct += 1
                matched_class = true_intent if true_intent in self.classes else pred_intent
                if matched_class in per_class_tp:
                    per_class_tp[matched_class] += 1
            else:
                if pred_intent in per_class_fp:
                    per_class_fp[pred_intent] += 1
                if true_intent in per_class_fn:
                    per_class_fn[true_intent] += 1

        accuracy = correct / total

        # Compute per-class Precision, Recall, F1
        class_metrics: Dict[str, Dict[str, float]] = {}
        precisions: List[float] = []
        recalls: List[float] = []
        f1s: List[float] = []

        for c in self.classes:
            tp = per_class_tp[c]
            fp = per_class_fp[c]
            fn = per_class_fn[c]

            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

            class_metrics[c] = {
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "support": tp + fn,
            }
            if (tp + fn) > 0:
                precisions.append(prec)
                recalls.append(rec)
                f1s.append(f1)

        macro_precision = float(np.mean(precisions)) if precisions else 0.0
        macro_recall = float(np.mean(recalls)) if recalls else 0.0
        macro_f1 = float(np.mean(f1s)) if f1s else 0.0

        return {
            "engine": "scikit-learn" if self._is_sklearn else "NumPy",
            "total_samples": total,
            "correct_samples": correct,
            "accuracy": round(accuracy, 4),
            "macro_precision": round(macro_precision, 4),
            "macro_recall": round(macro_recall, 4),
            "macro_f1": round(macro_f1, 4),
            "per_class": class_metrics,
        }


# Singleton instance
classifier_instance = LocalIntentClassifier()
