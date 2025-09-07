#!/usr/bin/env python3
"""Build denormalized product_catalog from normalized tables."""
from __future__ import annotations
import argparse, sqlite3
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--db', required=True)
    p.add_argument('--source', default=str(Path(__file__).with_name('assortment_catalog_normalized.db')))
    args = p.parse_args()
    src = sqlite3.connect(args.source)
    dst = sqlite3.connect(args.db)
    dst.executescript("""
    DROP TABLE IF EXISTS product_catalog;
    CREATE TABLE product_catalog (
        product_id INTEGER PRIMARY KEY,
        sku TEXT NOT NULL,
        product_name TEXT NOT NULL,
        category_name TEXT NOT NULL,
        supplier_name TEXT NOT NULL,
        status TEXT NOT NULL,
        price_cents INTEGER NOT NULL
    );
    """)
    rows = src.execute(
        """
        SELECT p.id, p.sku, p.name, c.name, s.name, p.status, p.price_cents
        FROM products p
        JOIN categories c ON p.category_id=c.id
        JOIN suppliers s ON p.supplier_id=s.id
        """
    ).fetchall()
    dst.executemany("INSERT INTO product_catalog VALUES (?,?,?,?,?,?,?)", rows)
    dst.executescript("""
    CREATE INDEX idx_pc_category ON product_catalog(category_name);
    CREATE INDEX idx_pc_supplier ON product_catalog(supplier_name);
    """)
    dst.commit()
    src.close(); dst.close()


if __name__ == '__main__':
    main()
