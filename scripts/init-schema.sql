-- Create tables
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alert_rules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    query TEXT NOT NULL,
    condition VARCHAR(50) NOT NULL,
    threshold FLOAT NOT NULL,
    time_window INTEGER NOT NULL,
    services JSON,
    levels JSON,
    notification_channel VARCHAR(50) NOT NULL,
    notification_config JSON,
    is_active BOOLEAN DEFAULT TRUE,
    last_triggered TIMESTAMP,
    trigger_count INTEGER DEFAULT 0,
    owner_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS triggered_alerts (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER REFERENCES alert_rules(id),
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    value FLOAT NOT NULL,
    threshold FLOAT NOT NULL,
    log_count INTEGER,
    sample_logs JSON,
    status VARCHAR(20) DEFAULT 'triggered',
    acknowledged_at TIMESTAMP,
    acknowledged_by INTEGER REFERENCES users(id),
    resolved_at TIMESTAMP,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSON NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert admin user (password hash for "admin123")
INSERT INTO users (username, email, hashed_password, full_name, is_active, is_admin)
VALUES ('admin', 'admin@logflow.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lk3v8Z8qU8yK', 'System Administrator', TRUE, TRUE)
ON CONFLICT (username) DO NOTHING;

-- Insert system config
INSERT INTO system_config (key, value, description)
VALUES 
    ('alert_check_interval', '{"seconds": 60}', 'How often to check alert rules (in seconds)'),
    ('max_alerts_per_rule', '{"count": 100}', 'Maximum number of triggered alerts to keep per rule'),
    ('log_retention_days', '{"days": 30}', 'How long to keep logs in Elasticsearch')
ON CONFLICT (key) DO NOTHING;
