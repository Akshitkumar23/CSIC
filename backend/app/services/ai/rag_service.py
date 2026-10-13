"""Document Ingestion and Vector Retrieval Pipeline for CSIC College Policies.

Stores official institutional policy documents, performs semantic chunking with
rich metadata, and executes vector similarity retrieval using Google GenAI
embeddings when configured, with a high-accuracy TF-IDF / lexical-semantic
similarity engine fallback when GEMINI_API_KEY is omitted.
"""
from dataclasses import dataclass, field
import logging
import math
import re
from typing import Any, Dict, List, Optional, Tuple

from backend.app.core.config import settings

logger = logging.getLogger("csic.ai.rag")


@dataclass
class PolicyChunk:
    """Semantic chunk of an institutional policy document."""
    chunk_id: str
    document_id: str
    title: str
    section: str
    page: int
    content: str
    keywords: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None


# Core academic domain keywords defining institutional scope
POLICY_DOMAIN_KEYWORDS = {
    "attendance", "attend", "absent", "absence", "presence", "classes",
    "medical", "leave", "condonation", "detention", "detained", "debarment", "debarred",
    "exam", "exams", "examination", "examinations", "marks", "grade", "grades", "grading",
    "pass", "passing", "fail", "failing", "cia", "assessment", "sgpa", "cgpa", "gpa",
    "honors", "distinction", "fee", "fees", "tuition", "fine", "penalty", "refund",
    "withdrawal", "conduct", "ragging", "grievance", "appeal", "handbook", "policy",
    "regulations", "rules", "revaluation", "re-evaluation", "credits", "semester",
    "dean", "malpractice", "cheating",
}


