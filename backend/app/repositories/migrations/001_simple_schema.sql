-- ==============================================================================
-- CSIC: Cloud-Based Student Information Chatbot
-- Simplified Relational Schema (11 Core Tables)
-- ANSI SQL Standard: Compatible with PostgreSQL 16+ and SQLite 3+
-- ==============================================================================

-- 1. USERS: Unified identity table for students, faculty, and administrators
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'faculty', 'admin')),
    phone VARCHAR(30),
    avatar_url VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. COURSES: Degree programs and departments
CREATE TABLE IF NOT EXISTS courses (
    id VARCHAR(64) PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    department VARCHAR(100) NOT NULL
);

-- 3. SUBJECTS: Curriculum subjects taught within courses
CREATE TABLE IF NOT EXISTS subjects (
    id VARCHAR(64) PRIMARY KEY,
    course_id VARCHAR(64) NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    credits NUMERIC(3,1) NOT NULL DEFAULT 4.0,
    semester INT NOT NULL CHECK (semester BETWEEN 1 AND 8),
    faculty_id VARCHAR(64) REFERENCES users(id) ON DELETE SET NULL
);

-- 4. ENROLLMENTS: Students registered in courses
CREATE TABLE IF NOT EXISTS enrollments (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id VARCHAR(64) NOT NULL REFERENCES courses(id) ON DELETE RESTRICT,
    roll_number VARCHAR(30) NOT NULL UNIQUE,
    semester INT NOT NULL DEFAULT 6,
    section VARCHAR(10) NOT NULL DEFAULT 'A',
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'dropped')),
    UNIQUE(user_id, course_id)
);

-- 5. ATTENDANCE_RECORDS: Class-by-class attendance logs
CREATE TABLE IF NOT EXISTS attendance_records (
    id VARCHAR(64) PRIMARY KEY,
    enrollment_id VARCHAR(64) NOT NULL REFERENCES enrollments(id) ON DELETE CASCADE,
    subject_id VARCHAR(64) NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    session_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('present', 'absent', 'excused')),
    remarks VARCHAR(255),
    UNIQUE(enrollment_id, subject_id, session_date)
);

-- 6. EXAMINATIONS: Scheduled assessment components
CREATE TABLE IF NOT EXISTS examinations (
    id VARCHAR(64) PRIMARY KEY,
    subject_id VARCHAR(64) NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    exam_date DATE NOT NULL,
    max_marks NUMERIC(5,2) NOT NULL CHECK (max_marks > 0),
    weightage_percentage NUMERIC(5,2) DEFAULT 30.0
);

-- 7. MARKS: Student grades and scores for examinations
CREATE TABLE IF NOT EXISTS marks (
    id VARCHAR(64) PRIMARY KEY,
    examination_id VARCHAR(64) NOT NULL REFERENCES examinations(id) ON DELETE CASCADE,
    enrollment_id VARCHAR(64) NOT NULL REFERENCES enrollments(id) ON DELETE CASCADE,
    marks_obtained NUMERIC(5,2) NOT NULL CHECK (marks_obtained >= 0),
    is_absent BOOLEAN NOT NULL DEFAULT FALSE,
    grade VARCHAR(5),
    UNIQUE(examination_id, enrollment_id)
);

-- 8. FEE_RECORDS: Financial ledger for student fee obligations
CREATE TABLE IF NOT EXISTS fee_records (
    id VARCHAR(64) PRIMARY KEY,
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    enrollment_id VARCHAR(64) NOT NULL REFERENCES enrollments(id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    amount NUMERIC(10,2) NOT NULL CHECK (amount > 0),
    amount_paid NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    due_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'unpaid' CHECK (status IN ('unpaid', 'partially_paid', 'paid'))
);

-- 9. TIMETABLE_ENTRIES: Weekly recurring lecture slots
CREATE TABLE IF NOT EXISTS timetable_entries (
    id VARCHAR(64) PRIMARY KEY,
    subject_id VARCHAR(64) NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    day_of_week VARCHAR(15) NOT NULL CHECK (day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')),
    start_time VARCHAR(10) NOT NULL,
    end_time VARCHAR(10) NOT NULL,
    room_number VARCHAR(50) NOT NULL
);

-- 10. NOTICES: Official university and departmental circulars
CREATE TABLE IF NOT EXISTS notices (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50) NOT NULL CHECK (category IN ('academic', 'examination', 'fees', 'event', 'urgent', 'administrative')),
    target_role VARCHAR(20) NOT NULL DEFAULT 'all' CHECK (target_role IN ('all', 'student', 'faculty')),
    published_by VARCHAR(64) REFERENCES users(id) ON DELETE SET NULL,
    is_published BOOLEAN NOT NULL DEFAULT TRUE,
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. CHAT_HISTORY: Conversational history and audit trail
CREATE TABLE IF NOT EXISTS chat_history (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    reply TEXT NOT NULL,
    intent VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Practical indexes for high-frequency queries
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_enrollments_user_id ON enrollments(user_id);
CREATE INDEX IF NOT EXISTS idx_attendance_enrollment ON attendance_records(enrollment_id, subject_id);
CREATE INDEX IF NOT EXISTS idx_marks_enrollment ON marks(enrollment_id);
CREATE INDEX IF NOT EXISTS idx_fee_enrollment ON fee_records(enrollment_id);
CREATE INDEX IF NOT EXISTS idx_timetable_day ON timetable_entries(day_of_week);
CREATE INDEX IF NOT EXISTS idx_notices_published ON notices(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_history_user ON chat_history(user_id, created_at DESC);
