"""Local NLP and Intent Classification Engine for CSIC.

Provides offline, CPU-compatible text normalization, entity extraction,
statistical intent classification, and evaluation metrics with zero external AI API dependencies.
"""
from backend.app.services.ai.nlp.dataset import TRAIN_DATA, TEST_DATA
from backend.app.services.ai.nlp.preprocessor import TextPreprocessor, EntityExtractor
from backend.app.services.ai.nlp.classifier import LocalIntentClassifier

__all__ = [
    "TRAIN_DATA",
    "TEST_DATA",
    "TextPreprocessor",
    "EntityExtractor",
    "LocalIntentClassifier",
]
