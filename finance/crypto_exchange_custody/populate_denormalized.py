#!/usr/bin/env python3
"""Populate denormalized mart for crypto exchange custody."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")

    schema = Path(__file__).with_name("schema_denormalized.sql").read_text(encoding="utf-8")
    conn.executescript(schema)

    conn.execute(
        """
        INSERT INTO wallet_daily_balances
        SELECT wallet_id,
               substr(transfer_ts,1,10) AS balance_date,
               SUM(CASE WHEN direction='DEPOSIT' THEN amount_sats ELSE 0 END) AS deposits_sats,
               SUM(CASE WHEN direction='WITHDRAWAL' THEN amount_sats ELSE 0 END) AS withdrawals_sats
        FROM custody_transfers
        WHERE status='COMPLETED'
        GROUP BY wallet_id, balance_date;
        """
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
