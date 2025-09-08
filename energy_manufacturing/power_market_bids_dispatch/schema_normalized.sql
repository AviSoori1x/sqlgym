PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS power_plants (
    id INTEGER PRIMARY KEY,
    plant_code TEXT NOT NULL UNIQUE,
    plant_name TEXT NOT NULL,
    plant_type TEXT NOT NULL CHECK(plant_type IN ('COAL', 'NATURAL_GAS', 'NUCLEAR', 'HYDRO', 'WIND', 'SOLAR', 'BIOMASS')),
    capacity_mw REAL NOT NULL,
    location TEXT NOT NULL,
    market_zone TEXT NOT NULL,
    fuel_type TEXT NOT NULL,
    heat_rate REAL, -- BTU/kWh
    minimum_run_time_hours INTEGER,
    startup_cost REAL,
    status TEXT NOT NULL CHECK(status IN ('AVAILABLE', 'UNAVAILABLE', 'MAINTENANCE', 'DECOMMISSIONED'))
);

CREATE TABLE IF NOT EXISTS market_periods (
    id INTEGER PRIMARY KEY,
    trading_date TEXT NOT NULL,
    hour_ending INTEGER NOT NULL CHECK(hour_ending BETWEEN 1 AND 24),
    market_type TEXT NOT NULL CHECK(market_type IN ('DAY_AHEAD', 'REAL_TIME', 'ANCILLARY_SERVICES')),
    bid_deadline TEXT NOT NULL,
    settlement_deadline TEXT NOT NULL,
    UNIQUE(trading_date, hour_ending, market_type)
);

CREATE TABLE IF NOT EXISTS market_bids (
    id INTEGER PRIMARY KEY,
    bid_id TEXT NOT NULL UNIQUE,
    plant_id INTEGER NOT NULL REFERENCES power_plants(id),
    market_period_id INTEGER NOT NULL REFERENCES market_periods(id),
    bid_submission_time TEXT NOT NULL,
    bid_type TEXT NOT NULL CHECK(bid_type IN ('ENERGY', 'CAPACITY', 'ANCILLARY')),
    bid_price_per_mwh REAL NOT NULL,
    bid_quantity_mw REAL NOT NULL,
    minimum_load_mw REAL,
    startup_offer REAL,
    bid_status TEXT NOT NULL CHECK(bid_status IN ('SUBMITTED', 'ACCEPTED', 'REJECTED', 'CLEARED'))
);

CREATE TABLE IF NOT EXISTS dispatch_instructions (
    id INTEGER PRIMARY KEY,
    instruction_id TEXT NOT NULL UNIQUE,
    plant_id INTEGER NOT NULL REFERENCES power_plants(id),
    market_period_id INTEGER NOT NULL REFERENCES market_periods(id),
    dispatch_time TEXT NOT NULL,
    dispatch_mw REAL NOT NULL,
    clearing_price_per_mwh REAL NOT NULL,
    instruction_type TEXT NOT NULL CHECK(instruction_type IN ('ECONOMIC', 'RELIABILITY', 'EMERGENCY')),
    ramp_rate_mw_per_min REAL,
    status TEXT NOT NULL CHECK(status IN ('ISSUED', 'ACKNOWLEDGED', 'EXECUTING', 'COMPLETED'))
);

CREATE TABLE IF NOT EXISTS settlement_data (
    id INTEGER PRIMARY KEY,
    plant_id INTEGER NOT NULL REFERENCES power_plants(id),
    market_period_id INTEGER NOT NULL REFERENCES market_periods(id),
    actual_generation_mwh REAL NOT NULL,
    scheduled_generation_mwh REAL NOT NULL,
    energy_payment REAL NOT NULL,
    capacity_payment REAL,
    ancillary_payment REAL,
    imbalance_charges REAL DEFAULT 0,
    settlement_date TEXT NOT NULL,
    UNIQUE(plant_id, market_period_id)
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_power_plants_type ON power_plants(plant_type);
CREATE INDEX IF NOT EXISTS idx_power_plants_zone ON power_plants(market_zone);
CREATE INDEX IF NOT EXISTS idx_market_periods_date ON market_periods(trading_date);
CREATE INDEX IF NOT EXISTS idx_market_bids_plant ON market_bids(plant_id);
CREATE INDEX IF NOT EXISTS idx_market_bids_period ON market_bids(market_period_id);
CREATE INDEX IF NOT EXISTS idx_dispatch_instructions_plant ON dispatch_instructions(plant_id);
CREATE INDEX IF NOT EXISTS idx_settlement_data_plant ON settlement_data(plant_id);