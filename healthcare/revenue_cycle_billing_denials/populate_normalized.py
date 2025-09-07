#!/usr/bin/env python3
"""Populate revenue cycle billing and denials schema."""
from __future__ import annotations
import argparse, sqlite3, random
from pathlib import Path

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    random.seed(0)
    conn=sqlite3.connect(args.db)
    patients=[(i,f'Patient{i}') for i in range(1,4)]
    conn.executemany('INSERT INTO patients VALUES (?,?)',patients)
    bills=[(i,patients[i-1][0],f'2024-01-0{i}',100+i*50) for i in range(1,4)]
    conn.executemany('INSERT INTO bills(id,patient_id,bill_date,total) VALUES (?,?,?,?)',bills)
    items=[]; iid=1
    for b in bills:
        items.append((iid,b[0],'ServiceA',50)); iid+=1
        items.append((iid,b[0],'ServiceB',50)); iid+=1
    conn.executemany('INSERT INTO bill_items(id,bill_id,description,amount) VALUES (?,?,?,?)',items)
    pays=[(1,1,'2024-01-05',80),(2,2,'2024-01-06',60)]
    conn.executemany('INSERT INTO payments(id,bill_id,payment_date,amount) VALUES (?,?,?,?)',pays)
    denials=[(1,3,'2024-01-07','Missing info')]
    conn.executemany('INSERT INTO denials(id,bill_id,denial_date,reason) VALUES (?,?,?,?)',denials)
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
