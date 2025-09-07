#!/usr/bin/env python3
"""Populate fund accounting normalized tables with deterministic data."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import get_rng, batch

FUNDS = 3
INVESTORS = 5
SECURITIES = 5


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")

    funds = [
        (i, f"Fund {i}", rng.choice(['US','EU','APAC']), rng.choice(['ACTIVE','INACTIVE']))
        for i in range(1, FUNDS + 1)
    ]
    conn.executemany("INSERT INTO funds VALUES (?,?,?,?)", funds)

    investors = [
        (i, f"Investor {i}", rng.choice(['RETAIL','INSTITUTIONAL']), rng.choice(['LOW','MED','HIGH']))
        for i in range(1, INVESTORS + 1)
    ]
    conn.executemany("INSERT INTO investors VALUES (?,?,?,?)", investors)

    securities = [
        (i, f"SEC{i:03d}", rng.choice(['EQUITY','BOND','CASH']), rng.choice(['USD','EUR','JPY']))
        for i in range(1, SECURITIES + 1)
    ]
    conn.executemany("INSERT INTO securities VALUES (?,?,?,?)", securities)

    subs = []
    sub_id = 1
    for inv in range(1, INVESTORS + 1):
        fund = rng.randint(1, FUNDS)
        subs.append((sub_id, fund, inv, f"2024-01-{rng.randint(1,3):02d}"))
        sub_id += 1
    for chunk in batch(subs, 100):
        conn.executemany("INSERT INTO subscriptions VALUES (?,?,?,?)", chunk)

    holdings = []
    hold_id = 1
    for fund in range(1, FUNDS + 1):
        for sec in rng.sample(range(1, SECURITIES + 1), 3):
            qty = rng.randint(1, 1000)
            date = f"2024-01-{rng.randint(1,3):02d}"
            holdings.append((hold_id, fund, sec, qty, date))
            hold_id += 1
    for chunk in batch(holdings, 100):
        conn.executemany("INSERT INTO holdings VALUES (?,?,?,?,?)", chunk)

    conn.execute("CREATE INDEX idx_funds_status ON funds(status)")
    conn.execute("CREATE INDEX idx_investors_tier ON investors(tier)")
    conn.execute("CREATE INDEX idx_securities_type ON securities(type)")
    conn.execute("CREATE INDEX idx_holdings_fund_date ON holdings(fund_id, position_date)")
    conn.execute("CREATE INDEX idx_subs_fund_inv ON subscriptions(fund_id, investor_id)")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
