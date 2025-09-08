PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY,
    patient_id TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    gender TEXT CHECK(gender IN ('M', 'F', 'OTHER')),
    medical_record_number TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'INACTIVE', 'DECEASED'))
);

CREATE TABLE IF NOT EXISTS radiologists (
    id INTEGER PRIMARY KEY,
    radiologist_id TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    subspecialty TEXT NOT NULL CHECK(subspecialty IN ('GENERAL', 'NEURO', 'CARDIAC', 'MUSCULOSKELETAL', 'ABDOMINAL', 'CHEST', 'INTERVENTIONAL')),
    license_number TEXT NOT NULL,
    shift_preference TEXT CHECK(shift_preference IN ('DAY', 'EVENING', 'NIGHT', 'ANY')),
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'INACTIVE', 'ON_CALL', 'UNAVAILABLE'))
);

CREATE TABLE IF NOT EXISTS imaging_studies (
    id INTEGER PRIMARY KEY,
    accession_number TEXT NOT NULL UNIQUE,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    study_datetime TEXT NOT NULL,
    modality TEXT NOT NULL CHECK(modality IN ('CT', 'MRI', 'XRAY', 'ULTRASOUND', 'MAMMOGRAPHY', 'NUCLEAR', 'PET')),
    body_part TEXT NOT NULL,
    study_description TEXT NOT NULL,
    ordering_provider TEXT NOT NULL,
    clinical_indication TEXT,
    contrast_used BOOLEAN NOT NULL DEFAULT 0,
    study_status TEXT NOT NULL CHECK(study_status IN ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
    priority TEXT NOT NULL CHECK(priority IN ('ROUTINE', 'URGENT', 'STAT'))
);

CREATE TABLE IF NOT EXISTS study_images (
    id INTEGER PRIMARY KEY,
    study_id INTEGER NOT NULL REFERENCES imaging_studies(id),
    image_number INTEGER NOT NULL,
    image_type TEXT NOT NULL CHECK(image_type IN ('SCOUT', 'AXIAL', 'CORONAL', 'SAGITTAL', 'RECONSTRUCTION')),
    acquisition_datetime TEXT NOT NULL,
    image_quality TEXT CHECK(image_quality IN ('EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'NON_DIAGNOSTIC')),
    file_size_mb REAL NOT NULL,
    UNIQUE(study_id, image_number)
);

CREATE TABLE IF NOT EXISTS worklist_assignments (
    id INTEGER PRIMARY KEY,
    study_id INTEGER NOT NULL REFERENCES imaging_studies(id),
    radiologist_id INTEGER NOT NULL REFERENCES radiologists(id),
    assignment_datetime TEXT NOT NULL,
    assignment_type TEXT NOT NULL CHECK(assignment_type IN ('PRIMARY', 'SECONDARY', 'CONSULTATION', 'OVERRIDE')),
    assignment_priority INTEGER NOT NULL DEFAULT 1,
    estimated_read_time_minutes INTEGER,
    status TEXT NOT NULL CHECK(status IN ('ASSIGNED', 'ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'REASSIGNED')),
    UNIQUE(study_id, radiologist_id, assignment_type)
);

CREATE TABLE IF NOT EXISTS radiology_reports (
    id INTEGER PRIMARY KEY,
    study_id INTEGER NOT NULL REFERENCES imaging_studies(id),
    radiologist_id INTEGER NOT NULL REFERENCES radiologists(id),
    report_datetime TEXT NOT NULL,
    findings TEXT NOT NULL,
    impression TEXT NOT NULL,
    recommendations TEXT,
    report_status TEXT NOT NULL CHECK(report_status IN ('PRELIMINARY', 'FINAL', 'ADDENDUM', 'CORRECTED')),
    dictation_time_minutes REAL,
    critical_finding BOOLEAN NOT NULL DEFAULT 0,
    UNIQUE(study_id)
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_patients_mrn ON patients(medical_record_number);
CREATE INDEX IF NOT EXISTS idx_radiologists_subspecialty ON radiologists(subspecialty);
CREATE INDEX IF NOT EXISTS idx_imaging_studies_patient ON imaging_studies(patient_id);
CREATE INDEX IF NOT EXISTS idx_imaging_studies_datetime ON imaging_studies(study_datetime);
CREATE INDEX IF NOT EXISTS idx_imaging_studies_modality ON imaging_studies(modality);
CREATE INDEX IF NOT EXISTS idx_study_images_study ON study_images(study_id);
CREATE INDEX IF NOT EXISTS idx_worklist_assignments_radiologist ON worklist_assignments(radiologist_id);
CREATE INDEX IF NOT EXISTS idx_worklist_assignments_study ON worklist_assignments(study_id);
CREATE INDEX IF NOT EXISTS idx_radiology_reports_study ON radiology_reports(study_id);
CREATE INDEX IF NOT EXISTS idx_radiology_reports_radiologist ON radiology_reports(radiologist_id);