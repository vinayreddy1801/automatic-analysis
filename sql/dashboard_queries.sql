-- 📊 Dashboard Queries for Looker Studio
-- Use these custom queries when connecting Supabase to Looker Studio.

-- Visual 1: Real-Time Yield (Last 1 Hour)
-- Calcuate pass/fail rate based on sensor thresholds (e.g., Temp < 500)
SELECT 
    COUNT(*) as total_units,
    SUM(CASE WHEN sensor_11_temp > 500 THEN 1 ELSE 0 END) as failed_units,
    SUM(CASE WHEN sensor_11_temp <= 500 THEN 1 ELSE 0 END) as passed_units,
    (SUM(CASE WHEN sensor_11_temp <= 500 THEN 1 ELSE 0 END)::FLOAT / COUNT(*)) * 100 as yield_percentage
FROM optimus_test_telemetry
WHERE timestamp >= NOW() - INTERVAL '1 hour';

-- Visual 2: Sensor Heatmap (Latest Reading per Unit)
-- Identify which bots are running hot right now.
SELECT DISTINCT ON (unit_id)
    unit_id,
    sensor_11_temp as motor_temp,
    sensor_12_pressure as pressure,
    timestamp
FROM optimus_test_telemetry
ORDER BY unit_id, timestamp DESC;

-- Visual 3: Pipeline Latency
-- Difference between "Event Time" (Cycle) and "Ingest Time" (DB Insert)
-- *Note: cycle_time is an int, so we assume a synthetic creation time for this demo*
SELECT 
    unit_id,
    timestamp as ingestion_time,
    EXTRACT(EPOCH FROM (NOW() - timestamp)) as latency_seconds
FROM optimus_test_telemetry
ORDER BY timestamp DESC
LIMIT 100;
