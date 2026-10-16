"""Independent Holdout Evaluation and Benchmarking Script for CSIC.

Evaluates the frozen LocalIntentClassifier on the untouched 55-sample HOLDOUT_DATA.
Calculates confusion matrix, precision, recall, F1-scores, and error breakdown.
"""
import json
from typing import Any, Dict, List
import numpy as np

from backend.app.services.ai.nlp.classifier import LocalIntentClassifier
from backend.app.services.ai.nlp.holdout_dataset import HOLDOUT_DATA
from backend.app.services.ai.nlp.dataset import TRAIN_DATA, TEST_DATA


def run_holdout_evaluation() -> Dict[str, Any]:
    # Initialize frozen classifier
    clf = LocalIntentClassifier(confidence_threshold=0.25)
    classes = sorted(list(set([d["intent"] for d in HOLDOUT_DATA])))

    total = len(HOLDOUT_DATA)
    confusion_matrix: Dict[str, Dict[str, int]] = {c: {c2: 0 for c2 in classes + ["low_confidence"]} for c in classes}
    misclassified: List[Dict[str, Any]] = []

    correct = 0
    for sample in HOLDOUT_DATA:
        text = sample["text"]
        true_intent = sample["intent"]
        pred = clf.classify(text)
        pred_intent = pred.intent

        # Record confusion
        if pred_intent in confusion_matrix[true_intent]:
            confusion_matrix[true_intent][pred_intent] += 1
        else:
            confusion_matrix[true_intent]["low_confidence"] += 1

        # Out of domain queries rejected as low_confidence or out_of_domain are correct refusals
        is_match = (pred_intent == true_intent) or (true_intent == "out_of_domain" and pred_intent in ("out_of_domain", "low_confidence"))

        if is_match:
            correct += 1
        else:
            misclassified.append({
                "text": text,
                "true_intent": true_intent,
                "pred_intent": pred_intent,
                "confidence": pred.confidence,
                "is_hinglish": pred.is_hinglish,
                "entities": pred.entities,
            })

    accuracy = correct / total

    # Per-class metrics
    class_metrics: Dict[str, Dict[str, float]] = {}
    precisions: List[float] = []
    recalls: List[float] = []
    f1s: List[float] = []

    for c in classes:
        # TP: true_intent == c and pred_intent matches
        tp = sum(1 for s in HOLDOUT_DATA if s["intent"] == c and ((clf.classify(s["text"]).intent == c) or (c == "out_of_domain" and clf.classify(s["text"]).intent in ("out_of_domain", "low_confidence"))))
        # FP: true_intent != c and pred_intent == c
        fp = sum(1 for s in HOLDOUT_DATA if s["intent"] != c and clf.classify(s["text"]).intent == c)
        # FN: true_intent == c and not is_match
        fn = sum(1 for s in HOLDOUT_DATA if s["intent"] == c and not ((clf.classify(s["text"]).intent == c) or (c == "out_of_domain" and clf.classify(s["text"]).intent in ("out_of_domain", "low_confidence"))))

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        support = tp + fn
        class_metrics[c] = {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "support": support,
        }
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)

    macro_precision = float(np.mean(precisions))
    macro_recall = float(np.mean(recalls))
    macro_f1 = float(np.mean(f1s))

    return {
        "engine": "NumPy TF-IDF + Softmax Linear Regression",
        "train_samples_count": len(TRAIN_DATA),
        "dev_samples_count": len(TEST_DATA),
        "holdout_samples_count": total,
        "correct_samples": correct,
        "accuracy": round(accuracy, 4),
        "macro_precision": round(macro_precision, 4),
        "macro_recall": round(macro_recall, 4),
        "macro_f1": round(macro_f1, 4),
        "per_class": class_metrics,
        "confusion_matrix": confusion_matrix,
        "misclassified": misclassified,
    }


if __name__ == "__main__":
    report = run_holdout_evaluation()
    print(json.dumps(report, indent=2))
