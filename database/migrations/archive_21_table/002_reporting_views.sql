-- ==============================================================================
-- Cloud-Based Student Information Chatbot (CSIC)
-- Migration: 002_reporting_views.sql
-- Description: 10 Analytical & Operational Database Views
-- Compliance: PostgreSQL 15+, Supabase
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- View 1: v_student_attendance
-- Calculates subject-wise conducted sessions, attendance, excused absences,
-- and percentage. Excludes cancelled sessions strictly from denominator.
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_student_attendance AS
SELECT 
    e.id AS enrollment_id,
    e.student_id,
    p.full_name AS student_name,
    e.roll_number,
    c.id AS course_id,
    prog.id AS program_id,
    prog.name AS program_name,
    sem.id AS semester_id,
    sem.semester_number,
    c.section,
    s.id AS subject_id,
    s.code AS subject_code,
    s.name AS subject_name,
    prof.full_name AS faculty_name,
    COUNT(cs.id) AS total_sessions_conducted,
    COUNT(CASE WHEN ar.status = 'present' THEN 1 END) AS sessions_present,
    COUNT(CASE WHEN ar.status = 'absent' THEN 1 END) AS sessions_absent,
    COUNT(CASE WHEN ar.status = 'excused' THEN 1 END) AS sessions_excused,
    COUNT(CASE WHEN ar.status = 'late' THEN 1 END) AS sessions_late,
    COUNT(CASE WHEN ar.status IN ('present', 'excused') THEN 1 END) AS attended_effective,
    COALESCE(
        ROUND(
            (COUNT(CASE WHEN ar.status IN ('present', 'excused') THEN 1.0 END) * 100.0) 
            / NULLIF(COUNT(cs.id), 0), 
            2
        ), 
        0.00
    ) AS attendance_percentage
FROM enrollments e
JOIN profiles p ON e.student_id = p.id
JOIN courses c ON e.course_id = c.id
JOIN programs prog ON c.program_id = prog.id
JOIN semesters sem ON c.semester_id = sem.id
JOIN faculty_assignments fa ON fa.course_id = c.id
JOIN subjects s ON fa.subject_id = s.id
JOIN profiles prof ON fa.faculty_id = prof.id
LEFT JOIN class_sessions cs ON cs.faculty_assignment_id = fa.id AND cs.status = 'conducted'
LEFT JOIN attendance_records ar ON ar.session_id = cs.id AND ar.enrollment_id = e.id
GROUP BY 
    e.id, e.student_id, p.full_name, e.roll_number, 
    c.id, prog.id, prog.name, sem.id, sem.semester_number, c.section,
    s.id, s.code, s.name, prof.full_name;

-- ------------------------------------------------------------------------------
-- View 2: v_low_attendance_warnings
-- Identifies students with attendance < 75.00%, assigning risk categories
-- and calculating the exact recovery sessions needed to clear eligibility.
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_low_attendance_warnings AS
SELECT 
    enrollment_id,
    student_id,
    roll_number,
    student_name,
    course_id,
    program_name,
    semester_number,
    section,
    subject_id,
    subject_code,
    subject_name,
    faculty_name,
    total_sessions_conducted,
    attended_effective,
    sessions_absent,
    attendance_percentage,
    ROUND(75.00 - attendance_percentage, 2) AS shortfall_percentage,
    CASE 
        WHEN attendance_percentage < 60.00 THEN 'CRITICAL'
        ELSE 'WARNING'
    END AS warning_level,
    -- Formula: To achieve (attended + x) / (total + x) >= 0.75 => x >= 3*total - 4*attended
    GREATEST(0, CEIL((3.0 * total_sessions_conducted) - (4.0 * attended_effective)))::INT AS sessions_needed_to_clear_75
FROM v_student_attendance
WHERE total_sessions_conducted > 0 
  AND attendance_percentage < 75.00;

