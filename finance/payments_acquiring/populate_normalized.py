#!/usr/bin/env python3
"""Populate normalized payments acquiring schema with deterministic synthetic data."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import get_rng, batch

MERCHANTS = 50
TERMINALS_PER_MERCHANT = 2
TXNS_PER_TERMINAL = 100


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")

    merchants = []
    for mid in range(1, MERCHANTS + 1):
        merchants.append((mid, f"Merchant {mid}", f"M{mid:05d}", rng.choice(['BASIC','STANDARD','GOLD']), rng.randint(1000,9999), 'US'))
    conn.executemany("INSERT INTO merchants VALUES (?,?,?,?,?,?)", merchants)

    terminals = []
    tid = 1
    for m in merchants:
        for _ in range(TERMINALS_PER_MERCHANT):
            terminals.append((tid, m[0], f"SN{tid:06d}", 'ACTIVE'))
            tid += 1
    conn.executemany("INSERT INTO terminals VALUES (?,?,?,?)", terminals)

    batches = []
    txns = []
    cbks = []
    batch_id = 1
    txn_id = 1
    cb_id = 1
    for m in merchants:
        for d in range(3):
            batches.append((batch_id, m[0], f"2024-01-{d+1:02d}", 'CLOSED'))
            for t in [t for t in terminals if t[1]==m[0]]:
                for _ in range(TXNS_PER_TERMINAL):
                    ts = f"2024-01-{d+1:02d}T12:{rng.randint(0,59):02d}:00"
                    amount = rng.randint(100,2000)
                    txns.append((txn_id, m[0], t[0], batch_id, ts, amount, 'USD', rng.choice(['AUTH','REFUND']), rng.choice(['APPROVED','DECLINED'])))
                    if rng.random() < 0.02:
                        cbks.append((cb_id, txn_id, 'RETRIEVAL', 'FRAUD', ts, amount))
                        cb_id += 1
                    txn_id += 1
            batch_id += 1
    conn.executemany("INSERT INTO settlement_batches VALUES (?,?,?,?)", batches)
    for chunk in batch(txns, 500):
        conn.executemany("INSERT INTO card_transactions VALUES (?,?,?,?,?,?,?,?,?)", chunk)
    if cbks:
        conn.executemany("INSERT INTO chargebacks VALUES (?,?,?,?,?,?)", cbks)
    conn.commit()
    print("rows", len(merchants), len(terminals), len(txns))
    conn.close()


if __name__ == "__main__":
    main()
