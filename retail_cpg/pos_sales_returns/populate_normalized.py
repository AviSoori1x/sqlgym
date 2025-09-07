#!/usr/bin/env python3
"""Populate POS sales and returns with deterministic synthetic data."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import get_rng, batch

STORES = 5
PRODUCTS = 20
ORDERS = 50


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")

    stores = [(i, f"Store {i}", 'OPEN', '2023-01-01') for i in range(1, STORES+1)]
    conn.executemany("INSERT INTO stores VALUES (?,?,?,?)", stores)

    products = [(i, f"SKU{i:05d}", f"Product {i}", rng.randint(100,10000)) for i in range(1, PRODUCTS+1)]
    conn.executemany("INSERT INTO products VALUES (?,?,?,?)", products)

    orders = []
    items = []
    returns = []
    order_id = 1
    item_id = 1
    ret_id = 1
    for _ in range(ORDERS):
        store = rng.randint(1, STORES)
        ordered_at = f"2024-01-{rng.randint(1,3):02d}T10:{rng.randint(0,59):02d}:00"
        status = rng.choice(['PLACED','SHIPPED'])
        orders.append((order_id, store, ordered_at, status))
        for _ in range(rng.randint(1,3)):
            prod = rng.randint(1, PRODUCTS)
            qty = rng.randint(1,5)
            items.append((item_id, order_id, prod, qty))
            if rng.random() < 0.1:
                ret_ts = f"2024-01-{rng.randint(1,3):02d}T12:00:00"
                returns.append((ret_id, item_id, ret_ts, rng.choice(['DEFECT','DISSATISFIED'])))
                ret_id += 1
            item_id += 1
        order_id += 1
    conn.executemany("INSERT INTO orders VALUES (?,?,?,?)", orders)
    for chunk in batch(items, 500):
        conn.executemany("INSERT INTO order_items VALUES (?,?,?,?)", chunk)
    if returns:
        conn.executemany("INSERT INTO returns VALUES (?,?,?,?)", returns)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
