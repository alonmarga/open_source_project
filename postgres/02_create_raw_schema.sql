CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.sample_table (
    id SERIAL PRIMARY KEY,
    data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO raw.sample_table (data) VALUES
('Sample Row 1'),
('Sample Row 2'),
('Sample Row 3');