#!/usr/bin/env python3
"""Populate contact center QA normalized schema."""
from __future__ import annotations
import argparse, sqlite3
from pathlib import Path
SCALE_CONVOS=1000
SCALE_TURNS=10000

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    conn=sqlite3.connect(args.db)
    conn.executescript(Path('schema_normalized.sql').read_text())
    # TODO populate with SCALE
    conn.executescript('''
    CREATE INDEX idx_turn_conv_time ON turns(conversation_id, ts);
    CREATE INDEX idx_res_conv ON resolutions(conversation_id);
    ''')
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
