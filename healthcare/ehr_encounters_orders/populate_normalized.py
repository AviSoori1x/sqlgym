#!/usr/bin/env python3
"""Populate EHR encounters and orders normalized schema."""
from __future__ import annotations
import argparse, sqlite3, random
from pathlib import Path

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    random.seed(0)
    conn=sqlite3.connect(args.db)
    patients=[(i,f'Patient{i}') for i in range(1,6)]
    conn.executemany('INSERT INTO patients VALUES (?,?)',patients)
    encounters=[(i,patients[i-1][0],f'2024-01-0{i}', 'INPATIENT' if i%2==0 else 'OUTPATIENT') for i in range(1,6)]
    conn.executemany('INSERT INTO encounters(id,patient_id,encounter_date,type) VALUES (?,?,?,?)',encounters)
    orders=[(i,encounters[i-1][0],f'2024-01-0{i}T08:00','PLACED') for i in range(1,6)]
    conn.executemany('INSERT INTO orders(id,encounter_id,order_time,status) VALUES (?,?,?,?)',orders)
    results=[(i,orders[i-1][0],f'2024-01-0{i}T09:00','FINAL') for i in range(1,6)]
    conn.executemany('INSERT INTO results(id,order_id,result_time,status) VALUES (?,?,?,?)',results)
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
