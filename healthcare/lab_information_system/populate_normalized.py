#!/usr/bin/env python3
"""Populate lab information system schema."""
from __future__ import annotations
import argparse, sqlite3, random
from pathlib import Path

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    random.seed(0)
    conn=sqlite3.connect(args.db)
    patients=[(i,f'Patient{i}') for i in range(1,6)]
    tests=[(1,'CBC'),(2,'CMP')]
    conn.executemany('INSERT INTO patients VALUES (?,?)',patients)
    conn.executemany('INSERT INTO lab_tests VALUES (?,?)',tests)
    orders=[]; oid=1
    for p in patients:
        orders.append((oid,p[0],1,f'2024-01-{p[0]:02d}')); oid+=1
    conn.executemany('INSERT INTO lab_orders(id,patient_id,test_id,ordered_at) VALUES (?,?,?,?)',orders)
    specimens=[(i,o[0],f'2024-01-{i:02d}') for i,o in enumerate(orders,1)]
    conn.executemany('INSERT INTO specimens(id,order_id,collected_at) VALUES (?,?,?)',specimens)
    results=[]
    for s in specimens:
        results.append((s[0],s[0],f'{90+s[0]}',f'2024-01-{s[0]:02d}'))
    conn.executemany('INSERT INTO lab_results(id,specimen_id,result_value,result_date) VALUES (?,?,?,?)',results)
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
