#!/usr/bin/env python3
"""Create denormalized summary table from normalized data."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--source", default="payments_acquiring_normalized.db")
    args = parser.parse_args()

    src = Path(args.source)
    conn_src = sqlite3.connect(src)
    conn_dst = sqlite3.connect(args.db)
    conn_dst.execute("PRAGMA foreign_keys=OFF")
    conn_dst.executescript(Path("schema_denormalized.sql").read_text())
    rows = conn_src.execute(
        """
        SELECT merchant_id, substr(txn_ts,1,10) as d,
               SUM(amount_cents) as gross,
               COALESCE(SUM(cb.amount_cents),0) as cb
        FROM card_transactions ct
        LEFT JOIN chargebacks cb ON ct.id=cb.card_transaction_id
        GROUP BY merchant_id, d
        """
    ).fetchall()
    conn_dst.executemany(
        "INSERT INTO merchant_txn_summary VALUES (?,?,?,?)",
        rows,
    )
    conn_dst.commit()
    conn_src.close()
    conn_dst.close()


if __name__ == "__main__":
    main()
