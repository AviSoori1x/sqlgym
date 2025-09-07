#!/usr/bin/env python3
"""Create denormalized fund positions mart."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import batch


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--source", default="asset_mgmt_fund_accounting_normalized.db")
    args = parser.parse_args()

    src = sqlite3.connect(args.source)
    dst = sqlite3.connect(args.db)
    dst.executescript(Path("schema_denormalized.sql").read_text())
    rows = src.execute(
        """
        SELECT f.id, f.name, s.symbol, h.quantity, h.position_date
        FROM holdings h
        JOIN funds f ON h.fund_id=f.id
        JOIN securities s ON h.security_id=s.id
        """
    ).fetchall()
    for chunk in batch(rows, 500):
        dst.executemany("INSERT INTO fund_positions VALUES (?,?,?,?,?)", chunk)
    dst.execute("CREATE INDEX idx_fp_date ON fund_positions(position_date, fund_id)")
    dst.execute("CREATE INDEX idx_fp_symbol ON fund_positions(security_symbol)")
    dst.commit()
    src.close()
    dst.close()


if __name__ == "__main__":
    main()
