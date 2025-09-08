#!/usr/bin/env python3
"""Populate production line OEE normalized schema."""
from __future__ import annotations
import argparse, sqlite3
from pathlib import Path
SCALE_LINES=20
SCALE_RUNS=10000

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    conn=sqlite3.connect(args.db)
    conn.executescript(Path('schema_normalized.sql').read_text())
    # TODO populate
    conn.executescript('''
    CREATE INDEX idx_run_line_date ON line_runs(line_id, run_date);
    CREATE INDEX idx_down_run ON downtime_events(line_run_id);
    CREATE INDEX idx_ncr_run ON ncrs(line_run_id);
    ''')
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
