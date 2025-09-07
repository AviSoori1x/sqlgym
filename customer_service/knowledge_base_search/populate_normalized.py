#!/usr/bin/env python3
"""Populate knowledge base search normalized schema deterministically."""
from __future__ import annotations
import argparse, sqlite3
from pathlib import Path

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    conn=sqlite3.connect(args.db)
    conn.executescript(Path('schema_normalized.sql').read_text())
    conn.executemany('INSERT INTO kb_articles VALUES (?,?,?)', [
        (1,'Reset Password','steps to reset'),
        (2,'Update Profile','profile instructions'),
        (3,'Delete Account','how to delete')
    ])
    conn.executemany('INSERT INTO tags VALUES (?,?)', [
        (1,'account'), (2,'security')
    ])
    conn.executemany('INSERT INTO article_tags VALUES (?,?)', [
        (1,1),(1,2),(2,1)
    ])
    conn.executemany('INSERT INTO article_views VALUES (?,?,?)', [
        (1,1,'2024-01-01'),
        (2,1,'2024-01-02'),
        (3,2,'2024-01-03')
    ])
    conn.executemany('INSERT INTO feedback VALUES (?,?,?)', [
        (1,1,1),
        (2,1,0),
        (3,2,1)
    ])
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
