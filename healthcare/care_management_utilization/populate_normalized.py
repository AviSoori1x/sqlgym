#!/usr/bin/env python3
"""Populate care management utilization normalized schema."""
from __future__ import annotations
import argparse, sqlite3, random
from pathlib import Path

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    random.seed(0)
    conn=sqlite3.connect(args.db)
    members=[(i,f'Member{i}') for i in range(1,6)]
    conn.executemany('INSERT INTO members(id,name) VALUES (?,?)',members)
    programs=[(1,'Diabetes'),(2,'Asthma')]
    conn.executemany('INSERT INTO care_programs(id,name) VALUES (?,?)',programs)
    enrollments=[]; eid=1
    for m in members:
        for p_id in (1,2):
            enrollments.append((eid,m[0],p_id,f'2024-01-{m[0]:02d}')); eid+=1
    conn.executemany('INSERT INTO enrollments(id,member_id,program_id,enroll_date) VALUES (?,?,?,?)',enrollments)
    interventions=[]; iid=1
    for e in enrollments:
        interventions.append((iid,e[0],f'2024-02-{(e[0]%28)+1:02d}',['CALL','VISIT','EMAIL'][e[0]%3])); iid+=1
    conn.executemany('INSERT INTO interventions(id,enrollment_id,intervention_date,type) VALUES (?,?,?,?)',interventions)
    outcomes=[]; oid=1
    for iv in interventions:
        outcome='IMPROVED' if iv[0]%2==0 else 'NO_CHANGE'
        outcomes.append((oid,iv[0],outcome)); oid+=1
    conn.executemany('INSERT INTO outcomes(id,intervention_id,outcome) VALUES (?,?,?)',outcomes)
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
