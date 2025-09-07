#!/usr/bin/env python3
"""Generate normalized schema for asset management fund accounting."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common import ddl_validators as dv

DDL = """
PRAGMA foreign_keys=ON;
CREATE TABLE funds (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    domicile TEXT NOT NULL CHECK(domicile IN ('US','EU','APAC')),
    status TEXT NOT NULL CHECK(status IN ('ACTIVE','INACTIVE'))
);
CREATE TABLE investors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    tier TEXT NOT NULL CHECK(tier IN ('RETAIL','INSTITUTIONAL')),
    risk_profile TEXT NOT NULL CHECK(risk_profile IN ('LOW','MED','HIGH'))
);
CREATE TABLE securities (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL CHECK(type IN ('EQUITY','BOND','CASH')),
    currency TEXT NOT NULL CHECK(currency IN ('USD','EUR','JPY'))
);
CREATE TABLE holdings (
    id INTEGER PRIMARY KEY,
    fund_id INTEGER NOT NULL REFERENCES funds(id),
    security_id INTEGER NOT NULL REFERENCES securities(id),
    quantity INTEGER NOT NULL CHECK(quantity>0),
    position_date TEXT NOT NULL
);
CREATE TABLE subscriptions (
    id INTEGER PRIMARY KEY,
    fund_id INTEGER NOT NULL REFERENCES funds(id),
    investor_id INTEGER NOT NULL REFERENCES investors(id),
    subscribed_at TEXT NOT NULL
);
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
