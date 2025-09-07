#!/usr/bin/env python3
"""Populate treasury risk normalized schema."""
from __future__ import annotations
import argparse, sqlite3
from pathlib import Path
SCALE_DESKS = 10
SCALE_EXPOSURES = 1000

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--db', required=True)
    args = p.parse_args()
    conn = sqlite3.connect(args.db)
    conn.executescript(Path('schema_normalized.sql').read_text())
    # TODO: populate tables with SCALE_* constants
    # heavy indexes created after bulk insert
    conn.executescript('''
    CREATE INDEX idx_exposure_asof_desk ON exposures(as_of, desk_id);
    CREATE INDEX idx_breach_limit_date ON breaches(limit_id, breached_on);
    ''')
    conn.commit()
    conn.close()
if __name__ == '__main__':
    main()
