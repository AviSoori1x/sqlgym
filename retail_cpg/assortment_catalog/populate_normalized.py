#!/usr/bin/env python3
"""Populate assortment catalog normalized tables with synthetic data."""
from __future__ import annotations
import argparse, sqlite3
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import get_rng

CATS = ["Beverages","Snacks","Household"]
SUPPLIERS = ["Acme Co","Globex","Soylent"]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--db', required=True)
    p.add_argument('--seed', type=int, default=0)
    args = p.parse_args()
    rng = get_rng(args.seed)
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")

    conn.executemany(
        "INSERT INTO categories VALUES (?,?)",
        [(i+1, name) for i, name in enumerate(CATS)]
    )
    conn.executemany(
        "INSERT INTO suppliers VALUES (?,?,?)",
        [(i+1, name, rng.choice(['ACTIVE','INACTIVE'])) for i, name in enumerate(SUPPLIERS)]
    )
    products = []
    attrs = []
    pid = 1
    for cat_id in range(1, len(CATS)+1):
        for _ in range(3):
            sup_id = rng.randint(1, len(SUPPLIERS))
            status = rng.choice(['ACTIVE','DISCONTINUED'])
            price = rng.randint(100, 1000)
            sku = f"SKU{pid:04d}"
            name = f"Product {pid}"
            products.append((pid, sku, name, cat_id, sup_id, status, price))
            attrs.append((len(attrs)+1, pid, 'color', rng.choice(['red','blue','green'])))
            attrs.append((len(attrs)+1, pid, 'size', rng.choice(['S','M','L'])))
            pid += 1
    conn.executemany("INSERT INTO products VALUES (?,?,?,?,?,?,?)", products)
    conn.executemany("INSERT INTO product_attributes VALUES (?,?,?,?)", attrs)
    conn.commit(); conn.close()


if __name__ == '__main__':
    main()
