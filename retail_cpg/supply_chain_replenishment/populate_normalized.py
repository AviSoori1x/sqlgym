#!/usr/bin/env python3
"""Populate supply chain replenishment normalized schema."""
from __future__ import annotations
import argparse, sqlite3
from pathlib import Path
SCALE_STORES=100
SCALE_SKUS=500

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    conn=sqlite3.connect(args.db)
    conn.executescript(Path('schema_normalized.sql').read_text())
    # TODO populate
    conn.executescript('''
    CREATE INDEX idx_stock_store_sku_date ON store_sku_stock(store_id, sku_id, date);
    CREATE INDEX idx_order_store_sku_date ON replen_orders(store_id, sku_id, order_date);
    ''')
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
