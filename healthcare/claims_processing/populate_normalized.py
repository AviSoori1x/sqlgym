#!/usr/bin/env python3
"""Populate claims processing normalized schema."""
from __future__ import annotations
import argparse, sqlite3, random
from pathlib import Path

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    random.seed(0)
    conn=sqlite3.connect(args.db)
    patients=[(i,f'Patient{i}') for i in range(1,6)]
    plans=[(1,'PlanA'),(2,'PlanB')]
    conn.executemany('INSERT INTO patients VALUES (?,?)',patients)
    conn.executemany('INSERT INTO payer_plans VALUES (?,?)',plans)
    claims=[(i,patients[i-1][0],f'2024-01-0{i}',1,'OPEN' if i<3 else 'PAID') for i in range(1,6)]
    conn.executemany('INSERT INTO claims(id,patient_id,claim_date,plan_id,status) VALUES (?,?,?,?,?)',claims)
    lines=[]; lid=1
    for c in claims:
        lines.append((lid,c[0],'A',100)); lid+=1
        lines.append((lid,c[0],'B',50)); lid+=1
    conn.executemany('INSERT INTO claim_lines(id,claim_id,code,amount) VALUES (?,?,?,?)',lines)
    adjs=[(1,1,'2024-01-05','APPROVED'),(2,2,'2024-01-06','DENIED')]
    conn.executemany('INSERT INTO adjudications(id,claim_line_id,adjudicated_on,status) VALUES (?,?,?,?)',adjs)
    denials=[(1,5,'2024-01-07','No auth')]
    conn.executemany('INSERT INTO denials(id,claim_id,denial_date,reason) VALUES (?,?,?,?)',denials)
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
