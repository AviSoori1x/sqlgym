PRAGMA foreign_keys=ON;
CREATE TABLE desks (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE scenarios (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE limits (
    id INTEGER PRIMARY KEY,
    desk_id INTEGER NOT NULL REFERENCES desks(id),
    limit_type TEXT NOT NULL CHECK(limit_type IN ('VAR','PNL')),
    amount NUMERIC(18,4) NOT NULL,
    window_days INTEGER NOT NULL CHECK(window_days>0),
    UNIQUE(desk_id, limit_type)
);
CREATE TABLE exposures (
    id INTEGER PRIMARY KEY,
    desk_id INTEGER NOT NULL REFERENCES desks(id),
    scenario_id INTEGER NOT NULL REFERENCES scenarios(id),
    as_of TEXT NOT NULL,
    amount NUMERIC(18,4) NOT NULL
);
CREATE INDEX idx_exposure_asof_desk ON exposures(as_of, desk_id);
CREATE TABLE breaches (
    id INTEGER PRIMARY KEY,
    limit_id INTEGER NOT NULL REFERENCES limits(id),
    exposure_id INTEGER NOT NULL REFERENCES exposures(id),
    breached_on TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('LOW','MEDIUM','HIGH'))
);
CREATE INDEX idx_breach_limit_date ON breaches(limit_id, breached_on);
