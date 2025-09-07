#!/usr/bin/env python3
"""Populate denormalized mart."""
from __future__ import annotations
import argparse, sqlite3
from pathlib import Path

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    conn=sqlite3.connect(args.db)
    norm_db=Path(__file__).with_name(Path(args.db).name.replace('_denormalized.db','_normalized.db'))
    conn.execute(f"ATTACH DATABASE '{norm_db}' AS norm")
    sql=Path(__file__).with_name('schema_denormalized.sql').read_text()
    sql=sql.replace('FROM ','FROM norm.').replace('JOIN ','JOIN norm.')
    conn.executescript(sql)
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
