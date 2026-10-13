"""Rich synthetic dataset strictly mirroring the 3NF PostgreSQL schema.

Includes profiles, departments, programs, courses, subjects, enrollments,
class sessions, attendance records, examinations, marks, fee invoices,
payments, timetable entries, and campus notices.
"""
from datetime import date, datetime, timezone
from typing import Any, Dict, List

# Passwords hashed with bcrypt:
# Student@123 -> $2b$12$NqL9s1x4eGq64K9Uo23qOedXj0hQ4LgJq3lV6XQe6tqN4Y6B9z0zC (or hashed at runtime)
# Faculty@123
# Admin@123

PROFILES: List[Dict[str, Any]] = [
    {
        "id": "stu-001",
        "email": "aarav.sharma@csic.edu",
        "password": "Student@123",
        "role": "student",
        "full_name": "Aarav Sharma",
        "phone": "+91 98765 43210",
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Aarav",
        "is_active": True,
        "created_at": datetime(2024, 8, 1, 10, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2024, 8, 1, 10, 0, tzinfo=timezone.utc),
    },
    {
        "id": "stu-002",
        "email": "priya.patel@csic.edu",
        "password": "Student@123",
        "role": "student",
        "full_name": "Priya Patel",
        "phone": "+91 98765 43211",
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Priya",
        "is_active": True,
        "created_at": datetime(2024, 8, 1, 10, 5, tzinfo=timezone.utc),
        "updated_at": datetime(2024, 8, 1, 10, 5, tzinfo=timezone.utc),
    },
    {
        "id": "stu-003",
        "email": "rohan.gupta@csic.edu",
        "password": "Student@123",
        "role": "student",
        "full_name": "Rohan Gupta",
        "phone": "+91 98765 43212",
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Rohan",
        "is_active": True,
        "created_at": datetime(2024, 8, 1, 10, 10, tzinfo=timezone.utc),
        "updated_at": datetime(2024, 8, 1, 10, 10, tzinfo=timezone.utc),
    },
    {
        "id": "fac-001",
        "email": "rajesh.kumar@csic.edu",
        "password": "Faculty@123",
        "role": "faculty",
        "full_name": "Dr. Rajesh Kumar",
        "phone": "+91 98765 11223",
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Rajesh",
        "is_active": True,
        "created_at": datetime(2023, 6, 1, 9, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2023, 6, 1, 9, 0, tzinfo=timezone.utc),
    },
    {
        "id": "fac-002",
        "email": "anita.deshmukh@csic.edu",
        "password": "Faculty@123",
        "role": "faculty",
        "full_name": "Prof. Anita Deshmukh",
        "phone": "+91 98765 11224",
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Anita",
        "is_active": True,
        "created_at": datetime(2023, 6, 1, 9, 15, tzinfo=timezone.utc),
        "updated_at": datetime(2023, 6, 1, 9, 15, tzinfo=timezone.utc),
    },
    {
        "id": "admin-001",
        "email": "admin@csic.edu",
        "password": "Admin@123",
        "role": "admin",
        "full_name": "Dean & System Admin",
        "phone": "+91 98765 00001",
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Admin",
        "is_active": True,
        "created_at": datetime(2023, 1, 1, 8, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2023, 1, 1, 8, 0, tzinfo=timezone.utc),
    },
]

DEPARTMENTS: List[Dict[str, Any]] = [
    {"id": "dept-01", "code": "CSE", "name": "Computer Science & Engineering"},
    {"id": "dept-02", "code": "ECE", "name": "Electronics & Communication Engineering"},
]

PROGRAMS: List[Dict[str, Any]] = [
    {
        "id": "prog-01",
        "department_id": "dept-01",
        "code": "BTECH_CSE",
        "name": "B.Tech Computer Science & Engineering",
        "duration_years": 4,
    },
]

ACADEMIC_YEARS: List[Dict[str, Any]] = [
    {"id": "ay-2025", "name": "2025-2026", "start_date": date(2025, 7, 1), "end_date": date(2026, 6, 30), "is_current": True},
]

