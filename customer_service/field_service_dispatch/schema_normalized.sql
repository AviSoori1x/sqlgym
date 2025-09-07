PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    service_level TEXT NOT NULL CHECK(service_level IN ('STANDARD', 'PRIORITY', 'VIP'))
);

CREATE TABLE IF NOT EXISTS technicians (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    skill_set TEXT NOT NULL, -- JSON array of skills
    certification_level TEXT NOT NULL CHECK(certification_level IN ('APPRENTICE', 'JOURNEYMAN', 'MASTER')),
    home_latitude REAL NOT NULL,
    home_longitude REAL NOT NULL,
    max_daily_jobs INTEGER NOT NULL DEFAULT 8,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'ON_LEAVE', 'TERMINATED'))
);

CREATE TABLE IF NOT EXISTS service_requests (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    request_type TEXT NOT NULL CHECK(request_type IN ('INSTALL', 'REPAIR', 'MAINTENANCE', 'INSPECTION', 'EMERGENCY')),
    priority TEXT NOT NULL CHECK(priority IN ('LOW', 'MEDIUM', 'HIGH', 'EMERGENCY')),
    skills_required TEXT NOT NULL, -- JSON array
    estimated_duration_hours REAL NOT NULL,
    created_at TEXT NOT NULL,
    requested_date TEXT NOT NULL,
    time_window TEXT NOT NULL CHECK(time_window IN ('MORNING', 'AFTERNOON', 'EVENING', 'ANYTIME')),
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'))
);

CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY,
    service_request_id INTEGER NOT NULL REFERENCES service_requests(id),
    technician_id INTEGER NOT NULL REFERENCES technicians(id),
    scheduled_date TEXT NOT NULL,
    scheduled_start_time TEXT NOT NULL,
    scheduled_end_time TEXT NOT NULL,
    actual_start_time TEXT,
    actual_end_time TEXT,
    travel_distance_km REAL,
    status TEXT NOT NULL CHECK(status IN ('SCHEDULED', 'EN_ROUTE', 'ON_SITE', 'COMPLETED', 'MISSED', 'RESCHEDULED')),
    UNIQUE(service_request_id)
);

CREATE TABLE IF NOT EXISTS dispatch_events (
    id INTEGER PRIMARY KEY,
    appointment_id INTEGER NOT NULL REFERENCES appointments(id),
    event_type TEXT NOT NULL CHECK(event_type IN ('ASSIGNED', 'REASSIGNED', 'STARTED_TRAVEL', 'ARRIVED', 'COMPLETED', 'CUSTOMER_NOT_HOME', 'RESCHEDULED')),
    event_timestamp TEXT NOT NULL,
    notes TEXT,
    location_latitude REAL,
    location_longitude REAL
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_customers_location ON customers(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_technicians_status ON technicians(status);
CREATE INDEX IF NOT EXISTS idx_service_requests_status ON service_requests(status);
CREATE INDEX IF NOT EXISTS idx_service_requests_date ON service_requests(requested_date);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_appointments_technician ON appointments(technician_id, scheduled_date);
CREATE INDEX IF NOT EXISTS idx_dispatch_events_appointment ON dispatch_events(appointment_id);