-- ------------------------------------------------------------------------------
-- View 3: v_subject_performance_summary
-- Aggregates exam statistics: candidate counts, average/min/max marks, and pass rates.
-- Passing criteria: marks_obtained >= 40% of max_marks.
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_subject_performance_summary AS
SELECT 
    s.id AS subject_id,
    s.code AS subject_code,
    s.name AS subject_name,
    ex.course_id,
    ex.id AS examination_id,
    ex.name AS exam_name,
    ex.exam_date,
    ex.max_marks,
    ex.weightage_percentage,
    COUNT(m.id) AS total_evaluated_candidates,
    COUNT(CASE WHEN m.is_absent = FALSE THEN 1 END) AS appeared_candidates,
    COUNT(CASE WHEN m.is_absent = TRUE THEN 1 END) AS absent_candidates,
    ROUND(AVG(CASE WHEN m.is_absent = FALSE THEN m.marks_obtained END), 2) AS avg_marks_obtained,
    MIN(CASE WHEN m.is_absent = FALSE THEN m.marks_obtained END) AS min_marks_obtained,
    MAX(CASE WHEN m.is_absent = FALSE THEN m.marks_obtained END) AS max_marks_obtained,
    COUNT(CASE WHEN m.is_absent = FALSE AND m.marks_obtained >= (0.40 * ex.max_marks) THEN 1 END) AS passed_candidates,
    COUNT(CASE WHEN m.is_absent = TRUE OR m.marks_obtained < (0.40 * ex.max_marks) THEN 1 END) AS failed_candidates,
    COALESCE(
        ROUND(
            (COUNT(CASE WHEN m.is_absent = FALSE AND m.marks_obtained >= (0.40 * ex.max_marks) THEN 1.0 END) * 100.0) 
            / NULLIF(COUNT(CASE WHEN m.is_absent = FALSE THEN 1 END), 0), 
            2
        ), 
        0.00
    ) AS pass_percentage
FROM examinations ex
JOIN subjects s ON ex.subject_id = s.id
LEFT JOIN marks m ON m.examination_id = ex.id
GROUP BY 
    s.id, s.code, s.name, 
    ex.course_id, ex.id, ex.name, ex.exam_date, ex.max_marks, ex.weightage_percentage;

-- ------------------------------------------------------------------------------
-- View 4: v_semester_result_summary
-- Aggregates overall marks, percentage, GPA conversion and backlog status per student.
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_semester_result_summary AS
SELECT 
    e.id AS enrollment_id,
    e.student_id,
    p.full_name AS student_name,
    e.roll_number,
    c.id AS course_id,
    prog.name AS program_name,
    sem.semester_number,
    COUNT(m.id) AS exams_evaluated_count,
    COALESCE(SUM(CASE WHEN m.is_absent = FALSE THEN m.marks_obtained ELSE 0 END), 0.00) AS total_marks_obtained,
    COALESCE(SUM(ex.max_marks), 0.00) AS total_max_marks,
    COALESCE(
        ROUND(
            (SUM(CASE WHEN m.is_absent = FALSE THEN m.marks_obtained ELSE 0 END) * 100.0)
            / NULLIF(SUM(ex.max_marks), 0),
            2
        ),
        0.00
    ) AS overall_percentage,
    COALESCE(
        ROUND(
            ((SUM(CASE WHEN m.is_absent = FALSE THEN m.marks_obtained ELSE 0 END) * 100.0)
            / NULLIF(SUM(ex.max_marks), 0)) / 10.0,
            2
        ),
        0.00
    ) AS gpa_equivalent,
    COUNT(CASE WHEN m.is_absent = TRUE OR m.marks_obtained < (0.40 * ex.max_marks) THEN 1 END) AS failed_exams_count,
    CASE 
        WHEN COUNT(CASE WHEN m.is_absent = TRUE OR m.marks_obtained < (0.40 * ex.max_marks) THEN 1 END) > 0 THEN 'BACKLOG'
        WHEN (SUM(CASE WHEN m.is_absent = FALSE THEN m.marks_obtained ELSE 0 END) * 100.0) / NULLIF(SUM(ex.max_marks), 0) >= 75.00 THEN 'DISTINCTION'
        WHEN (SUM(CASE WHEN m.is_absent = FALSE THEN m.marks_obtained ELSE 0 END) * 100.0) / NULLIF(SUM(ex.max_marks), 0) >= 60.00 THEN 'FIRST CLASS'
        ELSE 'SECOND CLASS'
    END AS academic_standing
