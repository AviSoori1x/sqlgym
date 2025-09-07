#!/usr/bin/env python3
"""Populate clinical trials site visits schema."""
from __future__ import annotations
import argparse, sqlite3, random
from pathlib import Path

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    random.seed(0)
    conn=sqlite3.connect(args.db)
    subjects=[(i,f'Subject{i}') for i in range(1,6)]
    trials=[(1,'TrialA'),(2,'TrialB')]
    investigators=[(1,'Dr. Alpha'),(2,'Dr. Beta'),(3,'Dr. Gamma')]
    conn.executemany('INSERT INTO subjects VALUES (?,?)',subjects)
    conn.executemany('INSERT INTO trials VALUES (?,?)',trials)
    conn.executemany('INSERT INTO investigators VALUES (?,?)',investigators)
    visits=[]; vid=1
    for s in subjects:
        visits.append((vid,s[0],1,1,f'2024-01-{s[0]:02d}')); vid+=1
        visits.append((vid,s[0],2,2,f'2024-02-{s[0]:02d}')); vid+=1
    conn.executemany('INSERT INTO site_visits(id,subject_id,trial_id,investigator_id,visit_date) VALUES (?,?,?,?,?)',visits)
    aes=[]; aeid=1
    for v in visits[::2]:
        aes.append((aeid,v[0],'Headache','MILD')); aeid+=1
    conn.executemany('INSERT INTO adverse_events(id,visit_id,description,severity) VALUES (?,?,?,?)',aes)
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
