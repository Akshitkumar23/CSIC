-- ==============================================================================
-- CSIC Migration 005: Synchronize Demo Login Accounts and Institutional Data
-- Target Accounts:
--   Students:
--     - Rashi (stu-001)                -> rashi@csic.edu          / 1234
--     - Vanshika (stu-002)             -> vanshika@csic.edu       / 1234
--     - Silki (stu-003)                -> silki@csic.edu          / 1234
--     - Akshit (stu-004)               -> akshit@csic.edu         / 1234
--   Faculty:
--     - Akshit (fac-001)               -> rajesh.kumar@csic.edu   / 1234
--     - Prof. Anita Deshmukh (fac-002) -> anita.deshmukh@csic.edu / 1234
--   Administrator:
--     - Akshit (admin-001)             -> admin@csic.edu          / 1234
--
-- Password Hash: $2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi
-- (Bcrypt cost 12, rigorously verified against password '1234')
-- Compatible with PostgreSQL 16+ and SQLite 3+ (Idempotent and safe to re-run)
-- ==============================================================================

-- 1. Ensure Multi-Session Chat Tables Exist
CREATE TABLE IF NOT EXISTS chat_sessions (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    sender_role VARCHAR(20) NOT NULL CHECK (sender_role IN ('user', 'assistant', 'system')),
    message_text TEXT NOT NULL,
    query_type VARCHAR(50),
    sources TEXT,
    verified_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON chat_sessions(user_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id, created_at ASC);

-- 2. Upsert the 7 Authoritative Demo User Accounts
INSERT INTO users (id, name, email, password_hash, role, phone, is_active)
VALUES
  ('stu-001', 'Rashi', 'rashi@csic.edu', '$2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi', 'student', '+91 98765 43210', TRUE),
  ('stu-002', 'Vanshika', 'vanshika@csic.edu', '$2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi', 'student', '+91 98765 43211', TRUE),
  ('stu-003', 'Silki', 'silki@csic.edu', '$2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi', 'student', '+91 98765 43212', TRUE),
  ('stu-004', 'Akshit', 'akshit@csic.edu', '$2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi', 'student', '+91 98765 43213', TRUE),
  ('fac-001', 'Akshit', 'rajesh.kumar@csic.edu', '$2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi', 'faculty', '+91 98765 11223', TRUE),
  ('fac-002', 'Prof. Anita Deshmukh', 'anita.deshmukh@csic.edu', '$2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi', 'faculty', '+91 98765 11224', TRUE),
  ('admin-001', 'Akshit', 'admin@csic.edu', '$2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi', 'admin', '+91 98765 00001', TRUE)
ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  email = EXCLUDED.email,
  password_hash = EXCLUDED.password_hash,
  role = EXCLUDED.role,
  phone = EXCLUDED.phone,
  is_active = EXCLUDED.is_active;

-- 3. Akshit (stu-004) Academic Course Enrollment
INSERT INTO enrollments (id, user_id, course_id, roll_number, semester, section, status)
VALUES ('enr-004', 'stu-004', 'crs-01', 'CS2023004', 6, 'A', 'active')
ON CONFLICT (id) DO UPDATE SET
  user_id = EXCLUDED.user_id,
  course_id = EXCLUDED.course_id,
  roll_number = EXCLUDED.roll_number,
  semester = EXCLUDED.semester,
  section = EXCLUDED.section,
  status = EXCLUDED.status;

-- 4. Akshit (enr-004) Cleared Tuition Fee Record
INSERT INTO fee_records (id, invoice_number, enrollment_id, title, amount, amount_paid, due_date, status)
VALUES ('inv-005', 'INV-2026-005', 'enr-004', 'Semester 6 Academic Tuition Fee', 65000.00, 65000.00, '2026-01-30', 'paid')
ON CONFLICT (id) DO UPDATE SET
  enrollment_id = EXCLUDED.enrollment_id,
  title = EXCLUDED.title,
  amount = EXCLUDED.amount,
  amount_paid = EXCLUDED.amount_paid,
  status = EXCLUDED.status;

-- 5. Akshit (enr-004) Attendance Records (24 Classroom Sessions, 100% Attendance)
INSERT INTO attendance_records (id, enrollment_id, subject_id, session_date, status, remarks) VALUES
('att-01-19', 'enr-004', 'sub-01', '2026-02-02', 'present', 'On time'),
('att-01-20', 'enr-004', 'sub-01', '2026-02-04', 'present', 'On time'),
('att-01-21', 'enr-004', 'sub-01', '2026-02-09', 'present', 'On time'),
('att-01-22', 'enr-004', 'sub-01', '2026-02-11', 'present', 'On time'),
('att-01-23', 'enr-004', 'sub-01', '2026-02-16', 'present', 'On time'),
('att-01-24', 'enr-004', 'sub-01', '2026-02-18', 'present', 'On time'),
('att-02-19', 'enr-004', 'sub-02', '2026-02-03', 'present', 'On time'),
('att-02-20', 'enr-004', 'sub-02', '2026-02-05', 'present', 'On time'),
('att-02-21', 'enr-004', 'sub-02', '2026-02-10', 'present', 'On time'),
('att-02-22', 'enr-004', 'sub-02', '2026-02-12', 'present', 'On time'),
('att-02-23', 'enr-004', 'sub-02', '2026-02-17', 'present', 'On time'),
('att-02-24', 'enr-004', 'sub-02', '2026-02-19', 'present', 'On time'),
('att-03-19', 'enr-004', 'sub-03', '2026-02-06', 'present', 'On time'),
('att-03-20', 'enr-004', 'sub-03', '2026-02-08', 'present', 'On time'),
('att-03-21', 'enr-004', 'sub-03', '2026-02-13', 'present', 'On time'),
('att-03-22', 'enr-004', 'sub-03', '2026-02-15', 'present', 'On time'),
('att-03-23', 'enr-004', 'sub-03', '2026-02-20', 'present', 'On time'),
('att-03-24', 'enr-004', 'sub-03', '2026-02-22', 'present', 'On time'),
('att-04-19', 'enr-004', 'sub-04', '2026-02-07', 'present', 'On time'),
('att-04-20', 'enr-004', 'sub-04', '2026-02-14', 'present', 'On time'),
('att-04-21', 'enr-004', 'sub-04', '2026-02-21', 'present', 'On time'),
('att-04-22', 'enr-004', 'sub-04', '2026-02-24', 'present', 'On time'),
('att-04-23', 'enr-004', 'sub-04', '2026-02-26', 'present', 'On time'),
('att-04-24', 'enr-004', 'sub-04', '2026-02-28', 'present', 'On time')
ON CONFLICT (id) DO NOTHING;

-- 6. Akshit (enr-004) Mid-Term Examination Scores
INSERT INTO marks (id, examination_id, enrollment_id, marks_obtained, is_absent, grade) VALUES
('mark-13', 'exam-mid-01', 'enr-004', 48.0, FALSE, 'O'),
('mark-14', 'exam-mid-02', 'enr-004', 47.0, FALSE, 'O'),
('mark-15', 'exam-mid-03', 'enr-004', 49.5, FALSE, 'O'),
('mark-16', 'exam-mid-04', 'enr-004', 46.0, FALSE, 'A+')
ON CONFLICT (id) DO NOTHING;

-- 7. Verification: Confirm All 7 Accounts
SELECT id, name, email, role, is_active FROM users ORDER BY role, id;
