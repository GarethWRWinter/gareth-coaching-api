
-- schema.sql

CREATE TABLE IF NOT EXISTS rides (
    id SERIAL PRIMARY KEY,
    ride_id TEXT UNIQUE NOT NULL,
    start_time TIMESTAMP,
    duration_sec INTEGER,
    distance_km DOUBLE PRECISION,
    avg_power DOUBLE PRECISION,
    avg_hr DOUBLE PRECISION,
    avg_cadence DOUBLE PRECISION,
    max_power DOUBLE PRECISION,
    max_hr DOUBLE PRECISION,
    max_cadence DOUBLE PRECISION,
    total_work_kj DOUBLE PRECISION,
    tss DOUBLE PRECISION,
    left_right_balance TEXT,
    power_zone_times JSONB
);

CREATE INDEX IF NOT EXISTS idx_ride_id ON rides (ride_id);
