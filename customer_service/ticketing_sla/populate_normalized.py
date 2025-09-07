#!/usr/bin/env python3
"""Populate ticketing SLA schema with synthetic data."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import get_rng, batch

CUSTOMERS = 5
AGENTS = 3
TICKETS = 20


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")

    customers = [(i, f'Customer {i}') for i in range(1, CUSTOMERS+1)]
    conn.executemany("INSERT INTO customers VALUES (?,?)", customers)

    agents = [(i, f'Agent {i}', f'a{i}@example.com') for i in range(1, AGENTS+1)]
    conn.executemany("INSERT INTO agents VALUES (?,?,?)", agents)

    slas = [(1,'Gold',4),(2,'Standard',24)]
    conn.executemany("INSERT INTO service_levels VALUES (?,?,?)", slas)

    tickets = []
    interactions = []
    tid = 1
    iid = 1
    for _ in range(TICKETS):
        cust = rng.randint(1, CUSTOMERS)
        agent = rng.randint(1, AGENTS)
        sl = rng.choice([1,2])
        status = rng.choice(['OPEN','PENDING','CLOSED'])
        pri = rng.choice(['LOW','MED','HIGH'])
        opened = f"2024-01-{rng.randint(1,5):02d}"
        closed = None if status!='CLOSED' else f"2024-01-{rng.randint(1,5):02d}"
        tickets.append((tid,cust,agent,sl,status,pri,opened,closed))
        interactions.append((iid, tid, agent, 'initial', opened+'T09:00'))
        iid += 1
        tid += 1
    conn.executemany("INSERT INTO tickets VALUES (?,?,?,?,?,?,?,?)", tickets)
    conn.executemany("INSERT INTO interactions VALUES (?,?,?,?,?)", interactions)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
