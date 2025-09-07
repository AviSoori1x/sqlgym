#!/usr/bin/env python3
"""Populate EHR encounters and orders normalized schema."""
from __future__ import annotations
import argparse, sqlite3
from pathlib import Path
SCALE_PATIENTS=500
SCALE_ORDERS=20000

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    conn=sqlite3.connect(args.db)
    conn.executescript(Path('schema_normalized.sql').read_text())
    # TODO populate
    conn.executescript('''
    CREATE INDEX idx_encounter_patient_date ON encounters(patient_id, encounter_date);
    CREATE INDEX idx_order_enc_time ON orders(encounter_id, order_time);
    CREATE INDEX idx_result_order_time ON results(order_id, result_time);
    ''')
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
