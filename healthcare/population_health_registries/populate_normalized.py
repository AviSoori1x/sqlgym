#!/usr/bin/env python3
"""Populate population health registries schema."""
from __future__ import annotations
import argparse, sqlite3, random
from pathlib import Path

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    random.seed(0)
    conn=sqlite3.connect(args.db)
    patients=[(i,f'Patient{i}') for i in range(1,6)]
    regs=[(1,'Diabetes'),(2,'Hypertension')]
    conn.executemany('INSERT INTO patients VALUES (?,?)',patients)
    conn.executemany('INSERT INTO registries VALUES (?,?)',regs)
    enroll=[]; eid=1
    for p in patients:
        enroll.append((eid,p[0],1,f'2024-01-{p[0]:02d}')); eid+=1
    conn.executemany('INSERT INTO enrollments(id,patient_id,registry_id,enroll_date) VALUES (?,?,?,?)',enroll)
    metrics=[(i,patients[i-1][0],f'2024-02-{i:02d}',0.5+i*0.1) for i in range(1,6)]
    conn.executemany('INSERT INTO metrics(id,patient_id,metric_date,metric_value) VALUES (?,?,?,?)',metrics)
    risks=[(i,patients[i-1][0],round(0.1*i,2)) for i in range(1,6)]
    conn.executemany('INSERT INTO risk_scores(id,patient_id,score) VALUES (?,?,?)',risks)
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
