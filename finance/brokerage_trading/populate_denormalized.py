#!/usr/bin/env python3
"""Create denormalized trade_facts table from normalized tables."""
from __future__ import annotations

import argparse
import sqlite3


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--source", default=None)
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()
    cur.executescript("""
DROP TABLE IF EXISTS trade_facts;
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
""")
    cur.execute(
        """
        INSERT INTO trade_facts (id, order_id, instrument_symbol, venue_name, side, quantity, price, exec_time)
        SELECT t.id, o.id, i.symbol, v.name, o.side, t.quantity, t.price, t.trade_time
        FROM trades t
        JOIN executions e ON t.execution_id=e.id
        JOIN orders o ON e.order_id=o.id
        JOIN instruments i ON o.instrument_id=i.id
        JOIN venues v ON o.venue_id=v.id
        """
    )
    conn.commit()
    # Heavy index build after insert
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tf_instr_time ON trade_facts(instrument_symbol, exec_time)")
    conn.close()


if __name__ == "__main__":
    main()