SEMESTERS: List[Dict[str, Any]] = [
    {"id": "sem-06", "academic_year_id": "ay-2025", "semester_number": 6, "term": "even", "start_date": date(2026, 1, 5), "end_date": date(2026, 5, 20)},
]

COURSES: List[Dict[str, Any]] = [
    {"id": "crs-01", "program_id": "prog-01", "semester_id": "sem-06", "section": "A"},
]

SUBJECTS: List[Dict[str, Any]] = [
    {"id": "sub-01", "code": "CS401", "name": "Cloud Computing & Distributed Systems", "credits": 4.0, "department_id": "dept-01"},
    {"id": "sub-02", "code": "CS402", "name": "Advanced Database Engineering", "credits": 4.0, "department_id": "dept-01"},
    {"id": "sub-03", "code": "CS403", "name": "Machine Learning & AI", "credits": 4.0, "department_id": "dept-01"},
    {"id": "sub-04", "code": "CS404", "name": "Computer Networks & Security", "credits": 3.0, "department_id": "dept-01"},
]

FACULTY_ASSIGNMENTS: List[Dict[str, Any]] = [
    {"id": "fa-01", "faculty_id": "fac-01", "subject_id": "sub-01", "course_id": "crs-01"},
    {"id": "fa-02", "faculty_id": "fac-01", "subject_id": "sub-02", "course_id": "crs-01"},
    {"id": "fa-03", "faculty_id": "fac-02", "subject_id": "sub-03", "course_id": "crs-01"},
    {"id": "fa-04", "faculty_id": "fac-02", "subject_id": "sub-04", "course_id": "crs-01"},
]

ENROLLMENTS: List[Dict[str, Any]] = [
    {
        "id": "enr-001",
        "student_id": "stu-001",
        "course_id": "crs-01",
        "roll_number": "CS2023001",
        "enrollment_date": date(2023, 8, 1),
        "status": "active",
        "program_code": "BTECH_CSE",
        "program_name": "B.Tech Computer Science & Engineering",
        "semester_number": 6,
        "section": "A",
    },
    {
        "id": "enr-002",
        "student_id": "stu-002",
        "course_id": "crs-01",
        "roll_number": "CS2023002",
        "enrollment_date": date(2023, 8, 1),
        "status": "active",
        "program_code": "BTECH_CSE",
        "program_name": "B.Tech Computer Science & Engineering",
        "semester_number": 6,
        "section": "A",
    },
    {
        "id": "enr-003",
        "student_id": "stu-003",
        "course_id": "crs-01",
        "roll_number": "CS2023003",
        "enrollment_date": date(2023, 8, 1),
        "status": "active",
        "program_code": "BTECH_CSE",
        "program_name": "B.Tech Computer Science & Engineering",
        "semester_number": 6,
        "section": "A",
    },
]

# 24 Class Sessions conducted
CLASS_SESSIONS: List[Dict[str, Any]] = [
    {"id": f"sess-{i:02d}", "faculty_assignment_id": fa_id, "session_date": date(2026, 2, 1 + (i % 25)), "start_time": "09:00:00", "end_time": "10:00:00", "topic": f"Lecture Session {i}: Architecture Principles", "status": "conducted"}
    for i, fa_id in enumerate(["fa-01", "fa-02", "fa-03", "fa-04"] * 6, start=1)
]

# Attendance records:
# Aarav (enr-001): 21 present, 2 excused, 1 absent -> (21+2)/24 = 95.8% (Good)
# Priya (enr-002): 20 present, 1 excused, 3 absent -> (20+1)/24 = 87.5% (Good)
# Rohan (enr-003): 14 present, 1 excused, 9 absent -> (14+1)/24 = 62.5% (Risk / Low Attendance Warning!)
ATTENDANCE_RECORDS: List[Dict[str, Any]] = []

