PRAGMA foreign_keys=ON;
CREATE TABLE trade_facts (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    instrument_symbol TEXT NOT NULL,
    venue_name TEXT NOT NULL,
    side TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price NUMERIC NOT NULL,
    exec_time TEXT NOT NULL
);
CREATE INDEX idx_tf_instr_time ON trade_facts(instrument_symbol, exec_time);
