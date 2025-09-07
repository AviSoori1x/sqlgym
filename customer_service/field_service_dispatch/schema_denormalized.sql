-- Denormalized field service dispatch analytics
-- Trade-off: Pre-calculated route metrics and utilization for real-time dispatch decisions vs storage
PRAGMA foreign_keys=OFF;

CREATE TABLE IF NOT EXISTS daily_technician_schedule (
    technician_id INTEGER NOT NULL,
    technician_name TEXT NOT NULL,
    schedule_date TEXT NOT NULL,
    total_appointments INTEGER NOT NULL,
    total_travel_km REAL NOT NULL,
    total_service_hours REAL NOT NULL,
    utilization_rate REAL NOT NULL,
    first_appointment_time TEXT,
    last_appointment_time TEXT,
    service_types TEXT, -- JSON array
    completion_rate REAL,
    avg_travel_between_stops REAL,
    PRIMARY KEY(technician_id, schedule_date)
);

CREATE TABLE IF NOT EXISTS service_metrics (
    date TEXT NOT NULL,
    request_type TEXT NOT NULL,
    total_requests INTEGER NOT NULL,
    scheduled_count INTEGER NOT NULL,
    completed_count INTEGER NOT NULL,
    cancelled_count INTEGER NOT NULL,
    avg_wait_time_hours REAL,
    avg_completion_time_hours REAL,
    on_time_rate REAL,
    first_time_fix_rate REAL,
    PRIMARY KEY(date, request_type)
);

CREATE TABLE IF NOT EXISTS geographic_demand (
    grid_latitude REAL NOT NULL,
    grid_longitude REAL NOT NULL,
    week_start TEXT NOT NULL,
    total_requests INTEGER NOT NULL,
    emergency_requests INTEGER NOT NULL,
    avg_response_time_hours REAL,
    nearest_tech_avg_distance_km REAL,
    underserved_score INTEGER, -- 1-10 scale
    PRIMARY KEY(grid_latitude, grid_longitude, week_start)
);

CREATE TABLE IF NOT EXISTS technician_performance (
    technician_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    jobs_completed INTEGER NOT NULL,
    jobs_assigned INTEGER NOT NULL,
    completion_rate REAL NOT NULL,
    avg_job_duration REAL,
    total_distance_traveled REAL,
    customer_ratings_avg REAL,
    on_time_arrival_rate REAL,
    skills_utilized TEXT, -- JSON object with skill:count
    revenue_generated INTEGER,
    PRIMARY KEY(technician_id, month)
);

-- Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_daily_schedule_date ON daily_technician_schedule(schedule_date);
CREATE INDEX IF NOT EXISTS idx_service_metrics_date ON service_metrics(date);
CREATE INDEX IF NOT EXISTS idx_geographic_week ON geographic_demand(week_start);
CREATE INDEX IF NOT EXISTS idx_tech_performance_month ON technician_performance(month);