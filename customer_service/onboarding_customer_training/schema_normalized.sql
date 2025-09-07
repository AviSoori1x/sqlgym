PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    company_size TEXT NOT NULL CHECK(company_size IN ('SMALL', 'MEDIUM', 'LARGE', 'ENTERPRISE')),
    industry TEXT NOT NULL,
    onboarding_tier TEXT NOT NULL CHECK(onboarding_tier IN ('SELF_SERVICE', 'STANDARD', 'PREMIUM', 'WHITE_GLOVE'))
);

CREATE TABLE IF NOT EXISTS training_programs (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    program_type TEXT NOT NULL CHECK(program_type IN ('ONBOARDING', 'FEATURE', 'CERTIFICATION', 'REFRESHER')),
    delivery_method TEXT NOT NULL CHECK(delivery_method IN ('SELF_PACED', 'INSTRUCTOR_LED', 'WEBINAR', 'ON_SITE')),
    duration_hours REAL NOT NULL,
    difficulty_level TEXT NOT NULL CHECK(difficulty_level IN ('BEGINNER', 'INTERMEDIATE', 'ADVANCED')),
    prerequisites TEXT, -- JSON array of program IDs
    is_mandatory BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    program_id INTEGER NOT NULL REFERENCES training_programs(id),
    enrolled_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    status TEXT NOT NULL CHECK(status IN ('ENROLLED', 'IN_PROGRESS', 'COMPLETED', 'DROPPED', 'EXPIRED')),
    progress_percentage INTEGER DEFAULT 0 CHECK(progress_percentage BETWEEN 0 AND 100),
    assigned_by TEXT,
    UNIQUE(customer_id, program_id)
);

CREATE TABLE IF NOT EXISTS modules (
    id INTEGER PRIMARY KEY,
    program_id INTEGER NOT NULL REFERENCES training_programs(id),
    sequence_number INTEGER NOT NULL,
    name TEXT NOT NULL,
    content_type TEXT NOT NULL CHECK(content_type IN ('VIDEO', 'DOCUMENT', 'QUIZ', 'EXERCISE', 'LIVE_SESSION')),
    duration_minutes INTEGER NOT NULL,
    passing_score INTEGER CHECK(passing_score BETWEEN 0 AND 100)
);

CREATE TABLE IF NOT EXISTS module_progress (
    id INTEGER PRIMARY KEY,
    enrollment_id INTEGER NOT NULL REFERENCES enrollments(id),
    module_id INTEGER NOT NULL REFERENCES modules(id),
    started_at TEXT NOT NULL,
    completed_at TEXT,
    score INTEGER CHECK(score BETWEEN 0 AND 100),
    attempts INTEGER NOT NULL DEFAULT 1,
    time_spent_minutes INTEGER,
    UNIQUE(enrollment_id, module_id)
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_customers_tier ON customers(onboarding_tier);
CREATE INDEX IF NOT EXISTS idx_programs_type ON training_programs(program_type);
CREATE INDEX IF NOT EXISTS idx_enrollments_customer ON enrollments(customer_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_status ON enrollments(status);
CREATE INDEX IF NOT EXISTS idx_enrollments_enrolled ON enrollments(enrolled_at);
CREATE INDEX IF NOT EXISTS idx_modules_program ON modules(program_id);
CREATE INDEX IF NOT EXISTS idx_module_progress_enrollment ON module_progress(enrollment_id);