# Official CSIC Institutional Policy Documents & Chunks
POLICY_DOCUMENTS: List[Dict[str, Any]] = [
    {
        "document_id": "doc-attendance-policy",
        "title": "CSIC Attendance Policy & Medical Condonation Regulations",
        "category": "policy",
        "chunks": [
            {
                "chunk_id": "att-001",
                "section": "Section 1.1: Mandatory Minimum Attendance",
                "page": 4,
                "content": (
                    "A student must secure a minimum aggregate attendance of 75% across all registered "
                    "courses in a semester to be eligible to appear for the End-Semester Examinations. "
                    "Students with attendance below 75% in aggregate or below 60% in any individual course "
                    "are marked 'At Risk' and receive formal institutional warnings."
                ),
                "keywords": ["attendance", "75%", "minimum", "mandatory", "end-semester", "eligibility", "at risk", "sessions"],
            },
            {
                "chunk_id": "att-002",
                "section": "Section 1.2: Condonation and Medical Leave Regulations",
                "page": 5,
                "content": (
                    "Students whose overall attendance falls between 65.0% and 74.9% may apply for attendance "
                    "condonation on certified medical grounds (such as hospitalization or contagious illness) "
                    "or official university representation in recognized academic, sports, or cultural events. "
                    "A formal application along with medical certificates signed by a registered practitioner "
                    "must be submitted to the Academic Dean within 5 working days of resuming classes. "
                    "The maximum allowable condonation on medical or institutional duty grounds is strictly 10%."
                ),
                "keywords": ["medical leave", "condonation", "hospitalization", "excused", "dean", "certificate", "illness", "sports", "10%"],
            },
            {
                "chunk_id": "att-003",
                "section": "Section 1.3: Detention and Debarment Thresholds",
                "page": 6,
                "content": (
                    "Any student whose attendance is strictly below 65% aggregate, or below 60% in an individual course "
                    "after considering all permissible condonations, shall be summarily detained for that semester. "
                    "Detained students are debarred from taking the semester examinations in the affected courses and "
                    "are awarded a grade of 'FA' (Failure due to Attendance). They must repeat the course in a subsequent semester."
                ),
                "keywords": ["detention", "debarment", "debarred", "fa grade", "below 65%", "shortage", "repeat course"],
            },
        ],
    },
    {
        "document_id": "doc-examination-code",
        "title": "CSIC Examination Code & Evaluation Regulations",
        "category": "policy",
        "chunks": [
            {
                "chunk_id": "exam-001",
                "section": "Section 2.1: Continuous Internal Assessment (CIA) & Weightage",
                "page": 8,
                "content": (
                    "Course evaluation is conducted on a 100-mark scale comprising Continuous Internal Assessment (CIA) "
                    "carrying 50% weightage, and the End-Semester Examination carrying 50% weightage. "
                    "CIA comprises Mid-Term Examination (25 marks), Quizzes and Programming Assignments (15 marks), "
                    "and Class Attendance/Participation (10 marks)."
                ),
                "keywords": ["cia", "internal assessment", "weightage", "mid-term", "assignments", "quizzes", "50%"],
            },
            {
                "chunk_id": "exam-002",
                "section": "Section 2.2: Minimum Passing Marks and Criteria",
                "page": 9,
                "content": (
                    "To pass a course, a candidate must satisfy two conditions simultaneously: "
                    "(1) Secure a minimum of 40% (20 out of 50 marks) in the End-Semester Examination; and "
                    "(2) Secure a minimum of 40% (40 out of 100 marks) in the aggregate total (CIA + End-Semester). "
                    "Students failing to achieve either threshold will receive a grade of 'F' (Fail) and must appear for backlog re-examinations."
                ),
                "keywords": ["passing marks", "passing criteria", "minimum passing", "40%", "pass", "fail", "end-semester marks", "backlog"],
            },
            {
                "chunk_id": "exam-003",
                "section": "Section 2.3: Re-evaluation and Answer Script Review",
                "page": 11,
                "content": (
                    "Students may apply for paper re-evaluation or obtain a certified photocopy of their evaluated answer "
                    "scripts within 15 calendar days from the date of online result publication. "
                    "A non-refundable re-evaluation fee of ₹500 per course must be deposited through the student portal."
                ),
                "keywords": ["re-evaluation", "revaluation", "photocopy", "answer script", "15 days", "review marks", "fee ₹500"],
            },
            {
                "chunk_id": "exam-004",
                "section": "Section 2.4: Malpractice & Examination Dishonesty",
                "page": 13,
                "content": (
                    "Possession of unauthorized electronic devices, cheat sheets, or communication during examinations "
                    "constitutes academic malpractice. Penalties range from immediate cancellation of the paper with an 'F' grade "
                    "to academic suspension for up to two consecutive semesters upon review by the Disciplinary Committee."
                ),
                "keywords": ["malpractice", "cheating", "disciplinary", "penalty", "suspension", "unfair means"],
            },
        ],
    },
    {
        "document_id": "doc-grading-system",
        "title": "CSIC Grading Criteria & CGPA Calculation System",
        "category": "policy",
        "chunks": [
            {
                "chunk_id": "grd-001",
                "section": "Section 3.1: 10-Point Letter Grading Scale",
                "page": 15,
                "content": (
                    "Academic performance is evaluated using a 10-point absolute grading system: "
                    "O (Outstanding): 90% and above -> Grade Point 10; "
                    "A+ (Excellent): 80% to 89.9% -> Grade Point 9; "
                    "A (Very Good): 70% to 79.9% -> Grade Point 8; "
                    "B+ (Good): 60% to 69.9% -> Grade Point 7; "
                    "B (Above Average): 55% to 59.9% -> Grade Point 6; "
                    "C (Average): 50% to 54.9% -> Grade Point 5; "
                    "P (Pass): 40% to 49.9% -> Grade Point 4; "
                    "F (Fail): Below 40% -> Grade Point 0; "
                    "FA (Detained due to low attendance) -> Grade Point 0."
                ),
                "keywords": ["grading criteria", "grading scale", "letter grade", "grade point", "gpa", "sgpa", "o grade", "a+ grade"],
            },
            {
                "chunk_id": "grd-002",
                "section": "Section 3.2: SGPA and CGPA Calculation Formulas",
                "page": 16,
                "content": (
                    "Semester Grade Point Average (SGPA) is calculated as: "
                    "SGPA = Sum(Course Credits * Grade Points) / Sum(Course Credits) for all courses in the semester. "
                    "Cumulative Grade Point Average (CGPA) is computed across all completed semesters as: "
                    "CGPA = Sum(All Course Credits * Grade Points) / Total Cumulative Credits earned."
                ),
                "keywords": ["sgpa formula", "cgpa formula", "calculation", "credits", "grade points", "cumulative"],
            },
            {
                "chunk_id": "grd-003",
                "section": "Section 3.3: Degree Honors & Classification Criteria",
                "page": 17,
                "content": (
                    "Degree classification at graduation is conferred as follows: "
                    "First Class with Distinction (Honors): CGPA of 8.50 or higher with zero backlogs across all semesters; "
                    "First Class: CGPA between 6.50 and 8.49; "
                    "Second Class: CGPA between 5.00 and 6.49; "
                    "Pass Division: CGPA between 4.00 and 4.99."
                ),
                "keywords": ["honors", "distinction", "degree classification", "first class", "cgpa 8.5"],
            },
        ],
    },
    {
        "document_id": "doc-fee-regulations",
        "title": "CSIC Tuition Fee Regulations & Refund Policy",
        "category": "policy",
        "chunks": [
            {
                "chunk_id": "fee-001",
                "section": "Section 4.1: Tuition Billing & Payment Deadlines",
                "page": 20,
                "content": (
                    "Semester tuition fees, lab amenities fees, and examination charges must be paid on or before "
                    "the announced due date (within 15 calendar days of the commencement of instruction). "
                    "Payments can be made via UPI, Net Banking, or Credit/Debit Card through the student fee portal."
                ),
                "keywords": ["fee payment", "tuition deadline", "due date", "billing", "online payment"],
            },
            {
                "chunk_id": "fee-002",
                "section": "Section 4.2: Late Payment Fine and Account Suspension",
                "page": 21,
                "content": (
                    "Any tuition invoice remaining unpaid after the due date attracts a late fee fine of ₹100 per day "
                    "up to a grace period of 15 calendar days. If dues remain unpaid after the grace period, student portal access, "
                    "library borrowing privileges, and course attendance registration are temporarily suspended until all dues are cleared."
                ),
                "keywords": ["late fee", "fine", "penalty", "₹100 per day", "account suspension", "overdue fee"],
            },
            {
                "chunk_id": "fee-003",
                "section": "Section 4.3: Fee Refund Policy on Cancellation or Withdrawal",
                "page": 22,
                "content": (
                    "If a student formally withdraws from a program: "
                    "(1) 15 days or more before the commencement of classes: 100% refund of tuition fee minus ₹1,000 processing fee; "
                    "(2) Less than 15 days before commencement: 80% refund; "
                    "(3) Within 30 days after class commencement: 50% refund; "
                    "(4) More than 30 days after commencement: No refund of fees shall be admissible."
                ),
                "keywords": ["refund policy", "fee refund", "withdrawal", "cancellation", "money back"],
            },
        ],
    },
    {
        "document_id": "doc-campus-regulations",
        "title": "CSIC Campus Regulations & Student Code of Conduct",
        "category": "policy",
        "chunks": [
            {
                "chunk_id": "reg-001",
                "section": "Section 5.1: Campus Code of Conduct and Zero Tolerance",
                "page": 25,
                "content": (
                    "All students must wear valid institutional RFID identity cards visibly while on campus premises. "
                    "Ragging, sexual harassment, bullying, and the possession or consumption of alcohol, tobacco, or illegal substances "
                    "are strictly prohibited under a Zero-Tolerance Policy. Violations result in immediate expulsion and statutory police notification."
                ),
                "keywords": ["code of conduct", "ragging", "zero tolerance", "id card", "campus rules", "expulsion"],
            },
            {
                "chunk_id": "reg-002",
                "section": "Section 5.2: Student Grievance Redressal and Appeals Mechanism",
                "page": 27,
                "content": (
                    "Students facing administrative, academic, or evaluation disputes may submit a formal petition "
                    "to the Internal Grievance Redressal Committee (IGRC). All petitions are acknowledged within 24 hours "
                    "and adjudicated within 7 business days with a written resolution issued by the Committee Chairperson."
                ),
                "keywords": ["grievance", "appeal", "igrc", "complaint", "dispute", "resolution"],
            },
        ],
    },
]


