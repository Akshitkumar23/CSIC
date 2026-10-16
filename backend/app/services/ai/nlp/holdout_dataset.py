"""Independent Final Holdout Evaluation Dataset for CSIC.

This dataset contains 55 genuinely novel, balanced English and Hinglish utterances
across all 11 intent classes (5 per class).

CRITICAL ASSURANCE:
This dataset was constructed strictly for final validation after all model tuning
and preprocessing decisions were completed. It was NEVER used for hyperparameter
tuning, error inspection, or training.
"""
from typing import Any, Dict, List

HOLDOUT_DATA: List[Dict[str, Any]] = [
    # 1. ATTENDANCE_LOOKUP (5)
    {"text": "How many sessions have I been present for in CS403?", "intent": "attendance_lookup", "entities": {"subject": "CS403"}},
    {"text": "Attendance percentage review", "intent": "attendance_lookup", "entities": {}},
    {"text": "Meri kul milakar kitni hazri hai?", "intent": "attendance_lookup", "entities": {}},
    {"text": "Kya meri presence 75 se upar hai?", "intent": "attendance_lookup", "entities": {}},
    {"text": "Display my lecture logs for Database Systems", "intent": "attendance_lookup", "entities": {"subject": "CS403"}},

    # 2. ATTENDANCE_ADVICE (5)
    {"text": "I received an alert about attendance shortage, what are the steps to resolve it?", "intent": "attendance_advice", "entities": {}},
    {"text": "Can the dean excuse my absences due to dengue fever?", "intent": "attendance_advice", "entities": {}},
    {"text": "Attendance theek karne ke liye kya process hai?", "intent": "attendance_advice", "entities": {}},
    {"text": "How can I avoid getting debarred from writing exams?", "intent": "attendance_advice", "entities": {}},
    {"text": "Shortage alert aaya hai mujhe, Dean ko letter kaise likhun?", "intent": "attendance_advice", "entities": {}},

    # 3. ACADEMIC_CALCULATION (5)
    {"text": "If I attend all classes for the next two weeks, will my percentage improve?", "intent": "academic_calculation", "entities": {}},
    {"text": "How many lectures am I permitted to skip safely?", "intent": "academic_calculation", "entities": {}},
    {"text": "Mujhe 75 percent touch karne ke liye kitne ghante baithna padega?", "intent": "academic_calculation", "entities": {"target": 75}},
    {"text": "Can I take a leave on Friday without violating attendance minimums?", "intent": "academic_calculation", "entities": {}},
    {"text": "Number of lectures required to get out of the red zone in CS401", "intent": "academic_calculation", "entities": {"subject": "CS401"}},

    # 4. MARKS_EXPLANATION (5)
    {"text": "Show my evaluation breakdown for internal assessments", "intent": "marks_explanation", "entities": {"exam": "Midterm"}},
    {"text": "Did I clear the minimum qualifying cutoff in Computer Networks?", "intent": "marks_explanation", "entities": {"subject": "CS404"}},
    {"text": "Mere semester ke paper me kitne score bane?", "intent": "marks_explanation", "entities": {}},
    {"text": "What was the class average mark in Machine Learning?", "intent": "marks_explanation", "entities": {"subject": "CS402"}},
    {"text": "Is CIA score factored into the semester grade?", "intent": "marks_explanation", "entities": {}},

    # 5. FEE_STATUS (5)
    {"text": "Is there an outstanding invoice on my student ledger?", "intent": "fee_status", "entities": {}},
    {"text": "Show the deadline for second installment tuition payment", "intent": "fee_status", "entities": {}},
    {"text": "Meri college ki fees bachi hui hai ya clear ho gayi?", "intent": "fee_status", "entities": {}},
    {"text": "Has the accounts department acknowledged my net banking transaction?", "intent": "fee_status", "entities": {}},
    {"text": "What is the penalty if I pay fees next week?", "intent": "fee_status", "entities": {}},

    # 6. TIMETABLE (5)
    {"text": "Where is the classroom for Thursday morning lecture?", "intent": "timetable", "entities": {"day": "thursday"}},
    {"text": "Which teacher has the 11 AM period tomorrow?", "intent": "timetable", "entities": {"day": "tomorrow"}},
    {"text": "Kal subah pehla lecture kitne baje shuru hoga?", "intent": "timetable", "entities": {"day": "tomorrow"}},
    {"text": "Do we have any laboratory practicals scheduled on Tuesday?", "intent": "timetable", "entities": {"day": "tuesday"}},
    {"text": "Give me the time slots for Machine Learning this week", "intent": "timetable", "entities": {"subject": "CS402"}},

    # 7. NOTICES (5)
    {"text": "Has the university declared any schedule for mid-term tests?", "intent": "notices", "entities": {}},
    {"text": "Are there any administrative circulars issued today?", "intent": "notices", "entities": {}},
    {"text": "Diwali ki chutti ka koi official circular aaya?", "intent": "notices", "entities": {}},
    {"text": "Check if there is a postponement circular for Friday", "intent": "notices", "entities": {}},
    {"text": "Important notices from the registrar office", "intent": "notices", "entities": {}},

    # 8. POLICY_LOOKUP (5)
    {"text": "What is the official procedure for seeking medical condonation?", "intent": "policy_lookup", "entities": {}},
    {"text": "How is SGPA converted to percentage under college ordinance?", "intent": "policy_lookup", "entities": {}},
    {"text": "What are the rules regarding campus dress code and RFID cards?", "intent": "policy_lookup", "entities": {}},
    {"text": "College regulations on course cancellation and tuition refund", "intent": "policy_lookup", "entities": {}},
    {"text": "Minimum aggregate attendance mandated by the academic council", "intent": "policy_lookup", "entities": {}},

    # 9. FOLLOW_UP (5)
    {"text": "What about that one?", "intent": "follow_up", "entities": {}},
    {"text": "And in the second course?", "intent": "follow_up", "entities": {}},
    {"text": "Usme kitna score hai?", "intent": "follow_up", "entities": {}},
    {"text": "What about the lecture timing for this subject?", "intent": "follow_up", "entities": {}},
    {"text": "Is there any shortage in it as well?", "intent": "follow_up", "entities": {}},

    # 10. GREETING (5)
    {"text": "Hey there CSIC", "intent": "greeting", "entities": {}},
    {"text": "Greetings assistant", "intent": "greeting", "entities": {}},
    {"text": "Can you guide me on academic matters?", "intent": "greeting", "entities": {}},
    {"text": "Pranam chatbot", "intent": "greeting", "entities": {}},
    {"text": "Good evening", "intent": "greeting", "entities": {}},

    # 11. OUT_OF_DOMAIN (5)
    {"text": "Who directed the movie Interstellar?", "intent": "out_of_domain", "entities": {}},
    {"text": "Can you teach me how to drive a car?", "intent": "out_of_domain", "entities": {}},
    {"text": "What is the exchange rate between US Dollar and Indian Rupee?", "intent": "out_of_domain", "entities": {}},
    {"text": "Write a poem celebrating spring season", "intent": "out_of_domain", "entities": {}},
    {"text": "What is the recipe for butter chicken?", "intent": "out_of_domain", "entities": {}},
]
