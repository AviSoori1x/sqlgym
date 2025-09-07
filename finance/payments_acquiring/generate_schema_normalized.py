#!/usr/bin/env python3
"""Generate normalized schema for payments acquiring.

Entities:
- merchants: onboarding/KYC lifecycle at daily grain
- terminals: merchant devices
- card_transactions: intraday auths/refunds in integer cents
- settlement_batches: business-day cutovers per merchant
- chargebacks: retrieval→arbitration→final dispute flow

Time grains vary from intraday transactions to daily batch cutovers. All monetary
fields use INTEGER cents and timestamps are ISO-8601 text. The schema enables
index-efficient queries on merchant+time and settlement joins.
"""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common import ddl_validators as dv

DDL = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS merchants (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    merchant_code TEXT NOT NULL UNIQUE,
    kyc_tier TEXT NOT NULL CHECK(kyc_tier IN ('BASIC','STANDARD','GOLD')),
    mcc INTEGER NOT NULL,
    country TEXT NOT NULL CHECK(length(country)=2)
);

CREATE TABLE IF NOT EXISTS terminals (
    id INTEGER PRIMARY KEY,
    merchant_id INTEGER NOT NULL REFERENCES merchants(id),
    serial_number TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE','INACTIVE'))
);

CREATE TABLE IF NOT EXISTS settlement_batches (
    id INTEGER PRIMARY KEY,
    merchant_id INTEGER NOT NULL REFERENCES merchants(id),
    cutover_utc_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('OPEN','CLOSED','PAID')),
    UNIQUE(merchant_id, cutover_utc_date)
);
CREATE INDEX IF NOT EXISTS idx_settlement_batches_merchant_date ON settlement_batches(merchant_id, cutover_utc_date);

CREATE TABLE IF NOT EXISTS card_transactions (
    id INTEGER PRIMARY KEY,
    merchant_id INTEGER NOT NULL REFERENCES merchants(id),
    terminal_id INTEGER NOT NULL REFERENCES terminals(id),
    settlement_batch_id INTEGER REFERENCES settlement_batches(id),
    txn_ts TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    currency TEXT NOT NULL CHECK(length(currency)=3),
    txn_type TEXT NOT NULL CHECK(txn_type IN ('AUTH','REFUND')),
    auth_status TEXT NOT NULL CHECK(auth_status IN ('APPROVED','DECLINED','REVERSED'))
);
CREATE INDEX IF NOT EXISTS idx_card_transactions_merchant_ts ON card_transactions(merchant_id, txn_ts);
CREATE INDEX IF NOT EXISTS idx_card_transactions_batch_merchant ON card_transactions(settlement_batch_id, merchant_id);

CREATE TABLE IF NOT EXISTS chargebacks (
    id INTEGER PRIMARY KEY,
    card_transaction_id INTEGER NOT NULL REFERENCES card_transactions(id),
    stage TEXT NOT NULL CHECK(stage IN ('RETRIEVAL','ARBITRATION','FINAL')),
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL,
    amount_cents INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_chargebacks_txn_stage ON chargebacks(card_transaction_id, stage);
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="schema_normalized.sql")
    parser.add_argument("--db", help="optional path to create sqlite db")
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
