#!/usr/bin/env python3
"""Populate brokerage trading schema with synthetic data."""
from __future__ import annotations

import argparse
import sqlite3
import random


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    random.seed(args.seed)
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()

    instruments = [(i, f"SYM{i}", f"Instrument {i}", random.choice(["STOCK","BOND"]))
                   for i in range(1, 6)]
    cur.executemany("INSERT INTO instruments VALUES (?,?,?,?)", instruments)

    venues = [(i, f"VENUE{i}", f"Country {i}") for i in range(1, 3)]
    cur.executemany("INSERT INTO venues VALUES (?,?,?)", venues)

    orders = []
    for i in range(1, 21):
        instr = random.randint(1, 5)
        venue = random.randint(1, 2)
        side = random.choice(["BUY","SELL"])
        otype = random.choice(["MARKET","LIMIT"])
        status = random.choice(["OPEN","FILLED","CANCELLED"])
        qty = random.randint(1, 100)
        price = random.randint(10, 100)
        created = f"2024-01-{random.randint(1,5):02d}"
        orders.append((i, instr, venue, side, otype, status, qty, price, created))
    cur.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?)", orders)

    execs = []
    trade_id = 1
    trades = []
    for i in range(1, 41):
        order = random.randint(1, 20)
        time = f"2024-01-{random.randint(1,5):02d}"
        qty = random.randint(1, 50)
        price = random.randint(10, 100)
        execs.append((i, order, time, qty, price))
        instr = orders[order-1][1]
        trades.append((trade_id, i, instr, time, qty, price))
        trade_id += 1
    cur.executemany("INSERT INTO executions VALUES (?,?,?,?,?)", execs)
    cur.executemany("INSERT INTO trades VALUES (?,?,?,?,?,?)", trades)

    conn.commit()
    # Heavy indexes could be created after inserts in larger builds
    # cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_instr_time ON orders(instrument_id, created_at)")
    conn.close()


if __name__ == "__main__":
    main()

