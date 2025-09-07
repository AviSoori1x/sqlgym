#!/usr/bin/env python3
"""Populate claims processing normalized schema."""
from __future__ import annotations
import argparse, sqlite3
from pathlib import Path
SCALE_PATIENTS=1000
SCALE_CLAIMS=20000

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    conn=sqlite3.connect(args.db)
    conn.executescript(Path('schema_normalized.sql').read_text())
    # TODO populate
    conn.executescript('''
    CREATE INDEX idx_claim_plan_date ON claims(plan_id, claim_date);
    CREATE INDEX idx_lines_claim ON claim_lines(claim_id);
    CREATE INDEX idx_adj_line ON adjudications(claim_line_id);
    CREATE INDEX idx_denial_claim_date ON denials(claim_id, denial_date);
    ''')
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
