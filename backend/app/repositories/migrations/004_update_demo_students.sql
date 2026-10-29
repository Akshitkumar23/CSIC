-- ==============================================================================
-- CSIC Migration 004: Update Demo Student, Faculty, and Admin Accounts
-- Updates:
-- - Students: Rashi (stu-001), Vanshika (stu-002), Silki (stu-003), Akshit (stu-004)
-- - Faculty: Akshit (fac-001), Prof. Anita Deshmukh (fac-002)
-- - Admin: Akshit (admin-001)
-- - Password for all: 1234 (bcrypt cost 12 hash: $2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi)
-- Compatible with PostgreSQL 16+ and SQLite 3+
-- ==============================================================================

UPDATE users
SET name = 'Rashi',
    email = 'rashi@csic.edu',
    password_hash = '$2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi'
WHERE id = 'stu-001';

UPDATE users
SET name = 'Vanshika',
    email = 'vanshika@csic.edu',
    password_hash = '$2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi'
WHERE id = 'stu-002';

UPDATE users
SET name = 'Silki',
    email = 'silki@csic.edu',
    password_hash = '$2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi'
WHERE id = 'stu-003';

INSERT INTO users (id, name, email, password_hash, role, phone, avatar_url, is_active)
VALUES ('stu-004', 'Akshit', 'akshit@csic.edu', '$2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi', 'student', '+91 98765 43213', NULL, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    email = EXCLUDED.email,
    password_hash = EXCLUDED.password_hash;

UPDATE users
SET name = 'Akshit',
    password_hash = '$2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi'
WHERE id = 'fac-001';

UPDATE users
SET password_hash = '$2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi'
WHERE id = 'fac-002';

UPDATE users
SET name = 'Akshit',
    password_hash = '$2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi'
WHERE id = 'admin-001';

INSERT INTO enrollments (id, user_id, course_id, roll_number, semester, section, status)
VALUES ('enr-004', 'stu-004', 'crs-01', 'CS2023004', 6, 'A', 'active')
ON CONFLICT (id) DO NOTHING;

INSERT INTO fee_records (id, invoice_number, enrollment_id, title, amount, amount_paid, due_date, status)
VALUES ('inv-005', 'INV-2026-005', 'enr-004', 'Semester 6 Academic Tuition Fee', 65000.00, 65000.00, '2026-01-30', 'paid')
ON CONFLICT (id) DO NOTHING;
