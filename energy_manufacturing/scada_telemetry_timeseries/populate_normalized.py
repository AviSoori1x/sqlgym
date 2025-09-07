#!/usr/bin/env python3
"""Populate SCADA telemetry schema with synthetic data."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import get_rng

SITES = 2
SENSORS_PER_SITE = 3
READINGS_PER_SENSOR = 10


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")

    sites = [(i, f'Plant {i}') for i in range(1, SITES + 1)]
    conn.executemany("INSERT INTO sites VALUES (?,?)", sites)

    sensors = []
    sid = 1
    for site_id in range(1, SITES + 1):
        sensors.append((sid, site_id, f'Temp{site_id}', 'C', 'ACTIVE')); sid += 1
        sensors.append((sid, site_id, f'Pressure{site_id}', 'psi', 'ACTIVE')); sid += 1
        sensors.append((sid, site_id, f'Power{site_id}', 'kW', 'INACTIVE')); sid += 1
    conn.executemany("INSERT INTO sensors VALUES (?,?,?,?,?)", sensors)

    readings = []
    rid = 1
    for sensor_id, site_id, name, unit, status in sensors:
        for i in range(READINGS_PER_SENSOR):
            time = f"2024-01-{(i % 5) + 1:02d}T{(i % 24):02d}:00"
            if unit == 'C':
                value = rng.uniform(20, 80)
            elif unit == 'psi':
                value = rng.uniform(100, 450)
            else:
                value = rng.uniform(10, 90)
            quality = rng.choice(['GOOD', 'BAD'])
            readings.append((rid, sensor_id, time, round(value, 2), quality))
            rid += 1
    conn.executemany("INSERT INTO readings VALUES (?,?,?,?,?)", readings)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
