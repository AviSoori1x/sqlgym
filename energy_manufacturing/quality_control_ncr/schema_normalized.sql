PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    product_code TEXT NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    product_family TEXT NOT NULL,
    specification_document TEXT,
    quality_standards TEXT, -- JSON array
    manufacturing_process TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'DISCONTINUED', 'UNDER_DEVELOPMENT'))
);

CREATE TABLE IF NOT EXISTS quality_tests (
    id INTEGER PRIMARY KEY,
    test_code TEXT NOT NULL UNIQUE,
    test_name TEXT NOT NULL,
    test_category TEXT NOT NULL CHECK(test_category IN ('DIMENSIONAL', 'MECHANICAL', 'ELECTRICAL', 'CHEMICAL', 'VISUAL')),
    test_method TEXT NOT NULL,
    acceptance_criteria TEXT NOT NULL,
    sampling_plan TEXT,
    is_mandatory BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS quality_inspections (
    id INTEGER PRIMARY KEY,
    inspection_id TEXT NOT NULL UNIQUE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    test_id INTEGER NOT NULL REFERENCES quality_tests(id),
    inspection_date TEXT NOT NULL,
    batch_lot_number TEXT NOT NULL,
    inspector_id TEXT NOT NULL,
    test_result_value TEXT,
    pass_fail TEXT NOT NULL CHECK(pass_fail IN ('PASS', 'FAIL', 'CONDITIONAL')),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS non_conformances (
    id INTEGER PRIMARY KEY,
    ncr_number TEXT NOT NULL UNIQUE,
    inspection_id INTEGER NOT NULL REFERENCES quality_inspections(id),
    detected_date TEXT NOT NULL,
    nonconformance_type TEXT NOT NULL CHECK(nonconformance_type IN ('MATERIAL_DEFECT', 'PROCESS_DEVIATION', 'SPECIFICATION_FAILURE', 'HANDLING_DAMAGE')),
    severity TEXT NOT NULL CHECK(severity IN ('MINOR', 'MAJOR', 'CRITICAL')),
    description TEXT NOT NULL,
    quantity_affected INTEGER NOT NULL,
    detected_by TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('OPEN', 'UNDER_INVESTIGATION', 'CORRECTIVE_ACTION', 'CLOSED'))
);

CREATE TABLE IF NOT EXISTS corrective_actions_qc (
    id INTEGER PRIMARY KEY,
    ncr_id INTEGER NOT NULL REFERENCES non_conformances(id),
    action_type TEXT NOT NULL CHECK(action_type IN ('REWORK', 'SCRAP', 'USE_AS_IS', 'RETURN_TO_SUPPLIER', 'PROCESS_IMPROVEMENT')),
    action_description TEXT NOT NULL,
    responsible_person TEXT NOT NULL,
    target_completion_date TEXT NOT NULL,
    actual_completion_date TEXT,
    effectiveness_verified BOOLEAN DEFAULT 0,
    status TEXT NOT NULL CHECK(status IN ('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'VERIFIED'))
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_products_family ON products(product_family);
CREATE INDEX IF NOT EXISTS idx_quality_inspections_product ON quality_inspections(product_id);
CREATE INDEX IF NOT EXISTS idx_quality_inspections_date ON quality_inspections(inspection_date);
CREATE INDEX IF NOT EXISTS idx_non_conformances_inspection ON non_conformances(inspection_id);
CREATE INDEX IF NOT EXISTS idx_non_conformances_severity ON non_conformances(severity);
CREATE INDEX IF NOT EXISTS idx_corrective_actions_ncr ON corrective_actions_qc(ncr_id);