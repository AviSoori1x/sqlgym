#!/usr/bin/env python3
"""Generate normalized schema for assortment catalog."""
from __future__ import annotations
import argparse, sqlite3
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common import ddl_validators as dv
DDL = """
PRAGMA foreign_keys=ON;
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE','INACTIVE'))
);
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    sku TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
    status TEXT NOT NULL CHECK(status IN ('ACTIVE','DISCONTINUED')),
    price_cents INTEGER NOT NULL CHECK(price_cents>0)
);
CREATE TABLE product_attributes (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    attribute TEXT NOT NULL,
    value TEXT NOT NULL
);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_supplier ON products(supplier_id);
CREATE INDEX idx_attr_product ON product_attributes(product_id);
"""

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--out', default='schema_normalized.sql')
    p.add_argument('--db')
    p.add_argument('--echo', action='store_true')
    args = p.parse_args()
    if args.echo:
        print(DDL)
    Path(args.out).write_text(DDL, encoding='utf-8')
    if args.db:
        conn = sqlite3.connect(args.db)
        dv.pragma_foreign_keys_on(conn)
        conn.executescript(DDL)
        conn.close()
if __name__ == '__main__':
    main()
