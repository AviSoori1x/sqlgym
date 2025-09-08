PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY,
    patient_id TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    preferred_device TEXT CHECK(preferred_device IN ('COMPUTER', 'TABLET', 'SMARTPHONE')),
    tech_comfort_level TEXT CHECK(tech_comfort_level IN ('LOW', 'MEDIUM', 'HIGH')),
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'INACTIVE'))
);

CREATE TABLE IF NOT EXISTS providers (
    id INTEGER PRIMARY KEY,
    provider_id TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    specialty TEXT NOT NULL,
    license_state TEXT NOT NULL,
    telehealth_certified BOOLEAN NOT NULL DEFAULT 0,
    platform_training_completed BOOLEAN NOT NULL DEFAULT 0,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'INACTIVE', 'TRAINING'))
);

CREATE TABLE IF NOT EXISTS telehealth_appointments (
    id INTEGER PRIMARY KEY,
    appointment_id TEXT NOT NULL UNIQUE,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    provider_id INTEGER NOT NULL REFERENCES providers(id),
    scheduled_datetime TEXT NOT NULL,
    appointment_type TEXT NOT NULL CHECK(appointment_type IN ('CONSULTATION', 'FOLLOW_UP', 'URGENT_CARE', 'MENTAL_HEALTH', 'SPECIALIST')),
    duration_minutes INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('SCHEDULED', 'CONFIRMED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'NO_SHOW')),
    cancellation_reason TEXT,
    reminder_sent BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS telehealth_sessions (
    id INTEGER PRIMARY KEY,
    appointment_id INTEGER NOT NULL REFERENCES telehealth_appointments(id),
    session_start_time TEXT NOT NULL,
    session_end_time TEXT,
    actual_duration_minutes INTEGER,
    connection_quality TEXT CHECK(connection_quality IN ('EXCELLENT', 'GOOD', 'FAIR', 'POOR')),
    audio_quality TEXT CHECK(audio_quality IN ('EXCELLENT', 'GOOD', 'FAIR', 'POOR')),
    video_quality TEXT CHECK(video_quality IN ('EXCELLENT', 'GOOD', 'FAIR', 'POOR')),
    technical_issues_count INTEGER NOT NULL DEFAULT 0,
    patient_satisfaction_score INTEGER CHECK(patient_satisfaction_score BETWEEN 1 AND 5),
    provider_notes TEXT,
    UNIQUE(appointment_id)
);

CREATE TABLE IF NOT EXISTS technical_issues (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES telehealth_sessions(id),
    issue_datetime TEXT NOT NULL,
    issue_type TEXT NOT NULL CHECK(issue_type IN ('CONNECTION', 'AUDIO', 'VIDEO', 'PLATFORM', 'DEVICE')),
    issue_description TEXT NOT NULL,
    resolution_time_minutes INTEGER,
    resolved_by TEXT,
    impact_level TEXT NOT NULL CHECK(impact_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
);

CREATE TABLE IF NOT EXISTS platform_usage (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES telehealth_sessions(id),
    feature_used TEXT NOT NULL CHECK(feature_used IN ('SCREEN_SHARE', 'CHAT', 'FILE_SHARE', 'WHITEBOARD', 'RECORDING')),
    usage_duration_seconds INTEGER NOT NULL,
    usage_datetime TEXT NOT NULL
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_patients_patient_id ON patients(patient_id);
CREATE INDEX IF NOT EXISTS idx_providers_specialty ON providers(specialty);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON telehealth_appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_provider ON telehealth_appointments(provider_id);
CREATE INDEX IF NOT EXISTS idx_appointments_datetime ON telehealth_appointments(scheduled_datetime);
CREATE INDEX IF NOT EXISTS idx_sessions_appointment ON telehealth_sessions(appointment_id);
CREATE INDEX IF NOT EXISTS idx_technical_issues_session ON technical_issues(session_id);
CREATE INDEX IF NOT EXISTS idx_platform_usage_session ON platform_usage(session_id);