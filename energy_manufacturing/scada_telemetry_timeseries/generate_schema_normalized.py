#!/usr/bin/env python3
"""Generate normalized schema for SCADA telemetry timeseries."""
from __future__ import annotations
import argparse, sqlite3
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common import ddl_validators as dv
DDL=Path(__file__).with_name('schema_normalized.sql').read_text()

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--out',default='schema_normalized.sql'); p.add_argument('--db'); p.add_argument('--echo',action='store_true'); args=p.parse_args()
    if args.echo: print(DDL)
    Path(args.out).write_text(DDL)
    if args.db:
        conn=sqlite3.connect(args.db); dv.pragma_foreign_keys_on(conn); conn.executescript(DDL); conn.close()
if __name__=='__main__':
    main()
