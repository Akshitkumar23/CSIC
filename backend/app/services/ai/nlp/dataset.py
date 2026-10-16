"""Curated English and Hinglish Training and Evaluation Dataset for CSIC.

Contains representative utterances, intent labels, and expected extracted entities
for local CPU-based intent classification and evaluation benchmarking.
"""
from typing import Dict, List, Any


# Training dataset (~160 utterances)
TRAIN_DATA: List[Dict[str, Any]] = [
    # --- ATTENDANCE_LOOKUP ---
    {"text": "What is my attendance?", "intent": "attendance_lookup", "entities": {}},
    {"text": "Check my overall attendance percentage", "intent": "attendance_lookup", "entities": {}},
    {"text": "Meri attendance kitni hai?", "intent": "attendance_lookup", "entities": {}},
    {"text": "Meri attendance batao", "intent": "attendance_lookup", "entities": {}},
    {"text": "Mera attendance status kya hai?", "intent": "attendance_lookup", "entities": {}},
    {"text": "What is my attendance in CS401?", "intent": "attendance_lookup", "entities": {"subject": "CS401"}},
    {"text": "How many classes did I attend in CS401?", "intent": "attendance_lookup", "entities": {"subject": "CS401"}},
    {"text": "Show attendance for Cloud Computing", "intent": "attendance_lookup", "entities": {"subject": "CS401"}},
    {"text": "CS402 Machine Learning attendance record", "intent": "attendance_lookup", "entities": {"subject": "CS402"}},
    {"text": "DBMS me meri attendance kitni hai?", "intent": "attendance_lookup", "entities": {"subject": "CS403"}},
    {"text": "Computer Networks attendance status", "intent": "attendance_lookup", "entities": {"subject": "CS404"}},
    {"text": "How many total lectures have I attended so far?", "intent": "attendance_lookup", "entities": {}},
    {"text": "Show my attendance card and breakdown", "intent": "attendance_lookup", "entities": {}},
    {"text": "Did I attend enough classes this semester?", "intent": "attendance_lookup", "entities": {}},
    {"text": "Attendance percentage check", "intent": "attendance_lookup", "entities": {}},
    {"text": "Check attendance in CS403", "intent": "attendance_lookup", "entities": {"subject": "CS403"}},

    # --- ATTENDANCE_ADVICE ---
    {"text": "Attendance kam chal rahi hai, kya karun?", "intent": "attendance_advice", "entities": {}},
    {"text": "My attendance is low what should I do?", "intent": "attendance_advice", "entities": {}},
    {"text": "CS401 mein shortage kyun hai?", "intent": "attendance_advice", "entities": {"subject": "CS401"}},
    {"text": "Why is my attendance below 75%?", "intent": "attendance_advice", "entities": {}},
    {"text": "Attendance shortage advice", "intent": "attendance_advice", "entities": {}},
    {"text": "I got an attendance warning, how to fix it?", "intent": "attendance_advice", "entities": {}},
    {"text": "Shortage aa gayi hai attendance mein", "intent": "attendance_advice", "entities": {}},
    {"text": "What happens if my attendance is low?", "intent": "attendance_advice", "entities": {}},
    {"text": "How to avoid detention due to low attendance?", "intent": "attendance_advice", "entities": {}},
    {"text": "Meri attendance bohot kam hai kya karun", "intent": "attendance_advice", "entities": {}},
    {"text": "At risk attendance warning advice", "intent": "attendance_advice", "entities": {}},
    {"text": "Can I submit medical certificate for attendance shortage?", "intent": "attendance_advice", "entities": {}},
    {"text": "Shortage in CS402 kaise theek karun?", "intent": "attendance_advice", "entities": {"subject": "CS402"}},
    {"text": "Guidance for attendance shortage", "intent": "attendance_advice", "entities": {}},

    # --- ACADEMIC_CALCULATION ---
    {"text": "How many more classes do I need?", "intent": "academic_calculation", "entities": {}},
    {"text": "How many classes do I need to reach 75%?", "intent": "academic_calculation", "entities": {"target": 75}},
    {"text": "Kitni classes attend karni padengi 75% ke liye?", "intent": "academic_calculation", "entities": {"target": 75}},
    {"text": "How many classes can I miss?", "intent": "academic_calculation", "entities": {}},
    {"text": "Can I bunk next class?", "intent": "academic_calculation", "entities": {}},
    {"text": "Can I skip tomorrow's class without falling below 75?", "intent": "academic_calculation", "entities": {"target": 75}},
    {"text": "How many lectures to reach 80% attendance in CS401?", "intent": "academic_calculation", "entities": {"subject": "CS401", "target": 80}},
    {"text": "Safe bunks left for this semester", "intent": "academic_calculation", "entities": {}},
    {"text": "Agar main 2 class miss karun toh attendance kitni hogi?", "intent": "academic_calculation", "entities": {}},
    {"text": "Classes needed to recover 75 percent attendance", "intent": "academic_calculation", "entities": {"target": 75}},
    {"text": "How many more classes required in CS401?", "intent": "academic_calculation", "entities": {"subject": "CS401"}},
    {"text": "Calculate attendance buffer", "intent": "academic_calculation", "entities": {}},
    {"text": "How many classes should I attend consecutively?", "intent": "academic_calculation", "entities": {}},
    {"text": "Bunk calculator", "intent": "academic_calculation", "entities": {}},

    # --- MARKS_EXPLANATION ---
    {"text": "What are my marks?", "intent": "marks_explanation", "entities": {}},
    {"text": "Mere marks kitne aaye hain?", "intent": "marks_explanation", "entities": {}},
    {"text": "Show my exam results", "intent": "marks_explanation", "entities": {}},
    {"text": "What did I score in Midterm?", "intent": "marks_explanation", "entities": {"exam": "Midterm"}},
    {"text": "Midterm marks in CS401", "intent": "marks_explanation", "entities": {"subject": "CS401", "exam": "Midterm"}},
    {"text": "Did I pass Machine Learning exam?", "intent": "marks_explanation", "entities": {"subject": "CS402"}},
    {"text": "Marks explain karo", "intent": "marks_explanation", "entities": {}},
    {"text": "What is my current semester SGPA?", "intent": "marks_explanation", "entities": {}},
    {"text": "Show marks breakdown for CS403", "intent": "marks_explanation", "entities": {"subject": "CS403"}},
    {"text": "Endterm score and grade card", "intent": "marks_explanation", "entities": {"exam": "Endterm"}},
    {"text": "Kitne number mile hain exam me?", "intent": "marks_explanation", "entities": {}},
    {"text": "Am I passing in all subjects?", "intent": "marks_explanation", "entities": {}},
    {"text": "Check marks for Computer Networks", "intent": "marks_explanation", "entities": {"subject": "CS404"}},
    {"text": "Internal assessment marks", "intent": "marks_explanation", "entities": {"exam": "Midterm"}},

    # --- FEE_STATUS ---
    {"text": "What is my fee balance?", "intent": "fee_status", "entities": {}},
    {"text": "How much fees do I owe?", "intent": "fee_status", "entities": {}},
    {"text": "Meri fees kitni baki hai?", "intent": "fee_status", "entities": {}},
    {"text": "Fees pending kitni hai?", "intent": "fee_status", "entities": {}},
    {"text": "Show my fee invoice details", "intent": "fee_status", "entities": {}},
    {"text": "When is the tuition fee due date?", "intent": "fee_status", "entities": {}},
    {"text": "Have I paid semester fees?", "intent": "fee_status", "entities": {}},
    {"text": "Fee receipt and payment history", "intent": "fee_status", "entities": {}},
    {"text": "Late fee fine kitna lagega?", "intent": "fee_status", "entities": {}},
    {"text": "Do I have any outstanding dues?", "intent": "fee_status", "entities": {}},
    {"text": "Tuition fees paid status", "intent": "fee_status", "entities": {}},
    {"text": "Payment due date for tuition invoice", "intent": "fee_status", "entities": {}},
    {"text": "Fee summary and balance", "intent": "fee_status", "entities": {}},

    # --- TIMETABLE ---
    {"text": "What classes do I have today?", "intent": "timetable", "entities": {"day": "today"}},
    {"text": "Aaj kaunsi class hai?", "intent": "timetable", "entities": {"day": "today"}},
    {"text": "Aaj ka timetable kya hai?", "intent": "timetable", "entities": {"day": "today"}},
    {"text": "Show my schedule for Monday", "intent": "timetable", "entities": {"day": "monday"}},
    {"text": "Kal ka schedule batao", "intent": "timetable", "entities": {"day": "tomorrow"}},
    {"text": "When is my next class?", "intent": "timetable", "entities": {}},
    {"text": "Tuesday schedule and classroom", "intent": "timetable", "entities": {"day": "tuesday"}},
    {"text": "What time is CS401 lecture?", "intent": "timetable", "entities": {"subject": "CS401"}},
    {"text": "Show weekly timetable", "intent": "timetable", "entities": {}},
    {"text": "Friday ko kaunsa lecture hai?", "intent": "timetable", "entities": {"day": "friday"}},
    {"text": "Class timings for Cloud Computing", "intent": "timetable", "entities": {"subject": "CS401"}},
    {"text": "What is the lecture venue for Machine Learning?", "intent": "timetable", "entities": {"subject": "CS402"}},

    # --- NOTICES ---
    {"text": "What are the latest notices?", "intent": "notices", "entities": {}},
    {"text": "Show recent circulars and announcements", "intent": "notices", "entities": {}},
    {"text": "Koi naya notice aaya kya?", "intent": "notices", "entities": {}},
    {"text": "Any new updates on exam schedule?", "intent": "notices", "entities": {}},
    {"text": "Latest college announcements", "intent": "notices", "entities": {}},
    {"text": "Is tomorrow a holiday?", "intent": "notices", "entities": {}},
    {"text": "Holiday notice check", "intent": "notices", "entities": {}},
    {"text": "Circular for semester registration", "intent": "notices", "entities": {}},
    {"text": "Notice board updates", "intent": "notices", "entities": {}},
    {"text": "Naye circulars dikhao", "intent": "notices", "entities": {}},

    # --- POLICY_LOOKUP ---
    {"text": "What is the attendance policy?", "intent": "policy_lookup", "entities": {}},
    {"text": "What are the rules for medical leave?", "intent": "policy_lookup", "entities": {}},
    {"text": "How much condonation is allowed for illness?", "intent": "policy_lookup", "entities": {}},
    {"text": "What is the minimum passing marks in exams?", "intent": "policy_lookup", "entities": {}},
    {"text": "Detention criteria and debarment rules", "intent": "policy_lookup", "entities": {}},
    {"text": "Explain the grading criteria and SGPA scale", "intent": "policy_lookup", "entities": {}},
    {"text": "Fee refund policy on cancellation", "intent": "policy_lookup", "entities": {}},
    {"text": "Code of conduct and campus rules", "intent": "policy_lookup", "entities": {}},
    {"text": "Ragging policy and penalties", "intent": "policy_lookup", "entities": {}},
    {"text": "Revaluation guidelines and passing rules", "intent": "policy_lookup", "entities": {}},
    {"text": "Medical certificate deadline rule", "intent": "policy_lookup", "entities": {}},

    # --- FOLLOW_UP ---
    {"text": "What about CS401?", "intent": "follow_up", "entities": {"subject": "CS401"}},
    {"text": "And in Machine Learning?", "intent": "follow_up", "entities": {"subject": "CS402"}},
    {"text": "What about that subject?", "intent": "follow_up", "entities": {}},
    {"text": "How many more in this one?", "intent": "follow_up", "entities": {}},
    {"text": "Usme kitni hai?", "intent": "follow_up", "entities": {}},
    {"text": "And marks?", "intent": "follow_up", "entities": {}},
    {"text": "How about CS403?", "intent": "follow_up", "entities": {"subject": "CS403"}},
    {"text": "Us subject me kitne marks hain?", "intent": "follow_up", "entities": {}},
    {"text": "What about the other course?", "intent": "follow_up", "entities": {}},

    # --- GREETING ---
    {"text": "Hello", "intent": "greeting", "entities": {}},
    {"text": "Hi", "intent": "greeting", "entities": {}},
    {"text": "Hey CSIC", "intent": "greeting", "entities": {}},
    {"text": "Namaste", "intent": "greeting", "entities": {}},
    {"text": "Good morning", "intent": "greeting", "entities": {}},
    {"text": "Who are you?", "intent": "greeting", "entities": {}},
    {"text": "Help me", "intent": "greeting", "entities": {}},
    {"text": "What can you do?", "intent": "greeting", "entities": {}},

    # --- OUT_OF_DOMAIN ---
    {"text": "What is the capital of France?", "intent": "out_of_domain", "entities": {}},
    {"text": "Write a python script to sort an array", "intent": "out_of_domain", "entities": {}},
    {"text": "Who won the cricket match yesterday?", "intent": "out_of_domain", "entities": {}},
    {"text": "Tell me a joke", "intent": "out_of_domain", "entities": {}},
    {"text": "Explain quantum computing theory", "intent": "out_of_domain", "entities": {}},
    {"text": "What is the weather outside?", "intent": "out_of_domain", "entities": {}},
]


