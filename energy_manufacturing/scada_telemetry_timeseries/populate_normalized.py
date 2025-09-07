#!/usr/bin/env python3
"""Populate SCADA telemetry normalized schema."""
from __future__ import annotations
import argparse, sqlite3
from pathlib import Path
SCALE_ASSETS=50
SCALE_READINGS=500000

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    conn=sqlite3.connect(args.db)
    conn.executescript(Path('schema_normalized.sql').read_text())
    # TODO populate
    conn.executescript('''
    CREATE INDEX idx_sensor_asset ON sensors(asset_id);
    CREATE INDEX idx_reading_sensor_time ON readings(sensor_id, reading_time);
    ''')
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