for idx, sess in enumerate(CLASS_SESSIONS):
    # Aarav
    st1 = "present" if idx != 23 else "absent"
    if idx == 10:
        st1 = "excused"
    ATTENDANCE_RECORDS.append({
        "id": f"att-001-{sess['id']}",
        "session_id": sess["id"],
        "enrollment_id": "enr-001",
        "status": st1,
        "remarks": "On time" if st1 == "present" else ("Medical" if st1 == "excused" else "Uninformed"),
        "marked_at": datetime(2026, 2, 1 + (idx % 25), 10, 5, tzinfo=timezone.utc),
    })
    
    # Priya
    st2 = "absent" if idx in (5, 12, 19) else "present"
    if idx == 7:
        st2 = "excused"
    ATTENDANCE_RECORDS.append({
        "id": f"att-002-{sess['id']}",
        "session_id": sess["id"],
        "enrollment_id": "enr-002",
        "status": st2,
        "remarks": "Regular" if st2 == "present" else "Absent",
        "marked_at": datetime(2026, 2, 1 + (idx % 25), 10, 5, tzinfo=timezone.utc),
    })
    
    # Rohan (Low attendance student)
    st3 = "absent" if idx in (1, 3, 6, 8, 11, 14, 16, 20, 22) else "present"
    if idx == 4:
        st3 = "excused"
    ATTENDANCE_RECORDS.append({
        "id": f"att-003-{sess['id']}",
        "session_id": sess["id"],
        "enrollment_id": "enr-003",
        "status": st3,
        "remarks": "Needs improvement" if st3 == "absent" else "Attended",
        "marked_at": datetime(2026, 2, 1 + (idx % 25), 10, 5, tzinfo=timezone.utc),
    })

EXAMINATIONS: List[Dict[str, Any]] = [
    {"id": "exam-mid-01", "course_id": "crs-01", "subject_id": "sub-01", "name": "Mid-Term Examination 2026", "exam_date": date(2026, 3, 10), "max_marks": 50.0, "weightage_percentage": 30.0},
    {"id": "exam-mid-02", "course_id": "crs-01", "subject_id": "sub-02", "name": "Mid-Term Examination 2026", "exam_date": date(2026, 3, 12), "max_marks": 50.0, "weightage_percentage": 30.0},
    {"id": "exam-mid-03", "course_id": "crs-01", "subject_id": "sub-03", "name": "Mid-Term Examination 2026", "exam_date": date(2026, 3, 15), "max_marks": 50.0, "weightage_percentage": 30.0},
    {"id": "exam-mid-04", "course_id": "crs-01", "subject_id": "sub-04", "name": "Mid-Term Examination 2026", "exam_date": date(2026, 3, 18), "max_marks": 50.0, "weightage_percentage": 30.0},
]

MARKS: List[Dict[str, Any]] = [
    # Aarav
    {"id": "mark-01", "examination_id": "exam-mid-01", "enrollment_id": "enr-001", "marks_obtained": 46.5, "is_absent": False, "grade": "A+", "entered_by": "fac-01"},
    {"id": "mark-02", "examination_id": "exam-mid-02", "enrollment_id": "enr-001", "marks_obtained": 44.0, "is_absent": False, "grade": "A", "entered_by": "fac-01"},
    {"id": "mark-03", "examination_id": "exam-mid-03", "enrollment_id": "enr-001", "marks_obtained": 48.0, "is_absent": False, "grade": "O", "entered_by": "fac-02"},
    {"id": "mark-04", "examination_id": "exam-mid-04", "enrollment_id": "enr-001", "marks_obtained": 42.0, "is_absent": False, "grade": "A", "entered_by": "fac-02"},
    # Priya
    {"id": "mark-05", "examination_id": "exam-mid-01", "enrollment_id": "enr-002", "marks_obtained": 41.0, "is_absent": False, "grade": "A", "entered_by": "fac-01"},
    {"id": "mark-06", "examination_id": "exam-mid-02", "enrollment_id": "enr-002", "marks_obtained": 40.0, "is_absent": False, "grade": "B+", "entered_by": "fac-01"},
    {"id": "mark-07", "examination_id": "exam-mid-03", "enrollment_id": "enr-002", "marks_obtained": 45.0, "is_absent": False, "grade": "A+", "entered_by": "fac-02"},
    {"id": "mark-08", "examination_id": "exam-mid-04", "enrollment_id": "enr-002", "marks_obtained": 38.5, "is_absent": False, "grade": "B+", "entered_by": "fac-02"},
    # Rohan
    {"id": "mark-09", "examination_id": "exam-mid-01", "enrollment_id": "enr-003", "marks_obtained": 26.0, "is_absent": False, "grade": "C", "entered_by": "fac-01"},
    {"id": "mark-10", "examination_id": "exam-mid-02", "enrollment_id": "enr-003", "marks_obtained": 24.5, "is_absent": False, "grade": "C", "entered_by": "fac-01"},
    {"id": "mark-11", "examination_id": "exam-mid-03", "enrollment_id": "enr-003", "marks_obtained": 29.0, "is_absent": False, "grade": "B", "entered_by": "fac-02"},
    {"id": "mark-12", "examination_id": "exam-mid-04", "enrollment_id": "enr-003", "marks_obtained": 21.0, "is_absent": False, "grade": "P", "entered_by": "fac-02"},
]

