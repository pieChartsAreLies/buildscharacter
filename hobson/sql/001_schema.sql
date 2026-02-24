-- Hobson schema for BuildsCharacter.com agent state management
-- Apply: psql -U postgres -d project_data -f 001_schema.sql

CREATE SCHEMA IF NOT EXISTS hobson;

-- Create hobson database user (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'hobson') THEN
        CREATE ROLE hobson WITH LOGIN PASSWORD '<from_bitwarden>';
    END IF;
END $$;

GRANT USAGE, CREATE ON SCHEMA hobson TO hobson;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA hobson TO hobson;
ALTER DEFAULT PRIVILEGES IN SCHEMA hobson GRANT ALL ON TABLES TO hobson;

-- Goals
CREATE TABLE IF NOT EXISTS hobson.goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quarter TEXT NOT NULL,
    objective TEXT NOT NULL,
    key_results JSONB NOT NULL DEFAULT '[]',
    progress DECIMAL(5,2) DEFAULT 0,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tasks
CREATE TABLE IF NOT EXISTS hobson.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'pending',
    due_date DATE,
    goal_id UUID REFERENCES hobson.goals(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Decisions
CREATE TABLE IF NOT EXISTS hobson.decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    outcome TEXT,
    category TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Metrics (daily snapshots)
CREATE TABLE IF NOT EXISTS hobson.metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    metric_type TEXT NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(date, metric_type)
);

-- Content inventory
CREATE TABLE IF NOT EXISTS hobson.content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content_type TEXT NOT NULL,
    status TEXT DEFAULT 'draft',
    slug TEXT,
    url TEXT,
    metadata JSONB DEFAULT '{}',
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Design inventory
CREATE TABLE IF NOT EXISTS hobson.designs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'concept',
    printful_product_id TEXT,
    image_url TEXT,
    performance JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Run log (immutable execution traces)
CREATE TABLE IF NOT EXISTS hobson.run_log (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'running',
    inputs JSONB DEFAULT '{}',
    outputs JSONB DEFAULT '{}',
    error TEXT,
    node_transitions JSONB DEFAULT '[]',
    cost_estimate DECIMAL(10,4) DEFAULT 0,
    llm_provider TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cost tracking
CREATE TABLE IF NOT EXISTS hobson.cost_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES hobson.run_log(run_id),
    provider TEXT NOT NULL,
    action TEXT NOT NULL,
    estimated_cost DECIMAL(10,4) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_run_log_workflow ON hobson.run_log(workflow);
CREATE INDEX IF NOT EXISTS idx_run_log_status ON hobson.run_log(status);
CREATE INDEX IF NOT EXISTS idx_run_log_started ON hobson.run_log(started_at);
CREATE INDEX IF NOT EXISTS idx_metrics_date ON hobson.metrics(date);
CREATE INDEX IF NOT EXISTS idx_content_status ON hobson.content(status);
CREATE INDEX IF NOT EXISTS idx_cost_log_created ON hobson.cost_log(created_at);
