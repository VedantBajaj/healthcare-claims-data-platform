CREATE SCHEMA IF NOT EXISTS audit;

CREATE TABLE IF NOT EXISTS audit.pipeline_run_log (
    audit_id BIGSERIAL PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    run_id TEXT NOT NULL,
    feed_date DATE,
    source_file_name TEXT,
    target_table TEXT,
    rows_loaded INTEGER,
    status TEXT NOT NULL,
    error_message TEXT,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);