FEE_INVOICES: List[Dict[str, Any]] = [
    {
        "id": "inv-001",
        "invoice_number": "INV-2026-001",
        "enrollment_id": "enr-001",
        "title": "Semester 6 Academic Tuition Fee",
        "amount": 65000.0,
        "due_date": date(2026, 1, 30),
        "status": "paid",
        "created_at": datetime(2026, 1, 5, 9, 0, tzinfo=timezone.utc),
    },
    {
        "id": "inv-002",
        "invoice_number": "INV-2026-002",
        "enrollment_id": "enr-001",
        "title": "Cloud Computing Specialization Lab Fee",
        "amount": 12500.0,
        "due_date": date(2026, 2, 28),
        "status": "paid",
        "created_at": datetime(2026, 1, 15, 9, 0, tzinfo=timezone.utc),
    },
    {
        "id": "inv-003",
        "invoice_number": "INV-2026-003",
        "enrollment_id": "enr-002",
        "title": "Semester 6 Academic Tuition Fee",
        "amount": 65000.0,
        "due_date": date(2026, 1, 30),
        "status": "partially_paid",
        "created_at": datetime(2026, 1, 5, 9, 0, tzinfo=timezone.utc),
    },
    {
        "id": "inv-004",
        "invoice_number": "INV-2026-004",
        "enrollment_id": "enr-003",
        "title": "Semester 6 Academic Tuition Fee",
        "amount": 65000.0,
        "due_date": date(2026, 1, 30),
        "status": "unpaid",
        "created_at": datetime(2026, 1, 5, 9, 0, tzinfo=timezone.utc),
    },
]

FEE_PAYMENTS: List[Dict[str, Any]] = [
    {
        "id": "pay-001",
        "invoice_id": "inv-001",
        "transaction_reference": "TXN_UPI_982341279",
        "amount_paid": 65000.0,
        "payment_date": datetime(2026, 1, 20, 14, 30, tzinfo=timezone.utc),
        "payment_method": "upi",
        "status": "success",
    },
    {
        "id": "pay-002",
        "invoice_id": "inv-002",
        "transaction_reference": "TXN_NB_443219081",
        "amount_paid": 12500.0,
        "payment_date": datetime(2026, 2, 10, 11, 15, tzinfo=timezone.utc),
        "payment_method": "net_banking",
        "status": "success",
    },
    {
        "id": "pay-003",
        "invoice_id": "inv-003",
        "transaction_reference": "TXN_CARD_11993240",
        "amount_paid": 35000.0,
        "payment_date": datetime(2026, 1, 25, 16, 45, tzinfo=timezone.utc),
        "payment_method": "card",
        "status": "success",
    },
]

