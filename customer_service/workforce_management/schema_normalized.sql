PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY,
    employee_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    department TEXT NOT NULL CHECK(department IN ('SALES', 'SUPPORT', 'TECHNICAL', 'BILLING', 'RETENTION')),
    skill_level TEXT NOT NULL CHECK(skill_level IN ('JUNIOR', 'MID', 'SENIOR', 'LEAD', 'MANAGER')),
    employment_type TEXT NOT NULL CHECK(employment_type IN ('FULL_TIME', 'PART_TIME', 'CONTRACT')),
    hire_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'ON_LEAVE', 'TRAINING', 'TERMINATED'))
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL CHECK(category IN ('LANGUAGE', 'TECHNICAL', 'PRODUCT', 'SOFT_SKILL')),
    requires_certification BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS agent_skills (
    id INTEGER PRIMARY KEY,
    agent_id INTEGER NOT NULL REFERENCES agents(id),
    skill_id INTEGER NOT NULL REFERENCES skills(id),
    proficiency_level INTEGER NOT NULL CHECK(proficiency_level BETWEEN 1 AND 5),
    certified_date TEXT,
    expiry_date TEXT,
    UNIQUE(agent_id, skill_id)
);

CREATE TABLE IF NOT EXISTS shifts (
    id INTEGER PRIMARY KEY,
    shift_date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    shift_type TEXT NOT NULL CHECK(shift_type IN ('MORNING', 'AFTERNOON', 'EVENING', 'NIGHT', 'FLEXIBLE')),
    required_agents INTEGER NOT NULL,
    minimum_skill_level TEXT NOT NULL CHECK(minimum_skill_level IN ('JUNIOR', 'MID', 'SENIOR', 'LEAD', 'MANAGER'))
);

CREATE TABLE IF NOT EXISTS schedules (
    id INTEGER PRIMARY KEY,
    agent_id INTEGER NOT NULL REFERENCES agents(id),
    shift_id INTEGER NOT NULL REFERENCES shifts(id),
    status TEXT NOT NULL CHECK(status IN ('SCHEDULED', 'CONFIRMED', 'CHECKED_IN', 'COMPLETED', 'ABSENT', 'LATE')),
    check_in_time TEXT,
    check_out_time TEXT,
    break_minutes INTEGER DEFAULT 0,
    overtime_minutes INTEGER DEFAULT 0,
    UNIQUE(agent_id, shift_id)
);

CREATE TABLE IF NOT EXISTS time_off_requests (
    id INTEGER PRIMARY KEY,
    agent_id INTEGER NOT NULL REFERENCES agents(id),
    request_type TEXT NOT NULL CHECK(request_type IN ('VACATION', 'SICK', 'PERSONAL', 'BEREAVEMENT', 'JURY_DUTY')),
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED')),
    requested_at TEXT NOT NULL,
    approved_by INTEGER REFERENCES agents(id),
    notes TEXT
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_agents_department ON agents(department);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_agent_skills_agent ON agent_skills(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_skills_skill ON agent_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_shifts_date ON shifts(shift_date);
CREATE INDEX IF NOT EXISTS idx_schedules_agent_date ON schedules(agent_id, shift_id);
CREATE INDEX IF NOT EXISTS idx_schedules_shift ON schedules(shift_id);
CREATE INDEX IF NOT EXISTS idx_time_off_dates ON time_off_requests(start_date, end_date);