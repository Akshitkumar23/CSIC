-- ==============================================================================
-- CSIC Migration 004: Update Demo Student Names and Login Credentials
-- Updates demo student profiles (stu-001, stu-002, stu-003) to Rashi, Vanshika, Silki
-- Password: 1234 (bcrypt hash with cost 12)
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
