#!/usr/bin/env python3
"""Populate denormalized daily sales table."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--source", default="pos_sales_returns_normalized.db")
    args = parser.parse_args()

    src = sqlite3.connect(args.source)
    dst = sqlite3.connect(args.db)
    dst.executescript(Path("schema_denormalized.sql").read_text())
    rows = src.execute(
        """
        SELECT o.store_id, substr(o.ordered_at,1,10) d,
               SUM(oi.quantity*p.price_cents) gross,
               COALESCE(SUM(r.quantity*p.price_cents),0) ret
        FROM orders o
        JOIN order_items oi ON o.id=oi.order_id
        JOIN products p ON oi.product_id=p.id
        LEFT JOIN (
            SELECT r.order_item_id, r.returned_at, oi.quantity
            FROM returns r JOIN order_items oi ON r.order_item_id=oi.id
        ) r ON r.order_item_id=oi.id
        GROUP BY o.store_id, d
        """
    ).fetchall()
    dst.executemany("INSERT INTO store_daily_sales VALUES (?,?,?,?)", rows)
    dst.commit()
    src.close()
    dst.close()


if __name__ == "__main__":
    main()
