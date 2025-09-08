PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS facilities (
    id INTEGER PRIMARY KEY,
    facility_code TEXT NOT NULL UNIQUE,
    facility_name TEXT NOT NULL,
    facility_type TEXT NOT NULL CHECK(facility_type IN ('POWER_PLANT', 'MANUFACTURING', 'REFINERY', 'CHEMICAL_PLANT', 'STEEL_MILL', 'CEMENT_PLANT')),
    location TEXT NOT NULL,
    country TEXT NOT NULL,
    regulatory_jurisdiction TEXT NOT NULL,
    operational_start_date TEXT NOT NULL,
    annual_capacity REAL NOT NULL, -- Production capacity
    status TEXT NOT NULL CHECK(status IN ('OPERATIONAL', 'MAINTENANCE', 'DECOMMISSIONED'))
);

CREATE TABLE IF NOT EXISTS emission_sources (
    id INTEGER PRIMARY KEY,
    source_code TEXT NOT NULL UNIQUE,
    facility_id INTEGER NOT NULL REFERENCES facilities(id),
    source_name TEXT NOT NULL,
    source_type TEXT NOT NULL CHECK(source_type IN ('COMBUSTION', 'PROCESS', 'FUGITIVE', 'INDIRECT')),
    emission_category TEXT NOT NULL CHECK(emission_category IN ('SCOPE_1', 'SCOPE_2', 'SCOPE_3')),
    fuel_type TEXT CHECK(fuel_type IN ('NATURAL_GAS', 'COAL', 'OIL', 'BIOMASS', 'ELECTRICITY', 'STEAM')),
    equipment_description TEXT NOT NULL,
    installation_date TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS emission_factors (
    id INTEGER PRIMARY KEY,
    factor_code TEXT NOT NULL UNIQUE,
    emission_source_type TEXT NOT NULL,
    pollutant TEXT NOT NULL CHECK(pollutant IN ('CO2', 'CH4', 'N2O', 'NOX', 'SO2', 'PM25', 'VOC')),
    factor_value REAL NOT NULL, -- kg pollutant per unit activity
    factor_units TEXT NOT NULL,
    data_source TEXT NOT NULL,
    effective_date TEXT NOT NULL,
    expiry_date TEXT,
    uncertainty_percentage REAL,
    is_default BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS activity_data (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES emission_sources(id),
    reporting_period TEXT NOT NULL, -- YYYY-MM format
    activity_type TEXT NOT NULL CHECK(activity_type IN ('FUEL_CONSUMPTION', 'PRODUCTION_VOLUME', 'ELECTRICITY_USAGE', 'STEAM_CONSUMPTION')),
    activity_amount REAL NOT NULL,
    activity_units TEXT NOT NULL,
    data_quality TEXT NOT NULL CHECK(data_quality IN ('MEASURED', 'CALCULATED', 'ESTIMATED', 'DEFAULT')),
    measurement_method TEXT,
    data_source_reference TEXT,
    UNIQUE(source_id, reporting_period, activity_type)
);

CREATE TABLE IF NOT EXISTS emissions_calculations (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES emission_sources(id),
    activity_data_id INTEGER NOT NULL REFERENCES activity_data(id),
    factor_id INTEGER NOT NULL REFERENCES emission_factors(id),
    reporting_period TEXT NOT NULL,
    pollutant TEXT NOT NULL,
    emission_amount_kg REAL NOT NULL,
    co2_equivalent_kg REAL, -- For GHG calculations
    calculation_method TEXT NOT NULL,
    calculated_date TEXT NOT NULL,
    verified BOOLEAN NOT NULL DEFAULT 0,
    verification_date TEXT
);

CREATE TABLE IF NOT EXISTS regulatory_reports (
    id INTEGER PRIMARY KEY,
    report_id TEXT NOT NULL UNIQUE,
    facility_id INTEGER NOT NULL REFERENCES facilities(id),
    reporting_year INTEGER NOT NULL,
    report_type TEXT NOT NULL CHECK(report_type IN ('EPA_GHGRP', 'EU_ETS', 'STATE_INVENTORY', 'VOLUNTARY')),
    submission_date TEXT NOT NULL,
    total_co2_equivalent REAL NOT NULL,
    verification_status TEXT NOT NULL CHECK(verification_status IN ('DRAFT', 'SUBMITTED', 'VERIFIED', 'APPROVED')),
    verifier_name TEXT,
    certification_date TEXT
);

CREATE TABLE IF NOT EXISTS compliance_monitoring (
    id INTEGER PRIMARY KEY,
    facility_id INTEGER NOT NULL REFERENCES facilities(id),
    monitoring_date TEXT NOT NULL,
    regulation_type TEXT NOT NULL CHECK(regulation_type IN ('EMISSION_LIMIT', 'REPORTING_REQUIREMENT', 'PERMIT_CONDITION')),
    compliance_status TEXT NOT NULL CHECK(compliance_status IN ('COMPLIANT', 'NON_COMPLIANT', 'PENDING_REVIEW')),
    violation_description TEXT,
    corrective_action TEXT,
    due_date TEXT,
    responsible_person TEXT
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_facilities_type ON facilities(facility_type);
CREATE INDEX IF NOT EXISTS idx_facilities_country ON facilities(country);
CREATE INDEX IF NOT EXISTS idx_emission_sources_facility ON emission_sources(facility_id);
CREATE INDEX IF NOT EXISTS idx_emission_sources_category ON emission_sources(emission_category);
CREATE INDEX IF NOT EXISTS idx_emission_factors_pollutant ON emission_factors(pollutant);
CREATE INDEX IF NOT EXISTS idx_activity_data_source ON activity_data(source_id);
CREATE INDEX IF NOT EXISTS idx_activity_data_period ON activity_data(reporting_period);
CREATE INDEX IF NOT EXISTS idx_emissions_calculations_source ON emissions_calculations(source_id);
CREATE INDEX IF NOT EXISTS idx_emissions_calculations_period ON emissions_calculations(reporting_period);
CREATE INDEX IF NOT EXISTS idx_regulatory_reports_facility ON regulatory_reports(facility_id);
CREATE INDEX IF NOT EXISTS idx_compliance_monitoring_facility ON compliance_monitoring(facility_id);