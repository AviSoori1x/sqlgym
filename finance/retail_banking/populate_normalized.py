#!/usr/bin/env python3
"""Populate retail banking schema with synthetic deterministic data."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import get_rng, batch

CUSTOMERS = 5
ACCOUNTS = 10
TRANSACTIONS = 50


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")

    customers = [(i, f'Customer {i}', rng.choice(['LOW','MED','HIGH'])) for i in range(1, CUSTOMERS+1)]
    conn.executemany("INSERT INTO customers VALUES (?,?,?)", customers)

    branches = [(i, f'Branch {i}', f'City {i}') for i in range(1, 4)]
    conn.executemany("INSERT INTO branches VALUES (?,?,?)", branches)

    accounts = []
    for i in range(1, ACCOUNTS+1):
        cust = rng.randint(1, CUSTOMERS)
        branch = rng.randint(1, 3)
        acct_num = f'ACCT{i:06d}'
        acct_type = rng.choice(['CHECKING','SAVINGS'])
        opened = f"2024-01-{rng.randint(1,5):02d}"
        accounts.append((i, cust, branch, acct_num, acct_type, opened))
    conn.executemany("INSERT INTO accounts VALUES (?,?,?,?,?,?)", accounts)

    txns = []
    for i in range(1, TRANSACTIONS+1):
        acct = rng.randint(1, ACCOUNTS)
        date = f"2024-01-{rng.randint(1,5):02d}"
        amt = rng.randint(-50000, 50000)
        status = rng.choice(['PENDING','POSTED'])
        txns.append((i, acct, date, amt, status))
    for chunk in batch(txns, 500):
        conn.executemany("INSERT INTO transactions VALUES (?,?,?,?,?)", chunk)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
