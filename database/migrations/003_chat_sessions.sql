-- ==============================================================================
-- CSIC: Cloud-Based Student Information Chatbot
-- Migration 003: Multi-Session Chat & Context Memory
-- ANSI SQL Standard: Compatible with PostgreSQL 16+ and SQLite 3+
-- ==============================================================================

-- 1. CHAT_SESSIONS: Distinct conversation threads per user
CREATE TABLE IF NOT EXISTS chat_sessions (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. CHAT_MESSAGES: Individual turns belonging to a chat session
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

-- Indexes for fast session retrieval and timeline playback
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON chat_sessions(user_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id, created_at ASC);