FROM enrollments e
JOIN profiles p ON e.student_id = p.id
JOIN courses c ON e.course_id = c.id
JOIN programs prog ON c.program_id = prog.id
JOIN semesters sem ON c.semester_id = sem.id
JOIN marks m ON m.enrollment_id = e.id
JOIN examinations ex ON m.examination_id = ex.id
GROUP BY 
    e.id, e.student_id, p.full_name, e.roll_number, c.id, prog.name, sem.semester_number;

-- ------------------------------------------------------------------------------
-- View 5: v_faculty_workload
-- Aggregates weekly teaching contact hours and unique course assignments.
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_faculty_workload AS
SELECT 
    prof.id AS faculty_id,
    prof.full_name AS faculty_name,
    prof.email AS faculty_email,
    d.name AS department_name,
    COUNT(DISTINCT fa.subject_id) AS assigned_subjects_count,
    COUNT(DISTINCT fa.course_id) AS assigned_courses_count,
    COUNT(te.id) AS weekly_scheduled_slots,
    COALESCE(
        ROUND(
            SUM(EXTRACT(EPOCH FROM (te.end_time - te.start_time)) / 3600.0)::NUMERIC, 
            2
        ),
        0.00
    ) AS weekly_teaching_hours
FROM profiles prof
JOIN departments d ON d.head_of_department_id = prof.id OR d.id = prof.id OR prof.role = 'faculty'
LEFT JOIN faculty_assignments fa ON fa.faculty_id = prof.id
LEFT JOIN timetable_entries te ON te.faculty_assignment_id = fa.id
WHERE prof.role = 'faculty'
GROUP BY prof.id, prof.full_name, prof.email, d.name;

-- ------------------------------------------------------------------------------
-- View 6: v_course_enrollment_counts
-- Counts active, dropped, and suspended students per program, semester, section.
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_course_enrollment_counts AS
SELECT 
    c.id AS course_id,
    prog.id AS program_id,
    prog.code AS program_code,
    prog.name AS program_name,
    sem.id AS semester_id,
    sem.semester_number,
    sem.term,
    c.section,
    COUNT(CASE WHEN e.status = 'active' THEN 1 END) AS active_enrollment_count,
    COUNT(CASE WHEN e.status = 'dropped' THEN 1 END) AS dropped_count,
    COUNT(CASE WHEN e.status = 'suspended' THEN 1 END) AS suspended_count,
    COUNT(CASE WHEN e.status = 'completed' THEN 1 END) AS completed_count,
    COUNT(e.id) AS total_enrollment_count
FROM courses c
JOIN programs prog ON c.program_id = prog.id
JOIN semesters sem ON c.semester_id = sem.id
LEFT JOIN enrollments e ON e.course_id = c.id
GROUP BY 
    c.id, prog.id, prog.code, prog.name, sem.id, sem.semester_number, sem.term, c.section;

