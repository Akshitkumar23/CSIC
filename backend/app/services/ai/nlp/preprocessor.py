"""Text Preprocessing, Hinglish Normalization, and Entity Extraction.

Cleans student input, normalizes spelling and transliterated Hinglish idioms,
and extracts canonical entities (subjects, exams, temporal days, percentage targets).
"""
import re
import unicodedata
from typing import Any, Dict, List, Optional, Set, Tuple


# Canonical subject catalog
SUBJECT_CATALOG: Dict[str, Dict[str, Any]] = {
    "CS401": {
        "code": "CS401",
        "name": "Cloud Computing",
        "aliases": ["cloud computing", "cloud", "cc", "cs 401", "cs401"],
    },
    "CS402": {
        "code": "CS402",
        "name": "Machine Learning",
        "aliases": ["machine learning", "ml", "cs 402", "cs402"],
    },
    "CS403": {
        "code": "CS403",
        "name": "Database Management Systems",
        "aliases": ["database management systems", "database", "dbms", "cs 403", "cs403"],
    },
    "CS404": {
        "code": "CS404",
        "name": "Computer Networks",
        "aliases": ["computer networks", "networks", "cn", "cs 404", "cs404"],
    },
}

# Hinglish stopwords and markers indicating Indic conversational phrasing
HINGLISH_MARKERS: Set[str] = {
    "meri", "mera", "mere", "mujhe", "apna", "apni",
    "kya", "kyun", "kaise", "kisko", "kaunsi", "kaun", "kab", "kaha",
    "kitni", "kitne", "kitna", "bohot", "kam", "jyada",
    "padegi", "padengi", "padega", "chahiye", "karun", "karein", "karo", "batao", "bataiye", "dikhao",
    "hai", "hain", "tha", "the", "thi", "hogi", "hoga", "honge",
    "aaj", "kal", "parso", "chutti", "chuttee",
    "baki", "bachi", "chal", "rahi", "raha", "shortage", "aa", "gayi", "gaya",
    "mein", "me", "pe", "par", "se", "ko", "ke", "ki", "ka",
}

# Label-independent linguistic normalization dictionary (no synthetic intent label injection)
HINGLISH_LINGUISTIC_NORMALIZATIONS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"\bhaz[a-z]*r[i]?\b", re.IGNORECASE), "attendance"),
    (re.compile(r"\bchhutti\b|\bchutti\b", re.IGNORECASE), "holiday"),
    (re.compile(r"\bpariksha\b|\bimtehan\b", re.IGNORECASE), "exam"),
    (re.compile(r"\bbaki\b|\bbachi\b", re.IGNORECASE), "pending"),
    (re.compile(r"\baaj\b", re.IGNORECASE), "today"),
    (re.compile(r"\bkal\b", re.IGNORECASE), "tomorrow"),
    (re.compile(r"\bshukriya\b|\bdhanyawad\b", re.IGNORECASE), "thank you"),
    (re.compile(r"\bnamaskar\b|\bnamaste\b|\bpranam\b", re.IGNORECASE), "hello"),
]


class TextPreprocessor:
    """Cleans, normalizes, and extracts language cues from student input."""

    @staticmethod
    def normalize_text(text: str) -> str:
        """Strip accents, normalize Unicode, lowercase, and collapse whitespace."""
        if not text:
            return ""
        # Unicode NFKD decomposition
        text = unicodedata.normalize("NFKD", text)
        # Lowercase
        text = text.lower()
        # Normalize punctuation and hyphens
        text = re.sub(r"[\u2018\u2019\u201A\u201B]", "'", text)
        text = re.sub(r"[\u201C\u201D\u201E\u201F]", '"', text)
        text = re.sub(r"[\u2013\u2014]", "-", text)
        # Collapse multiple spaces
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def detect_hinglish(text: str) -> bool:
        """Return True if the text contains recognizable Hinglish tokens."""
        tokens = set(re.findall(r"\b[a-z]+\b", text.lower()))
        matches = tokens.intersection(HINGLISH_MARKERS)
        return len(matches) >= 1

    @classmethod
    def apply_phrase_normalization(cls, text: str) -> str:
        """Apply label-independent text cleaning and standard linguistic transliteration."""
        normalized = cls.normalize_text(text)
        for pattern, replacement in HINGLISH_LINGUISTIC_NORMALIZATIONS:
            normalized = pattern.sub(replacement, normalized)
        return normalized


class EntityExtractor:
    """Extracts structured academic entities from normalized input."""

    @staticmethod
    def extract_subject(text: str) -> Optional[str]:
        """Match subject codes or common aliases, returning canonical code (e.g. 'CS401')."""
        lower = text.lower()

        # 1. Direct Regex match for CS401-CS404
        match = re.search(r"\bcs\s*[-_]?\s*(40[1-4])\b", lower)
        if match:
            return f"CS{match.group(1)}"

        # 2. Match aliases
        for code, info in SUBJECT_CATALOG.items():
            for alias in info["aliases"]:
                if re.search(rf"\b{re.escape(alias)}\b", lower):
                    return code

        return None

    @staticmethod
    def extract_exam(text: str) -> Optional[str]:
        """Match exam types, returning canonical exam name ('Midterm', 'Endterm', etc.)."""
        lower = text.lower()
        if re.search(r"\b(midterm|mid[- ]?sem|midsem|cia|internal)\b", lower):
            return "Midterm"
        if re.search(r"\b(endterm|end[- ]?sem|endsem|final|semester exam)\b", lower):
            return "Endterm"
        if re.search(r"\bquiz\b", lower):
            return "Quiz"
        if re.search(r"\bassignment\b", lower):
            return "Assignment"
        return None

    @staticmethod
    def extract_day(text: str) -> Optional[str]:
        """Extract day references ('today', 'tomorrow', 'monday', etc.)."""
        lower = text.lower()
        if re.search(r"\b(today|aaj)\b", lower):
            return "today"
        if re.search(r"\b(tomorrow|kal)\b", lower):
            return "tomorrow"

        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day in days:
            if re.search(rf"\b{day}\b", lower):
                return day
        return None

    @staticmethod
    def extract_target_percentage(text: str) -> Optional[int]:
        """Extract attendance or score target percentage (e.g. 75, 80)."""
        match = re.search(r"\b(\d{1,2})\s*(?:%|percent)\b", text.lower())
        if match:
            return int(match.group(1))
        return None

    @classmethod
    def extract_all(cls, text: str) -> Dict[str, Any]:
        """Extract all identifiable academic entities into a structured dictionary."""
        entities: Dict[str, Any] = {}
        subject = cls.extract_subject(text)
        if subject:
            entities["subject"] = subject

        exam = cls.extract_exam(text)
        if exam:
            entities["exam"] = exam

        day = cls.extract_day(text)
        if day:
            entities["day"] = day

        target = cls.extract_target_percentage(text)
        if target:
            entities["target"] = target

        return entities
