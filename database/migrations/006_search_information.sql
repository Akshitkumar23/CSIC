-- ==============================================================================
-- CSIC: Cloud-Based Student Information Chatbot
-- Migration 006: Search Information Module
-- ANSI SQL Standard: Compatible with PostgreSQL 16+ and SQLite 3+
-- ==============================================================================

-- 1. SEARCH_INFORMATION: Institutional repository filterable by branch, year, category, and subject
CREATE TABLE IF NOT EXISTS search_information (
    id VARCHAR(64) PRIMARY KEY,
    branch VARCHAR(100) NOT NULL,
    year INT NOT NULL CHECK (year BETWEEN 1 AND 4),
    category VARCHAR(50) NOT NULL, -- Syllabus, Timetable, Results, Fees, FAQ
    subject VARCHAR(150) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content_details TEXT NOT NULL,
    file_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_search_info_lookup ON search_information(branch, year, category);
CREATE INDEX IF NOT EXISTS idx_search_info_subject ON search_information(subject);

-- 2. SEED REFERENCE RECORDS (From Academic Synopsis / modules_schema.sql)
INSERT INTO search_information (id, branch, year, category, subject, title, content_details, file_url) VALUES
('info-001', 'Computer Science & Engineering', 3, 'Syllabus', 'Cloud Computing & Distributed Systems', 'CS401 Complete Course Syllabus & Lab Manual', 'Unit 1: Virtualization & Cloud Models, Unit 2: Storage & Networking, Unit 3: AWS/GCP Hands-on. 4 Credits.', '/docs/syllabus/cs401_syllabus.pdf'),
('info-002', 'Computer Science & Engineering', 3, 'Timetable', 'Advanced Database Engineering', 'CS402 Lecture and Lab Timing', 'Monday 10:15 - 11:15 AM (Lab-204), Wednesday 09:00 - 10:00 AM (Lab-204), Friday 10:15 - 11:15 AM.', '/docs/timetable/cse_sem6_tt.pdf'),
('info-003', 'Computer Science & Engineering', 3, 'Results', 'Machine Learning & AI', 'CS403 Mid-Term Result Summary', 'Exam Date: 15-Mar-2026. Max Marks: 50. Class Average: 43.5. Highest Score: 49.5 (Grade O).', '/docs/results/midterm_cs403.pdf'),
('info-004', 'Computer Science & Engineering', 3, 'Fees', 'Accounts Section', 'Semester 6 Academic & Specialization Lab Fee Details', 'Semester 6 Academic Tuition: ₹65,000.00 (Due: 30-Jan-2026). Lab Fee: ₹12,500.00 (Due: 28-Feb-2026).', '/docs/fees/sem6_structure.pdf'),
('info-005', 'Computer Science & Engineering', 3, 'FAQ', 'Academic Regulations', 'Minimum Attendance & Exam Hall Ticket Eligibility', 'Students must maintain minimum 75% aggregate attendance to appear in End-Term University Examinations.', '/docs/faq/attendance_rules.pdf')
ON CONFLICT (id) DO NOTHING;
