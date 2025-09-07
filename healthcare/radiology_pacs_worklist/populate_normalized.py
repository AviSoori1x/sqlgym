#!/usr/bin/env python3
"""Populate radiology PACS worklist schema."""
from __future__ import annotations
import argparse, sqlite3, random
from pathlib import Path

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    random.seed(0)
    conn=sqlite3.connect(args.db)
    patients=[(i,f'Patient{i}') for i in range(1,6)]
    rads=[(1,'RadA'),(2,'RadB')]
    conn.executemany('INSERT INTO patients VALUES (?,?)',patients)
    conn.executemany('INSERT INTO radiologists VALUES (?,?)',rads)
    studies=[(i,patients[i-1][0],f'2024-01-{i:02d}') for i in range(1,6)]
    conn.executemany('INSERT INTO studies(id,patient_id,study_date) VALUES (?,?,?)',studies)
    images=[(i,studies[(i-1)%5][0],'XRAY') for i in range(1,6)]
    conn.executemany('INSERT INTO images(id,study_id,modality) VALUES (?,?,?)',images)
    assigns=[(i,studies[i-1][0],1,f'2024-01-{i:02d}') for i in range(1,6)]
    conn.executemany('INSERT INTO assignments(id,study_id,radiologist_id,assigned_at) VALUES (?,?,?,?)',assigns)
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
