#!/usr/bin/env python3
"""Populate telehealth scheduling sessions schema."""
from __future__ import annotations
import argparse, sqlite3, random
from pathlib import Path

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    random.seed(0)
    conn=sqlite3.connect(args.db)
    providers=[(1,'ProvA'),(2,'ProvB')]
    patients=[(i,f'Patient{i}') for i in range(1,6)]
    conn.executemany('INSERT INTO providers VALUES (?,?)',providers)
    conn.executemany('INSERT INTO patients VALUES (?,?)',patients)
    appts=[(i,providers[0][0],patients[i-1][0],f'2024-01-{i:02d}T10:00') for i in range(1,6)]
    conn.executemany('INSERT INTO appointments(id,provider_id,patient_id,appt_time) VALUES (?,?,?,?)',appts)
    sessions=[(i,appts[i-1][0],f'2024-01-{i:02d}T10:00','COMPLETED') for i in range(1,4)]
    conn.executemany('INSERT INTO sessions(id,appointment_id,start_time,status) VALUES (?,?,?,?)',sessions)
    feedback=[(i,sessions[i-1][0],5-i) for i in range(1,4)]
    conn.executemany('INSERT INTO feedback(id,session_id,rating) VALUES (?,?,?)',feedback)
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
