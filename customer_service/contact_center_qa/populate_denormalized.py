#!/usr/bin/env python3
"""Populate denormalized table for contact center QA."""
from __future__ import annotations
import argparse, sqlite3
from pathlib import Path

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    conn=sqlite3.connect(args.db)
    conn.executescript(Path('schema_denormalized.sql').read_text())
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