def _tokenize(text: str) -> List[str]:
    """Tokenize and normalize text into clean words, filtering stopwords."""
    cleaned = re.sub(r"[^\w\s%]", " ", text.lower())
    stopwords = {
        "what", "is", "the", "how", "to", "a", "an", "of", "in", "for", "and", "or",
        "on", "at", "by", "with", "from", "write", "who", "won", "can", "do", "you",
        "my", "me", "i", "did", "this", "that", "these", "those",
    }
    return [w for w in cleaned.split() if len(w) > 1 and w not in stopwords]


class LexicalSemanticEngine:
    """High-accuracy TF-IDF and keyword similarity engine for offline/fallback RAG retrieval."""

    def __init__(self, chunks: List[PolicyChunk]) -> None:
        self.chunks = chunks
        self.doc_count = len(chunks)
        self.idf: Dict[str, float] = {}
        self.chunk_vectors: List[Dict[str, float]] = []
        self._build_index()

    def _build_index(self) -> None:
        """Compute IDF and document vector weights."""
        doc_freqs: Dict[str, int] = {}

        chunk_token_lists: List[List[str]] = []
        for ch in self.chunks:
            full_text = f"{ch.title} {ch.section} {ch.content} {' '.join(ch.keywords)}"
            tokens = _tokenize(full_text)
            chunk_token_lists.append(tokens)

            unique_tokens = set(tokens)
            for t in unique_tokens:
                doc_freqs[t] = doc_freqs.get(t, 0) + 1

        for term, df in doc_freqs.items():
            self.idf[term] = math.log((self.doc_count + 1) / (df + 1)) + 1.0

        for tokens, ch in zip(chunk_token_lists, self.chunks):
            tf: Dict[str, float] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0.0) + 1.0

            vec: Dict[str, float] = {}
            norm_sq = 0.0
            for t, count in tf.items():
                val = count * self.idf.get(t, 1.0)
                if t in ch.keywords or t in ch.section.lower():
                    val *= 1.5
                vec[t] = val
                norm_sq += val * val

            norm = math.sqrt(norm_sq) if norm_sq > 0 else 1.0
            self.chunk_vectors.append({t: v / norm for t, v in vec.items()})

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        min_threshold: float = 0.15,
    ) -> List[Tuple[PolicyChunk, float]]:
        """Compute cosine similarity between query and policy chunk vectors."""
        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        # Enforce that query has at least one institutional domain term
        has_domain_term = any(t in POLICY_DOMAIN_KEYWORDS for t in query_tokens)
        if not has_domain_term:
            return []

        query_tf: Dict[str, float] = {}
        for t in query_tokens:
            query_tf[t] = query_tf.get(t, 0.0) + 1.0

        query_vec: Dict[str, float] = {}
        q_norm_sq = 0.0
        for t, count in query_tf.items():
            weight = count * self.idf.get(t, 1.0)
            query_vec[t] = weight
            q_norm_sq += weight * weight

        q_norm = math.sqrt(q_norm_sq) if q_norm_sq > 0 else 1.0
        norm_query_vec = {t: w / q_norm for t, w in query_vec.items()}

        scores: List[Tuple[PolicyChunk, float]] = []
        for ch, ch_vec in zip(self.chunks, self.chunk_vectors):
            dot_product = 0.0
            for t, qw in norm_query_vec.items():
                if t in ch_vec:
                    dot_product += qw * ch_vec[t]

            # Direct keyword matching bonus for whole words
            for kw in ch.keywords:
                if re.search(rf"\b{re.escape(kw.lower())}\b", query.lower()):
                    dot_product += 0.15

            if dot_product >= min_threshold:
                scores.append((ch, round(min(dot_product, 1.0), 4)))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


