-- Exxon Carbon Tracking Denormalized Analytics
-- Trade-off: Pre-calculated emissions summaries and compliance metrics vs real-time accuracy
PRAGMA foreign_keys=OFF;

-- Facility emissions summary with annual totals
CREATE TABLE IF NOT EXISTS facility_emissions_summary (
    facility_id INTEGER PRIMARY KEY,
    facility_name TEXT NOT NULL,
    facility_type TEXT NOT NULL,
    regulatory_jurisdiction TEXT NOT NULL,
    annual_scope1_emissions REAL NOT NULL,
    annual_scope2_emissions REAL NOT NULL,
    annual_scope3_emissions REAL NOT NULL,
    total_annual_emissions REAL NOT NULL,
    emissions_intensity REAL NOT NULL,
    compliance_status TEXT NOT NULL,
    last_report_date TEXT NOT NULL,
    next_report_due TEXT NOT NULL,
    violations_count INTEGER NOT NULL,
    carbon_tax_liability REAL NOT NULL
);

-- Monthly emissions rollup by source type
CREATE TABLE IF NOT EXISTS monthly_emissions_rollup (
    id INTEGER PRIMARY KEY,
    facility_id INTEGER NOT NULL,
    year_month TEXT NOT NULL,
    source_type TEXT NOT NULL,
    total_emissions REAL NOT NULL,
    activity_volume REAL NOT NULL,
    emission_factor REAL NOT NULL,
    verification_status TEXT NOT NULL,
    UNIQUE(facility_id, year_month, source_type)
);

-- Analytical indexes
CREATE INDEX IF NOT EXISTS idx_facility_summary_type ON facility_emissions_summary(facility_type);
CREATE INDEX IF NOT EXISTS idx_facility_summary_jurisdiction ON facility_emissions_summary(regulatory_jurisdiction);
CREATE INDEX IF NOT EXISTS idx_monthly_rollup_facility ON monthly_emissions_rollup(facility_id);
CREATE INDEX IF NOT EXISTS idx_monthly_rollup_month ON monthly_emissions_rollup(year_month);
