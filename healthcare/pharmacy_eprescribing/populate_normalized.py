#!/usr/bin/env python3
"""Populate pharmacy e-prescribing schema."""
from __future__ import annotations
import argparse, sqlite3, random
from pathlib import Path

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    random.seed(0)
    conn=sqlite3.connect(args.db)
    patients=[(i,f'Patient{i}') for i in range(1,6)]
    meds=[(1,'DrugA'),(2,'DrugB')]
    pharmacies=[(1,'Pharm1','CA'),(2,'Pharm2','NY')]
    conn.executemany('INSERT INTO patients VALUES (?,?)',patients)
    conn.executemany('INSERT INTO medications VALUES (?,?)',meds)
    conn.executemany('INSERT INTO pharmacies VALUES (?,?,?)',pharmacies)
    rxs=[]; rxid=1
    for p in patients:
        rxs.append((rxid,p[0],1,f'2024-01-{p[0]:02d}',1)); rxid+=1
    conn.executemany('INSERT INTO prescriptions(id,patient_id,medication_id,written_date,pharmacy_id) VALUES (?,?,?,?,?)',rxs)
    fills=[(i,rxs[i-1][0],f'2024-01-{i:02d}','FILLED') for i in range(1,4)]
    conn.executemany('INSERT INTO fills(id,prescription_id,fill_date,status) VALUES (?,?,?,?)',fills)
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
