PRAGMA foreign_keys=ON;
CREATE TABLE lines (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE line_runs (
    id INTEGER PRIMARY KEY,
    line_id INTEGER NOT NULL REFERENCES lines(id),
    run_date TEXT NOT NULL,
    planned_minutes INTEGER NOT NULL,
    good_units INTEGER NOT NULL,
    total_units INTEGER NOT NULL
);
CREATE INDEX idx_run_line_date ON line_runs(line_id, run_date);
CREATE TABLE downtime_events (
    id INTEGER PRIMARY KEY,
    line_run_id INTEGER NOT NULL REFERENCES line_runs(id),
    minutes INTEGER NOT NULL,
    reason TEXT NOT NULL CHECK(reason IN ('MAINT','BREAKDOWN','SETUP'))
);
CREATE INDEX idx_down_run ON downtime_events(line_run_id);
CREATE TABLE ncrs (
    id INTEGER PRIMARY KEY,
    line_run_id INTEGER NOT NULL REFERENCES line_runs(id),
    defect_count INTEGER NOT NULL
);
CREATE INDEX idx_ncr_run ON ncrs(line_run_id);
