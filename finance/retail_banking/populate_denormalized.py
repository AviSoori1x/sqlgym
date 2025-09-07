#!/usr/bin/env python3
"""Populate denormalized daily balance table."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--source", default="retail_banking_normalized.db")
    args = parser.parse_args()

    src = sqlite3.connect(args.source)
    dst = sqlite3.connect(args.db)
    dst.executescript(Path("schema_denormalized.sql").read_text())
    rows = src.execute(
        """
        SELECT account_id, txn_date, SUM(amount_cents)
        FROM transactions
        GROUP BY account_id, txn_date
        """
    ).fetchall()
    dst.executemany("INSERT INTO account_daily_balances VALUES (?,?,?)", rows)
    dst.commit()
    src.close()
    dst.close()


if __name__ == "__main__":
    main()
