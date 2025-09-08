PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS clinical_trials (
    id INTEGER PRIMARY KEY,
    trial_id TEXT NOT NULL UNIQUE,
    protocol_number TEXT NOT NULL,
    trial_title TEXT NOT NULL,
    phase TEXT NOT NULL CHECK(phase IN ('PHASE_I', 'PHASE_II', 'PHASE_III', 'PHASE_IV')),
    therapeutic_area TEXT NOT NULL,
    sponsor_name TEXT NOT NULL,
    start_date TEXT NOT NULL,
    planned_end_date TEXT,
    target_enrollment INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('PLANNING', 'ENROLLING', 'ACTIVE', 'COMPLETED', 'TERMINATED'))
);

CREATE TABLE IF NOT EXISTS trial_sites (
    id INTEGER PRIMARY KEY,
    site_id TEXT NOT NULL UNIQUE,
    trial_id INTEGER NOT NULL REFERENCES clinical_trials(id),
    site_name TEXT NOT NULL,
    principal_investigator TEXT NOT NULL,
    address TEXT NOT NULL,
    activation_date TEXT NOT NULL,
    target_enrollment INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'ACTIVE', 'SUSPENDED', 'CLOSED'))
);

CREATE TABLE IF NOT EXISTS trial_subjects (
    id INTEGER PRIMARY KEY,
    subject_id TEXT NOT NULL UNIQUE,
    trial_id INTEGER NOT NULL REFERENCES clinical_trials(id),
    site_id INTEGER NOT NULL REFERENCES trial_sites(id),
    screening_date TEXT NOT NULL,
    enrollment_date TEXT,
    randomization_date TEXT,
    treatment_arm TEXT,
    subject_status TEXT NOT NULL CHECK(subject_status IN ('SCREENING', 'ENROLLED', 'RANDOMIZED', 'ACTIVE', 'COMPLETED', 'WITHDRAWN', 'DISCONTINUED'))
);

CREATE TABLE IF NOT EXISTS site_visits (
    id INTEGER PRIMARY KEY,
    visit_id TEXT NOT NULL UNIQUE,
    subject_id INTEGER NOT NULL REFERENCES trial_subjects(id),
    visit_number INTEGER NOT NULL,
    visit_type TEXT NOT NULL CHECK(visit_type IN ('SCREENING', 'BASELINE', 'TREATMENT', 'FOLLOW_UP', 'END_OF_STUDY', 'UNSCHEDULED')),
    scheduled_date TEXT NOT NULL,
    actual_date TEXT,
    visit_window_start TEXT NOT NULL,
    visit_window_end TEXT NOT NULL,
    visit_status TEXT NOT NULL CHECK(visit_status IN ('SCHEDULED', 'COMPLETED', 'MISSED', 'RESCHEDULED')),
    protocol_deviations_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS adverse_events (
    id INTEGER PRIMARY KEY,
    ae_id TEXT NOT NULL UNIQUE,
    subject_id INTEGER NOT NULL REFERENCES trial_subjects(id),
    onset_date TEXT NOT NULL,
    resolution_date TEXT,
    event_term TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('MILD', 'MODERATE', 'SEVERE')),
    seriousness TEXT NOT NULL CHECK(seriousness IN ('NON_SERIOUS', 'SERIOUS')),
    causality TEXT NOT NULL CHECK(causality IN ('UNRELATED', 'UNLIKELY', 'POSSIBLE', 'PROBABLE', 'DEFINITE')),
    action_taken TEXT CHECK(action_taken IN ('NONE', 'DOSE_REDUCED', 'DOSE_INTERRUPTED', 'DRUG_WITHDRAWN')),
    outcome TEXT CHECK(outcome IN ('RECOVERED', 'RECOVERING', 'NOT_RECOVERED', 'FATAL', 'UNKNOWN')),
    reported_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS protocol_deviations (
    id INTEGER PRIMARY KEY,
    deviation_id TEXT NOT NULL UNIQUE,
    subject_id INTEGER NOT NULL REFERENCES trial_subjects(id),
    visit_id INTEGER REFERENCES site_visits(id),
    deviation_date TEXT NOT NULL,
    deviation_type TEXT NOT NULL CHECK(deviation_type IN ('INCLUSION_EXCLUSION', 'VISIT_WINDOW', 'PROCEDURE', 'MEDICATION', 'ASSESSMENT')),
    deviation_description TEXT NOT NULL,
    impact_assessment TEXT NOT NULL CHECK(impact_assessment IN ('MINOR', 'MAJOR')),
    corrective_action TEXT,
    reported_date TEXT NOT NULL
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_trial_sites_trial ON trial_sites(trial_id);
CREATE INDEX IF NOT EXISTS idx_trial_subjects_trial ON trial_subjects(trial_id);
CREATE INDEX IF NOT EXISTS idx_trial_subjects_site ON trial_subjects(site_id);
CREATE INDEX IF NOT EXISTS idx_site_visits_subject ON site_visits(subject_id);
CREATE INDEX IF NOT EXISTS idx_site_visits_date ON site_visits(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_adverse_events_subject ON adverse_events(subject_id);
CREATE INDEX IF NOT EXISTS idx_adverse_events_onset ON adverse_events(onset_date);
CREATE INDEX IF NOT EXISTS idx_protocol_deviations_subject ON protocol_deviations(subject_id);