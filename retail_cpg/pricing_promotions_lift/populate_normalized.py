#!/usr/bin/env python3
"""Populate pricing promotions lift normalized schema."""
from __future__ import annotations
import argparse, sqlite3
from pathlib import Path
SCALE_PRODUCTS = 1000
SCALE_RECEIPTS = 50000

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--db', required=True)
    args = p.parse_args()
    conn = sqlite3.connect(args.db)
    conn.executescript(Path('schema_normalized.sql').read_text())
    # TODO: populate tables
    # create indexes after bulk insert
    conn.executescript('''
    CREATE INDEX idx_price_product ON price_books(product_id);
    CREATE INDEX idx_promo_prod_date ON promos(product_id, start_date);
    CREATE INDEX idx_receipt_prod_date ON receipts(product_id, sale_date);
    ''')
    conn.commit(); conn.close()
if __name__ == '__main__':
    main()