# Evaluation Test Dataset (~50 utterances) for benchmarking Precision, Recall & F1
TEST_DATA: List[Dict[str, Any]] = [
    # Attendance Lookup
    {"text": "Show my attendance percentage in CS401", "intent": "attendance_lookup", "entities": {"subject": "CS401"}},
    {"text": "Overall attendance status bataiye", "intent": "attendance_lookup", "entities": {}},
    {"text": "How many lectures have I attended?", "intent": "attendance_lookup", "entities": {}},
    {"text": "Cloud Computing attendance check", "intent": "attendance_lookup", "entities": {"subject": "CS401"}},
    {"text": "Meri CS402 me attendance kitni hai?", "intent": "attendance_lookup", "entities": {"subject": "CS402"}},

    # Attendance Advice
    {"text": "Attendance kam hai, kya karun?", "intent": "attendance_advice", "entities": {}},
    {"text": "Why do I have an attendance warning?", "intent": "attendance_advice", "entities": {}},
    {"text": "I am having shortage in CS401, what should I do?", "intent": "attendance_advice", "entities": {"subject": "CS401"}},
    {"text": "Shortage kaise theek karein?", "intent": "attendance_advice", "entities": {}},
    {"text": "How to avoid exam debarment due to attendance?", "intent": "attendance_advice", "entities": {}},

    # Academic Calculation
    {"text": "How many more classes do I need to reach 75%?", "intent": "academic_calculation", "entities": {"target": 75}},
    {"text": "Kitni classes aur lagani padengi?", "intent": "academic_calculation", "entities": {}},
    {"text": "Can I miss tomorrow's lecture?", "intent": "academic_calculation", "entities": {}},
    {"text": "How many bunks can I take safely?", "intent": "academic_calculation", "entities": {}},
    {"text": "How many consecutive classes needed in CS401?", "intent": "academic_calculation", "entities": {"subject": "CS401"}},

    # Marks Explanation
    {"text": "Check my Midterm marks in CS402", "intent": "marks_explanation", "entities": {"subject": "CS402", "exam": "Midterm"}},
    {"text": "Exam result explain karo", "intent": "marks_explanation", "entities": {}},
    {"text": "Did I pass Computer Networks exam?", "intent": "marks_explanation", "entities": {"subject": "CS404"}},
    {"text": "What is my GPA this semester?", "intent": "marks_explanation", "entities": {}},
    {"text": "Mere Endterm marks kitne the?", "intent": "marks_explanation", "entities": {"exam": "Endterm"}},

    # Fee Status
    {"text": "How much fee is pending?", "intent": "fee_status", "entities": {}},
    {"text": "Meri fees baki hai kya?", "intent": "fee_status", "entities": {}},
    {"text": "What is the tuition invoice balance?", "intent": "fee_status", "entities": {}},
    {"text": "Has my tuition payment been confirmed?", "intent": "fee_status", "entities": {}},
    {"text": "Late fee kitna lagega agar payment miss ho jaye?", "intent": "fee_status", "entities": {}},

    # Timetable
    {"text": "Aaj kaun kaun si classes hain?", "intent": "timetable", "entities": {"day": "today"}},
    {"text": "What is my timetable for Wednesday?", "intent": "timetable", "entities": {"day": "wednesday"}},
    {"text": "When is the next Database lecture?", "intent": "timetable", "entities": {"subject": "CS403"}},
    {"text": "Tomorrow schedule and room numbers", "intent": "timetable", "entities": {"day": "tomorrow"}},
    {"text": "Monday ko first lecture kab hai?", "intent": "timetable", "entities": {"day": "monday"}},

    # Notices
    {"text": "Latest college notices batao", "intent": "notices", "entities": {}},
    {"text": "Are there any circulars about upcoming exams?", "intent": "notices", "entities": {}},
    {"text": "Koi circular aaya hai kya?", "intent": "notices", "entities": {}},
    {"text": "Is next Monday an official holiday?", "intent": "notices", "entities": {"day": "monday"}},

    # Policy Lookup
    {"text": "What is the attendance condonation criteria for medical leave?", "intent": "policy_lookup", "entities": {}},
    {"text": "How are passing marks calculated in CSIC?", "intent": "policy_lookup", "entities": {}},
    {"text": "What is the policy for fee refund on course withdrawal?", "intent": "policy_lookup", "entities": {}},
    {"text": "Detention rule aggregate percentage requirement", "intent": "policy_lookup", "entities": {}},

    # Follow-up
    {"text": "What about CS401?", "intent": "follow_up", "entities": {"subject": "CS401"}},
    {"text": "And in Machine Learning?", "intent": "follow_up", "entities": {"subject": "CS402"}},
    {"text": "How many classes to recover in that subject?", "intent": "follow_up", "entities": {}},
    {"text": "Usme kitne marks aaye?", "intent": "follow_up", "entities": {}},

    # Greeting
    {"text": "Namaste assistant", "intent": "greeting", "entities": {}},
    {"text": "Hey CSIC what can you help with?", "intent": "greeting", "entities": {}},
    {"text": "Good morning assistant", "intent": "greeting", "entities": {}},

    # Out of Domain
    {"text": "What is the capital of Spain?", "intent": "out_of_domain", "entities": {}},
    {"text": "How do I make pasta at home?", "intent": "out_of_domain", "entities": {}},
    {"text": "Explain black holes in outer space", "intent": "out_of_domain", "entities": {}},
]
