-- ==============================================================================
-- CSIC: Cloud-Based Student Information Chatbot
-- Simplified Relational Seed Data (11 Core Tables)
-- Compatible with PostgreSQL 16+ and SQLite 3+
-- ==============================================================================

-- 1. USERS
INSERT INTO users (id, name, email, password_hash, role, phone, avatar_url, is_active) VALUES
('stu-001', 'Aarav Sharma', 'aarav.sharma@csic.edu', '$2b$12$ewvtHUP1vfT2eZA5bI9kRuC6Adp5QxbjjWk9OcZP5WF9vwoZFmqsi', 'student', '+91 98765 43210', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Aarav', TRUE),
('stu-002', 'Priya Patel', 'priya.patel@csic.edu', '$2b$12$ewvtHUP1vfT2eZA5bI9kRuC6Adp5QxbjjWk9OcZP5WF9vwoZFmqsi', 'student', '+91 98765 43211', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Priya', TRUE),
('stu-003', 'Rohan Gupta', 'rohan.gupta@csic.edu', '$2b$12$ewvtHUP1vfT2eZA5bI9kRuC6Adp5QxbjjWk9OcZP5WF9vwoZFmqsi', 'student', '+91 98765 43212', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Rohan', TRUE),
('fac-001', 'Dr. Rajesh Kumar', 'rajesh.kumar@csic.edu', '$2b$12$eWwO5.KmhFAK0miGCgVhJeGqUY74Z0qBKp4p5INK0Q47zluNWS5Yy', 'faculty', '+91 98765 11223', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Rajesh', TRUE),
('fac-002', 'Prof. Anita Deshmukh', 'anita.deshmukh@csic.edu', '$2b$12$eWwO5.KmhFAK0miGCgVhJeGqUY74Z0qBKp4p5INK0Q47zluNWS5Yy', 'faculty', '+91 98765 11224', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Anita', TRUE),
('admin-001', 'Dean & System Admin', 'admin@csic.edu', '$2b$12$Lha58Xsa8EhCK4emMwPjCuKVP2ikM/VG2VsZlosxUjPRZoQmN81w6', 'admin', '+91 98765 00001', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Admin', TRUE)
ON CONFLICT (id) DO NOTHING;

-- 2. COURSES
INSERT INTO courses (id, code, name, department) VALUES
('crs-01', 'BTECH-CSE', 'Bachelor of Technology in Computer Science & Engineering', 'Computer Science & Engineering')
ON CONFLICT (id) DO NOTHING;

-- 3. SUBJECTS
INSERT INTO subjects (id, course_id, code, name, credits, semester, faculty_id) VALUES
('sub-01', 'crs-01', 'CS401', 'Cloud Computing & Distributed Systems', 4.0, 6, 'fac-001'),
('sub-02', 'crs-01', 'CS402', 'Advanced Database Engineering', 4.0, 6, 'fac-001'),
('sub-03', 'crs-01', 'CS403', 'Machine Learning & AI', 4.0, 6, 'fac-002'),
('sub-04', 'crs-01', 'CS404', 'Computer Networks & Security', 3.0, 6, 'fac-002')
ON CONFLICT (id) DO NOTHING;

-- 4. ENROLLMENTS
INSERT INTO enrollments (id, user_id, course_id, roll_number, semester, section, status) VALUES
('enr-001', 'stu-001', 'crs-01', 'CS2023001', 6, 'A', 'active'),
('enr-002', 'stu-002', 'crs-01', 'CS2023002', 6, 'A', 'active'),
('enr-003', 'stu-003', 'crs-01', 'CS2023003', 6, 'A', 'active')
ON CONFLICT (id) DO NOTHING;

-- 5. ATTENDANCE_RECORDS
-- 24 total class sessions (6 per subject) across February 2026
-- Sub-01 (Cloud Computing): Sessions 1 to 6
INSERT INTO attendance_records (id, enrollment_id, subject_id, session_date, status, remarks) VALUES
-- Aarav (enr-001): 6/6 present
('att-01-01', 'enr-001', 'sub-01', '2026-02-02', 'present', 'On time'),
('att-01-02', 'enr-001', 'sub-01', '2026-02-04', 'present', 'On time'),
('att-01-03', 'enr-001', 'sub-01', '2026-02-09', 'present', 'On time'),
('att-01-04', 'enr-001', 'sub-01', '2026-02-11', 'present', 'On time'),
('att-01-05', 'enr-001', 'sub-01', '2026-02-16', 'present', 'On time'),
('att-01-06', 'enr-001', 'sub-01', '2026-02-18', 'present', 'On time'),
-- Priya (enr-002): 5/6 present, 1 absent
('att-01-07', 'enr-002', 'sub-01', '2026-02-02', 'present', 'On time'),
('att-01-08', 'enr-002', 'sub-01', '2026-02-04', 'absent', 'Uninformed'),
('att-01-09', 'enr-002', 'sub-01', '2026-02-09', 'present', 'On time'),
('att-01-10', 'enr-002', 'sub-01', '2026-02-11', 'present', 'On time'),
('att-01-11', 'enr-002', 'sub-01', '2026-02-16', 'present', 'On time'),
('att-01-12', 'enr-002', 'sub-01', '2026-02-18', 'present', 'On time'),
-- Rohan (enr-003): 3/6 present, 3 absent (50% in Cloud Computing)
('att-01-13', 'enr-003', 'sub-01', '2026-02-02', 'absent', 'Uninformed'),
('att-01-14', 'enr-003', 'sub-01', '2026-02-04', 'present', 'On time'),
('att-01-15', 'enr-003', 'sub-01', '2026-02-09', 'absent', 'Uninformed'),
('att-01-16', 'enr-003', 'sub-01', '2026-02-11', 'present', 'On time'),
('att-01-17', 'enr-003', 'sub-01', '2026-02-16', 'absent', 'Uninformed'),
('att-01-18', 'enr-003', 'sub-01', '2026-02-18', 'present', 'On time'),

-- Sub-02 (Database Engineering): Sessions 7 to 12
-- Aarav: 5 present, 1 excused
('att-02-01', 'enr-001', 'sub-02', '2026-02-03', 'present', 'On time'),
('att-02-02', 'enr-001', 'sub-02', '2026-02-05', 'present', 'On time'),
('att-02-03', 'enr-001', 'sub-02', '2026-02-10', 'excused', 'Medical leave'),
('att-02-04', 'enr-001', 'sub-02', '2026-02-12', 'present', 'On time'),
('att-02-05', 'enr-001', 'sub-02', '2026-02-17', 'present', 'On time'),
('att-02-06', 'enr-001', 'sub-02', '2026-02-19', 'present', 'On time'),
-- Priya: 5 present, 1 excused
('att-02-07', 'enr-002', 'sub-02', '2026-02-03', 'present', 'On time'),
('att-02-08', 'enr-002', 'sub-02', '2026-02-05', 'present', 'On time'),
('att-02-09', 'enr-002', 'sub-02', '2026-02-10', 'excused', 'Sports duty'),
('att-02-10', 'enr-002', 'sub-02', '2026-02-12', 'present', 'On time'),
('att-02-11', 'enr-002', 'sub-02', '2026-02-17', 'present', 'On time'),
('att-02-12', 'enr-002', 'sub-02', '2026-02-19', 'present', 'On time'),
-- Rohan: 4 present, 2 absent
('att-02-13', 'enr-003', 'sub-02', '2026-02-03', 'present', 'On time'),
('att-02-14', 'enr-003', 'sub-02', '2026-02-05', 'absent', 'Uninformed'),
('att-02-15', 'enr-003', 'sub-02', '2026-02-10', 'present', 'On time'),
('att-02-16', 'enr-003', 'sub-02', '2026-02-12', 'present', 'On time'),
('att-02-17', 'enr-003', 'sub-02', '2026-02-17', 'absent', 'Uninformed'),
('att-02-18', 'enr-003', 'sub-02', '2026-02-19', 'present', 'On time'),

-- Sub-03 (Machine Learning): Sessions 13 to 18
-- Aarav: 6 present
('att-03-01', 'enr-001', 'sub-03', '2026-02-06', 'present', 'On time'),
('att-03-02', 'enr-001', 'sub-03', '2026-02-08', 'present', 'On time'),
('att-03-03', 'enr-001', 'sub-03', '2026-02-13', 'present', 'On time'),
('att-03-04', 'enr-001', 'sub-03', '2026-02-15', 'present', 'On time'),
('att-03-05', 'enr-001', 'sub-03', '2026-02-20', 'present', 'On time'),
('att-03-06', 'enr-001', 'sub-03', '2026-02-22', 'present', 'On time'),
-- Priya: 5 present, 1 absent
('att-03-07', 'enr-002', 'sub-03', '2026-02-06', 'present', 'On time'),
('att-03-08', 'enr-002', 'sub-03', '2026-02-08', 'present', 'On time'),
('att-03-09', 'enr-002', 'sub-03', '2026-02-13', 'absent', 'Uninformed'),
('att-03-10', 'enr-002', 'sub-03', '2026-02-15', 'present', 'On time'),
('att-03-11', 'enr-002', 'sub-03', '2026-02-20', 'present', 'On time'),
('att-03-12', 'enr-002', 'sub-03', '2026-02-22', 'present', 'On time'),
-- Rohan: 3 present, 1 excused, 2 absent
('att-03-13', 'enr-003', 'sub-03', '2026-02-06', 'present', 'On time'),
('att-03-14', 'enr-003', 'sub-03', '2026-02-08', 'absent', 'Uninformed'),
('att-03-15', 'enr-003', 'sub-03', '2026-02-13', 'excused', 'Medical'),
('att-03-16', 'enr-003', 'sub-03', '2026-02-15', 'absent', 'Uninformed'),
('att-03-17', 'enr-003', 'sub-03', '2026-02-20', 'present', 'On time'),
('att-03-18', 'enr-003', 'sub-03', '2026-02-22', 'present', 'On time'),

-- Sub-04 (Computer Networks): Sessions 19 to 24
-- Aarav: 5 present, 1 absent
('att-04-01', 'enr-001', 'sub-04', '2026-02-07', 'present', 'On time'),
('att-04-02', 'enr-001', 'sub-04', '2026-02-14', 'present', 'On time'),
('att-04-03', 'enr-001', 'sub-04', '2026-02-21', 'present', 'On time'),
('att-04-04', 'enr-001', 'sub-04', '2026-02-24', 'present', 'On time'),
('att-04-05', 'enr-001', 'sub-04', '2026-02-26', 'present', 'On time'),
('att-04-06', 'enr-001', 'sub-04', '2026-02-28', 'absent', 'Uninformed'),
-- Priya: 5 present, 1 absent
('att-04-07', 'enr-002', 'sub-04', '2026-02-07', 'present', 'On time'),
('att-04-08', 'enr-002', 'sub-04', '2026-02-14', 'present', 'On time'),
('att-04-09', 'enr-002', 'sub-04', '2026-02-21', 'present', 'On time'),
('att-04-10', 'enr-002', 'sub-04', '2026-02-24', 'absent', 'Uninformed'),
('att-04-11', 'enr-002', 'sub-04', '2026-02-26', 'present', 'On time'),
('att-04-12', 'enr-002', 'sub-04', '2026-02-28', 'present', 'On time'),
-- Rohan: 4 present, 2 absent
('att-04-13', 'enr-003', 'sub-04', '2026-02-07', 'absent', 'Uninformed'),
('att-04-14', 'enr-003', 'sub-04', '2026-02-14', 'present', 'On time'),
('att-04-15', 'enr-003', 'sub-04', '2026-02-21', 'present', 'On time'),
('att-04-16', 'enr-003', 'sub-04', '2026-02-24', 'absent', 'Uninformed'),
('att-04-17', 'enr-003', 'sub-04', '2026-02-26', 'present', 'On time'),
('att-04-18', 'enr-003', 'sub-04', '2026-02-28', 'present', 'On time')
ON CONFLICT (id) DO NOTHING;

-- 6. EXAMINATIONS
INSERT INTO examinations (id, subject_id, name, exam_date, max_marks, weightage_percentage) VALUES
('exam-mid-01', 'sub-01', 'Mid-Term Examination 2026', '2026-03-10', 50.0, 30.0),
('exam-mid-02', 'sub-02', 'Mid-Term Examination 2026', '2026-03-12', 50.0, 30.0),
('exam-mid-03', 'sub-03', 'Mid-Term Examination 2026', '2026-03-15', 50.0, 30.0),
('exam-mid-04', 'sub-04', 'Mid-Term Examination 2026', '2026-03-18', 50.0, 30.0)
ON CONFLICT (id) DO NOTHING;

-- 7. MARKS
INSERT INTO marks (id, examination_id, enrollment_id, marks_obtained, is_absent, grade) VALUES
-- Aarav (enr-001): Excellent performance
('mark-01', 'exam-mid-01', 'enr-001', 46.5, FALSE, 'A+'),
('mark-02', 'exam-mid-02', 'enr-001', 44.0, FALSE, 'A'),
('mark-03', 'exam-mid-03', 'enr-001', 48.0, FALSE, 'O'),
('mark-04', 'exam-mid-04', 'enr-001', 42.0, FALSE, 'A'),
-- Priya (enr-002): Strong performance
('mark-05', 'exam-mid-01', 'enr-002', 41.0, FALSE, 'A'),
('mark-06', 'exam-mid-02', 'enr-002', 40.0, FALSE, 'B+'),
('mark-07', 'exam-mid-03', 'enr-002', 45.0, FALSE, 'A+'),
('mark-08', 'exam-mid-04', 'enr-002', 38.5, FALSE, 'B+'),
-- Rohan (enr-003): Needs improvement
('mark-09', 'exam-mid-01', 'enr-003', 26.0, FALSE, 'C'),
('mark-10', 'exam-mid-02', 'enr-003', 24.5, FALSE, 'C'),
('mark-11', 'exam-mid-03', 'enr-003', 29.0, FALSE, 'B'),
('mark-12', 'exam-mid-04', 'enr-003', 21.0, FALSE, 'P')
ON CONFLICT (id) DO NOTHING;

-- 8. FEE_RECORDS
INSERT INTO fee_records (id, invoice_number, enrollment_id, title, amount, amount_paid, due_date, status) VALUES
('inv-001', 'INV-2026-001', 'enr-001', 'Semester 6 Academic Tuition Fee', 65000.00, 65000.00, '2026-01-30', 'paid'),
('inv-002', 'INV-2026-002', 'enr-001', 'Cloud Computing Specialization Lab Fee', 12500.00, 12500.00, '2026-02-28', 'paid'),
('inv-003', 'INV-2026-003', 'enr-002', 'Semester 6 Academic Tuition Fee', 65000.00, 35000.00, '2026-01-30', 'partially_paid'),
('inv-004', 'INV-2026-004', 'enr-003', 'Semester 6 Academic Tuition Fee', 65000.00, 0.00, '2026-01-30', 'unpaid')
ON CONFLICT (id) DO NOTHING;

-- 9. TIMETABLE_ENTRIES
INSERT INTO timetable_entries (id, subject_id, day_of_week, start_time, end_time, room_number) VALUES
-- Monday
('tt-01', 'sub-01', 'Monday', '09:00', '10:00', 'LH-301'),
('tt-02', 'sub-02', 'Monday', '10:15', '11:15', 'Lab-204'),
('tt-03', 'sub-03', 'Monday', '11:30', '12:30', 'LH-302'),
-- Tuesday
('tt-04', 'sub-04', 'Tuesday', '09:00', '10:00', 'LH-301'),
('tt-05', 'sub-01', 'Tuesday', '10:15', '11:15', 'LH-301'),
-- Wednesday
('tt-06', 'sub-02', 'Wednesday', '09:00', '10:00', 'Lab-204'),
('tt-07', 'sub-03', 'Wednesday', '10:15', '11:15', 'LH-302'),
-- Thursday
('tt-08', 'sub-04', 'Thursday', '09:00', '10:00', 'LH-301'),
('tt-09', 'sub-01', 'Thursday', '11:30', '12:30', 'LH-301'),
-- Friday
('tt-10', 'sub-03', 'Friday', '09:00', '10:00', 'LH-302'),
('tt-11', 'sub-02', 'Friday', '10:15', '11:15', 'Lab-204')
ON CONFLICT (id) DO NOTHING;

-- 10. NOTICES
INSERT INTO notices (id, title, content, category, target_role, published_by, is_published, published_at) VALUES
('not-01', 'Semester 6 End-Term Examination Schedule Released', 'The Controller of Examinations has published the final datesheet for B.Tech Semester 6. Exams commence May 10, 2026. Hall tickets available on portal.', 'examination', 'all', 'admin-001', TRUE, '2026-04-01 10:00:00'),
('not-02', 'Mandatory 75% Attendance Requirement Warning', 'Students falling below 75% aggregate attendance will not be permitted to appear for university end-term examinations under Academic Regulation Clause 4.2.', 'academic', 'student', 'admin-001', TRUE, '2026-03-20 11:30:00'),
('not-03', 'AWS Cloud Computing Hackathon & Workshop', 'Department of CSE is hosting a 48-hour Cloud Innovation Hackathon with industry mentors from AWS on April 25-26. Register via student council.', 'event', 'student', 'fac-001', TRUE, '2026-03-15 14:00:00'),
('not-04', 'Campus Power Maintenance Schedule - Scheduled Outage', 'Campus sub-station maintenance scheduled for Saturday 9 AM to 1 PM. Central server systems will operate on uninterrupted auxiliary generator backups.', 'urgent', 'all', 'admin-001', TRUE, '2026-04-05 08:00:00')
ON CONFLICT (id) DO NOTHING;

-- 11. CHAT_HISTORY (Initial sample turns)
INSERT INTO chat_history (id, user_id, message, reply, intent, created_at) VALUES
('chat-01', 'stu-001', 'What is my attendance in Cloud Computing?', 'Your attendance in Cloud Computing & Distributed Systems (CS401) is 100.0% (6 attended out of 6 total sessions).', 'attendance', '2026-04-02 09:15:00'),
('chat-02', 'stu-001', 'Do I have any pending fee balance?', 'All your fee dues for Semester 6 are fully cleared! Total paid: ₹77,500.00 across 2 invoices. Outstanding balance is ₹0.00.', 'fees', '2026-04-03 14:20:00')
ON CONFLICT (id) DO NOTHING;