TIMETABLE_ENTRIES: List[Dict[str, Any]] = [
    # Monday
    {"id": "tt-01", "faculty_assignment_id": "fa-01", "day_of_week": "Monday", "start_time": "09:00:00", "end_time": "10:00:00", "room_number": "LH-301"},
    {"id": "tt-02", "faculty_assignment_id": "fa-02", "day_of_week": "Monday", "start_time": "10:15:00", "end_time": "11:15:00", "room_number": "Lab-204"},
    {"id": "tt-03", "faculty_assignment_id": "fa-03", "day_of_week": "Monday", "start_time": "11:30:00", "end_time": "12:30:00", "room_number": "LH-302"},
    # Tuesday
    {"id": "tt-04", "faculty_assignment_id": "fa-04", "day_of_week": "Tuesday", "start_time": "09:00:00", "end_time": "10:00:00", "room_number": "LH-301"},
    {"id": "tt-05", "faculty_assignment_id": "fa-01", "day_of_week": "Tuesday", "start_time": "10:15:00", "end_time": "11:15:00", "room_number": "LH-301"},
    # Wednesday
    {"id": "tt-06", "faculty_assignment_id": "fa-02", "day_of_week": "Wednesday", "start_time": "09:00:00", "end_time": "10:00:00", "room_number": "Lab-204"},
    {"id": "tt-07", "faculty_assignment_id": "fa-03", "day_of_week": "Wednesday", "start_time": "10:15:00", "end_time": "11:15:00", "room_number": "LH-302"},
    # Thursday
    {"id": "tt-08", "faculty_assignment_id": "fa-04", "day_of_week": "Thursday", "start_time": "09:00:00", "end_time": "10:00:00", "room_number": "LH-301"},
    {"id": "tt-09", "faculty_assignment_id": "fa-01", "day_of_week": "Thursday", "start_time": "11:30:00", "end_time": "12:30:00", "room_number": "LH-301"},
    # Friday
    {"id": "tt-10", "faculty_assignment_id": "fa-03", "day_of_week": "Friday", "start_time": "09:00:00", "end_time": "10:00:00", "room_number": "LH-302"},
    {"id": "tt-11", "faculty_assignment_id": "fa-02", "day_of_week": "Friday", "start_time": "10:15:00", "end_time": "11:15:00", "room_number": "Lab-204"},
]

NOTICES: List[Dict[str, Any]] = [
    {
        "id": "not-01",
        "title": "Semester 6 End-Term Examination Schedule Released",
        "category": "examination",
        "content": "The Controller of Examinations has published the final datesheet for B.Tech Semester 6. Exams commence May 10, 2026. Hall tickets available on portal.",
        "published_by": "admin-001",
        "is_published": True,
        "target_role": "all",
        "published_at": datetime(2026, 4, 1, 10, 0, tzinfo=timezone.utc),
    },
    {
        "id": "not-02",
        "title": "Mandatory 75% Attendance Requirement Warning",
        "category": "academic",
        "content": "Students falling below 75% aggregate attendance will not be permitted to appear for university end-term examinations under Academic Regulation Clause 4.2.",
        "published_by": "admin-001",
        "is_published": True,
        "target_role": "student",
        "published_at": datetime(2026, 3, 20, 11, 30, tzinfo=timezone.utc),
    },
    {
        "id": "not-03",
        "title": "AWS Cloud Computing Hackathon & Workshop",
        "category": "event",
        "content": "Department of CSE is hosting a 48-hour Cloud Innovation Hackathon with industry mentors from AWS on April 25-26. Register via student council.",
        "published_by": "fac-001",
        "is_published": True,
        "target_role": "student",
        "published_at": datetime(2026, 3, 15, 14, 0, tzinfo=timezone.utc),
    },
    {
        "id": "not-04",
        "title": "Campus Power Maintenance Schedule - Scheduled Outage",
        "category": "urgent",
        "content": "Campus sub-station maintenance scheduled for Saturday 9 AM to 1 PM. Central server systems will operate on uninterrupted auxiliary generator backups.",
        "published_by": "admin-001",
        "is_published": True,
        "target_role": "all",
        "published_at": datetime(2026, 4, 5, 8, 0, tzinfo=timezone.utc),
    },
]
