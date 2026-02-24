-- Hobson: message history and approval tracking
-- Apply: psql -U hobson -d project_data -f 002_messages_approvals.sql

-- Message history for Telegram conversations
CREATE TABLE IF NOT EXISTS hobson.messages (
    id SERIAL PRIMARY KEY,
    chat_id TEXT NOT NULL,
    sender_name TEXT NOT NULL,
    content TEXT NOT NULL,
    is_from_hobson BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_chat_timestamp
    ON hobson.messages (chat_id, timestamp DESC);

-- Approval requests (replaces in-memory dict)
CREATE TABLE IF NOT EXISTS hobson.approvals (
    request_id TEXT PRIMARY KEY,
    action TEXT NOT NULL,
    reasoning TEXT,
    estimated_cost FLOAT DEFAULT 0,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);
