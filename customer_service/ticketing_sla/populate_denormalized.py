#!/usr/bin/env python3
"""Populate denormalized ticket daily counts."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--source", default="ticketing_sla_normalized.db")
    args = parser.parse_args()

    src = sqlite3.connect(args.source)
    dst = sqlite3.connect(args.db)
    dst.executescript(Path("schema_denormalized.sql").read_text())
    rows = src.execute(
        """
        SELECT substr(opened_at,1,10) day, status, COUNT(*)
        FROM tickets
        GROUP BY day, status
        """
    ).fetchall()
    dst.executemany("INSERT INTO ticket_daily_counts VALUES (?,?,?)", rows)
    dst.commit()
    src.close()
    dst.close()


if __name__ == "__main__":
    main()
