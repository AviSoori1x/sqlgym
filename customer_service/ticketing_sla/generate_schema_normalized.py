#!/usr/bin/env python3
"""Generate normalized schema for ticketing SLAs."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common import ddl_validators as dv

DDL = Path(__file__).with_name('schema_normalized.sql').read_text()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="schema_normalized.sql")
    parser.add_argument("--db")
    parser.add_argument("--echo", action="store_true")
    args = parser.parse_args()

    if args.echo:
        print(DDL)
    Path(args.out).write_text(DDL, encoding="utf-8")
    if args.db:
        conn = sqlite3.connect(args.db)
        dv.pragma_foreign_keys_on(conn)
        conn.executescript(DDL)
        conn.close()


if __name__ == "__main__":
    main()