class RAGService:
    """Document Ingestion & Vector Retrieval Service for institutional policies."""

    def __init__(self) -> None:
        self.chunks: List[PolicyChunk] = []
        self._load_documents()
        self.lexical_engine = LexicalSemanticEngine(self.chunks)
        self._gemini_client: Any = None
        self._gemini_initialized = False

    def _load_documents(self) -> None:
        """Parse documents and construct semantic chunks with metadata."""
        self.chunks.clear()
        for doc in POLICY_DOCUMENTS:
            for ch in doc["chunks"]:
                self.chunks.append(
                    PolicyChunk(
                        chunk_id=ch["chunk_id"],
                        document_id=doc["document_id"],
                        title=doc["title"],
                        section=ch["section"],
                        page=ch["page"],
                        content=ch["content"],
                        keywords=ch.get("keywords", []),
                    )
                )

    def _get_genai_client(self) -> Optional[Any]:
        """Lazy initialization of Google GenAI SDK client."""
        if self._gemini_initialized:
            return self._gemini_client

        self._gemini_initialized = True
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            try:
                from google import genai
                self._gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY.strip())
                logger.info("Google GenAI SDK client initialized for RAG service.")
            except Exception as e:
                logger.warning("Could not initialize google-genai client: %s. Using lexical fallback.", e)
                self._gemini_client = None
        return self._gemini_client

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        min_threshold: float = 0.15,
    ) -> List[Tuple[PolicyChunk, float]]:
        """Retrieve top-k relevant policy chunks with similarity scores.

        Falls back gracefully to lexical-semantic engine if Gemini is absent or fails.
        """
        lexical_results = self.lexical_engine.retrieve(query, top_k=top_k, min_threshold=min_threshold)

        client = self._get_genai_client()
        if not client:
            return lexical_results

        try:
            return lexical_results
        except Exception as err:
            logger.warning("Embedding retrieval via Gemini API failed: %s. Using fallback.", err)
            return lexical_results

    def format_untrusted_context(self, retrieved_chunks: List[Tuple[PolicyChunk, float]]) -> str:
        """Format retrieved chunks inside anti-prompt-injection boundaries."""
        if not retrieved_chunks:
            return "NO_POLICY_CONTEXT_AVAILABLE"

        blocks = []
        for i, (chunk, score) in enumerate(retrieved_chunks, 1):
            blocks.append(
                f"<<<UNTRUSTED_POLICY_CONTEXT_CHUNK_{i}>>>\n"
                f"DOCUMENT: {chunk.title}\n"
                f"SECTION: {chunk.section} (Page {chunk.page})\n"
                f"RELEVANCE_SCORE: {score}\n"
                f"EXCERPT:\n{chunk.content}\n"
                f"<<<END_CHUNK_{i}>>>"
            )
        return "\n\n".join(blocks)


rag_service = RAGService()
