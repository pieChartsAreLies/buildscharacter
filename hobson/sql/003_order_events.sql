-- Order Guard: order event audit log
CREATE TABLE IF NOT EXISTS hobson.order_events (
    id SERIAL PRIMARY KEY,
    printful_order_id BIGINT NOT NULL,
    event_type TEXT NOT NULL,
    production_cost NUMERIC(10,2),
    retail_total NUMERIC(10,2),
    item_count INTEGER,
    rule_violated TEXT,
    raw_payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(printful_order_id, event_type)
);

CREATE INDEX IF NOT EXISTS idx_order_events_created_at
    ON hobson.order_events(created_at);
