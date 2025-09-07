#!/usr/bin/env python3
"""Populate denormalized daily averages for SCADA telemetry."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--db", required=True)
    p.add_argument("--source", default="scada_telemetry_timeseries_normalized.db")
    args = p.parse_args()

    src = sqlite3.connect(args.source)
    dst = sqlite3.connect(args.db)
    ddl_path = Path(__file__).with_name("schema_denormalized.sql")
    dst.executescript(ddl_path.read_text())
    rows = src.execute("""
        SELECT substr(reading_time,1,10) AS day, sensor_id, AVG(value)
        FROM readings
        GROUP BY day, sensor_id
        """).fetchall()
    dst.executemany("INSERT INTO sensor_daily_avg VALUES (?,?,?)", rows)
    dst.commit()
    src.close()
    dst.close()


if __name__ == "__main__":
    main()
