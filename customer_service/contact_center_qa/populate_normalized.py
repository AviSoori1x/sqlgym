#!/usr/bin/env python3
"""Populate contact center QA normalized schema deterministically."""
from __future__ import annotations
import argparse, sqlite3
from pathlib import Path

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    conn=sqlite3.connect(args.db)
    conn.executescript(Path('schema_normalized.sql').read_text())
    conn.executemany('INSERT INTO conversations VALUES (?,?,?)', [
        (1, 100, '2024-01-01T09:00:00',),
        (2, 101, '2024-01-02T10:00:00',),
        (3, 102, '2024-01-03T11:00:00',)
    ])
    conn.executemany('INSERT INTO intents VALUES (?,?)', [
        (1,'GREETING'), (2,'QUESTION'), (3,'CLOSING')
    ])
    conn.executemany('INSERT INTO turns VALUES (?,?,?,?,?,?)', [
        (1,1,'AGENT',1,'Hello, how can I help?','2024-01-01T09:00:05'),
        (2,1,'CUSTOMER',2,'I have an issue.','2024-01-01T09:00:10'),
        (3,2,'AGENT',1,'Welcome!','2024-01-02T10:00:05'),
        (4,2,'CUSTOMER',2,'Need assistance.','2024-01-02T10:00:15'),
        (5,3,'AGENT',1,'Hi there','2024-01-03T11:00:05')
    ])
    conn.executemany('INSERT INTO resolutions VALUES (?,?,?,?)', [
        (1,1,1,'2024-01-01T09:05:00'),
        (2,2,0,NULL)
    ])
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
