-- ==============================================================================
-- CSIC Portal - Educational & Academic Synopsis Reference Schema (4 Modules)
-- NOTE FOR STUDENTS & EVALUATORS:
-- This file is an educational/learning reference schema directly mapping the 4
-- core modules from the academic synopsis (1 Module = 1 Table concept).
--
-- The live running application uses the 14-table ANSI SQL normalized schema
-- in database/migrations/ (001_simple_schema.sql to 006_search_information.sql).
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. STUDENT MODULE TABLE
-- Real Students from CSIC Project (Rashi, Vanshika, Silki, Akshit)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    branch VARCHAR(50) NOT NULL,
    year INT NOT NULL CHECK (year BETWEEN 1 AND 4),
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Real Values: Students registered in the CSIC system (Password: 1234)
INSERT INTO students (student_id, roll_no, name, branch, year, email, password_hash) VALUES
(1, 'CS2023001', 'Rashi', 'Computer Science & Engineering', 3, 'rashi@csic.edu', '$2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi'),
(2, 'CS2023002', 'Vanshika', 'Computer Science & Engineering', 3, 'vanshika@csic.edu', '$2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi'),
(3, 'CS2023003', 'Silki', 'Computer Science & Engineering', 3, 'silki@csic.edu', '$2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi'),
(4, 'CS2023004', 'Akshit', 'Computer Science & Engineering', 3, 'akshit@csic.edu', '$2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi');


-- ------------------------------------------------------------------------------
-- 2. ADMIN MODULE TABLE
-- Admin Account & College Institutional Details from CSIC
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    college_name VARCHAR(150) NOT NULL,
    college_code VARCHAR(50),
    contact_no VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Real Values: Admin account with college info (Password: 1234)
INSERT INTO admins (admin_id, name, email, password_hash, college_name, college_code, contact_no) VALUES
(1, 'Akshit', 'admin@csic.edu', '$2b$12$2FN9n7b/2zKhVQnyWm/BS.t5weH8ZRhLGLulvEJApBfszUES3cMwi', 'Cloud-Based Student Information College', 'CSIC-2026', '+91 98765 00001');


-- ------------------------------------------------------------------------------
-- 3. CHATBOT ENGINE MODULE TABLE
-- Real Chat Queries, Matched Intents, Bot Natural Language Answers,
-- and Forwarded Unresolved Queries to Admin
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS chatbot_queries (
    query_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    query_text TEXT NOT NULL,
    matched_intent VARCHAR(100),
    bot_response TEXT,
    is_answer_found BOOLEAN DEFAULT TRUE,
    forwarded_to_admin BOOLEAN DEFAULT FALSE,
    admin_reply TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- Real Values: Chatbot queries tested in CSIC
INSERT INTO chatbot_queries (query_id, student_id, query_text, matched_intent, bot_response, is_answer_found, forwarded_to_admin, admin_reply) VALUES
(1, 1, 'What is my attendance in Cloud Computing?', 'attendance', 'Your attendance in Cloud Computing & Distributed Systems (CS401) is 100.0% (6 attended out of 6 total sessions).', TRUE, FALSE, NULL),
(2, 4, 'Do I have any pending fee balance?', 'fees', 'All your fee dues for Semester 6 are fully cleared! Total paid: ₹65,000.00. Outstanding balance is ₹0.00.', TRUE, FALSE, NULL),
(3, 2, 'Show me Mid-Term exam datesheet', 'examination', 'Mid-Term Examination 2026 commences on March 10, 2026 with CS401 at 10:00 AM.', TRUE, FALSE, NULL),
(4, 3, 'When will campus placement drive for AWS begin?', 'placements', 'Information not found in database. Query forwarded to Admin.', FALSE, TRUE, 'AWS campus placement drive is scheduled for April 25-26, 2026. Register via student council.');


-- ------------------------------------------------------------------------------
-- 4. SEARCH INFORMATION MODULE TABLE
-- Searchable by: Branch, Year, Category (Syllabus, Timetable, Result, Fees, FAQ), and Subject
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS search_information (
    info_id INT AUTO_INCREMENT PRIMARY KEY,
    branch VARCHAR(50) NOT NULL,
    year INT NOT NULL CHECK (year BETWEEN 1 AND 4),
    category VARCHAR(50) NOT NULL,          -- Syllabus, Timetable, Results, Fees, FAQ
    subject VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content_details TEXT NOT NULL,
    file_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Real Values: Filterable academic information matching CSIC courses & notices
INSERT INTO search_information (info_id, branch, year, category, subject, title, content_details, file_url) VALUES
(1, 'Computer Science & Engineering', 3, 'Syllabus', 'Cloud Computing & Distributed Systems', 'CS401 Complete Course Syllabus & Lab Manual', 'Unit 1: Virtualization & Cloud Models, Unit 2: Storage & Networking, Unit 3: AWS/GCP Hands-on. 4 Credits.', '/docs/syllabus/cs401_syllabus.pdf'),
(2, 'Computer Science & Engineering', 3, 'Timetable', 'Advanced Database Engineering', 'CS402 Lecture and Lab Timing', 'Monday 10:15 - 11:15 AM (Lab-204), Wednesday 09:00 - 10:00 AM (Lab-204), Friday 10:15 - 11:15 AM.', '/docs/timetable/cse_sem6_tt.pdf'),
(3, 'Computer Science & Engineering', 3, 'Results', 'Machine Learning & AI', 'CS403 Mid-Term Result Summary', 'Exam Date: 15-Mar-2026. Max Marks: 50. Class Average: 43.5. Highest Score: 49.5 (Grade O).', '/docs/results/midterm_cs403.pdf'),
(4, 'Computer Science & Engineering', 3, 'Fees', 'Accounts Section', 'Semester 6 Academic & Specialization Lab Fee Details', 'Semester 6 Academic Tuition: ₹65,000.00 (Due: 30-Jan-2026). Lab Fee: ₹12,500.00 (Due: 28-Feb-2026).', '/docs/fees/sem6_structure.pdf'),
(5, 'Computer Science & Engineering', 3, 'FAQ', 'Academic Regulations', 'Minimum Attendance & Exam Hall Ticket Eligibility', 'Students must maintain minimum 75% aggregate attendance to appear in End-Term University Examinations.', '/docs/faq/attendance_rules.pdf');
