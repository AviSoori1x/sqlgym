#!/usr/bin/env python3
"""Generate normalized schema for brokerage trading."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common import ddl_validators as dv

DDL = """
PRAGMA foreign_keys=ON;
CREATE TABLE instruments (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('STOCK','BOND'))
);

CREATE TABLE venues (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    country TEXT NOT NULL
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    instrument_id INTEGER NOT NULL REFERENCES instruments(id),
    venue_id INTEGER NOT NULL REFERENCES venues(id),
    side TEXT NOT NULL CHECK(side IN ('BUY','SELL')),
    type TEXT NOT NULL CHECK(type IN ('MARKET','LIMIT')),
    status TEXT NOT NULL CHECK(status IN ('OPEN','FILLED','CANCELLED')),
    quantity INTEGER NOT NULL CHECK(quantity>0),
    price NUMERIC NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX idx_orders_instr_time ON orders(instrument_id, created_at);

CREATE TABLE executions (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    exec_time TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity>0),
    price NUMERIC NOT NULL
);
CREATE INDEX idx_exec_order ON executions(order_id);

CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    execution_id INTEGER NOT NULL REFERENCES executions(id),
    instrument_id INTEGER NOT NULL REFERENCES instruments(id),
    trade_time TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity>0),
    price NUMERIC NOT NULL
);
CREATE INDEX idx_trade_instr_time ON trades(instrument_id, trade_time);
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="schema_normalized.sql")
    parser.add_argument("--db")
    parser.add_argument("--echo", action="store_true")
    args = parser.parse_args()

    if args.echo:
        print(DDL)
    Path(args.out).write_text(DDL, encoding="utf-8")
    if args.db:
        conn = sqlite3.connect(args.db)
        dv.pragma_foreign_keys_on(conn)
        conn.executescript(DDL)
        conn.close()


if __name__ == "__main__":
    main()