-- ------------------------------------------------------------------------------
-- View 7: v_fee_outstanding_summary
-- Computes total billed invoices, paid receipts, and balance per enrollment.
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_fee_outstanding_summary AS
SELECT 
    e.id AS enrollment_id,
    e.student_id,
    p.full_name AS student_name,
    e.roll_number,
    c.id AS course_id,
    prog.name AS program_name,
    sem.semester_number,
    COUNT(DISTINCT fi.id) AS total_invoices_count,
    COALESCE(SUM(fi.amount), 0.00) AS total_amount_invoiced,
    COALESCE(
        (SELECT SUM(fp.amount_paid) 
         FROM fee_payments fp 
         JOIN fee_invoices fi_sub ON fp.invoice_id = fi_sub.id 
         WHERE fi_sub.enrollment_id = e.id AND fp.status = 'success'), 
        0.00
    ) AS total_amount_paid,
    GREATEST(
        0.00,
        COALESCE(SUM(fi.amount), 0.00) - 
        COALESCE(
            (SELECT SUM(fp.amount_paid) 
             FROM fee_payments fp 
             JOIN fee_invoices fi_sub ON fp.invoice_id = fi_sub.id 
             WHERE fi_sub.enrollment_id = e.id AND fp.status = 'success'), 
            0.00
        )
    ) AS outstanding_balance,
    COUNT(CASE WHEN fi.status = 'overdue' THEN 1 END) AS overdue_invoices_count,
    CASE 
        WHEN COALESCE((SELECT SUM(fp.amount_paid) FROM fee_payments fp JOIN fee_invoices fi_sub ON fp.invoice_id = fi_sub.id WHERE fi_sub.enrollment_id = e.id AND fp.status = 'success'), 0.00) >= COALESCE(SUM(fi.amount), 0.00) AND COALESCE(SUM(fi.amount), 0.00) > 0 THEN 'PAID'
        WHEN COALESCE((SELECT SUM(fp.amount_paid) FROM fee_payments fp JOIN fee_invoices fi_sub ON fp.invoice_id = fi_sub.id WHERE fi_sub.enrollment_id = e.id AND fp.status = 'success'), 0.00) > 0 THEN 'PARTIALLY_PAID'
        ELSE 'UNPAID'
    END AS overall_payment_status
FROM enrollments e
JOIN profiles p ON e.student_id = p.id
JOIN courses c ON e.course_id = c.id
JOIN programs prog ON c.program_id = prog.id
JOIN semesters sem ON c.semester_id = sem.id
LEFT JOIN fee_invoices fi ON fi.enrollment_id = e.id AND fi.status != 'cancelled'
GROUP BY 
    e.id, e.student_id, p.full_name, e.roll_number, c.id, prog.name, sem.semester_number;

-- ------------------------------------------------------------------------------
-- View 8: v_upcoming_examinations
-- Displays examinations scheduled within the upcoming 30 days.
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_upcoming_examinations AS
SELECT 
    ex.id AS examination_id,
    ex.name AS exam_name,
    ex.exam_date,
    ex.max_marks,
    ex.weightage_percentage,
    s.id AS subject_id,
    s.code AS subject_code,
    s.name AS subject_name,
    c.id AS course_id,
    prog.name AS program_name,
    sem.semester_number,
    c.section,
    (ex.exam_date - CURRENT_DATE) AS days_until_exam
FROM examinations ex
JOIN subjects s ON ex.subject_id = s.id
JOIN courses c ON ex.course_id = c.id
JOIN programs prog ON c.program_id = prog.id
JOIN semesters sem ON c.semester_id = sem.id
WHERE ex.exam_date >= CURRENT_DATE 
  AND ex.exam_date <= (CURRENT_DATE + INTERVAL '30 days')
ORDER BY ex.exam_date ASC;

-- ------------------------------------------------------------------------------
-- View 9: v_notices_by_category
-- Summarizes notices partitioned by category, target role, and month.
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_notices_by_category AS
SELECT 
    category,
    target_role,
    TO_CHAR(COALESCE(published_at, created_at), 'YYYY-MM') AS publication_month,
    COUNT(id) AS total_notices,
    COUNT(CASE WHEN is_published = TRUE THEN 1 END) AS published_count,
    COUNT(CASE WHEN is_published = FALSE THEN 1 END) AS draft_count
FROM notices
GROUP BY 
    category, target_role, TO_CHAR(COALESCE(published_at, created_at), 'YYYY-MM');

-- ------------------------------------------------------------------------------
-- View 10: v_audit_activity_report
-- Aggregates administrative system operations by actor, action, and day.
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_audit_activity_report AS
SELECT 
    al.created_at::DATE AS activity_date,
    al.actor_id,
    COALESCE(p.full_name, 'System') AS actor_name,
    COALESCE(p.role, 'system') AS actor_role,
    al.action,
    al.entity_name,
    COUNT(al.id) AS operation_count
FROM audit_logs al
LEFT JOIN profiles p ON al.actor_id = p.id
GROUP BY 
    al.created_at::DATE, al.actor_id, p.full_name, p.role, al.action, al.entity_name;
