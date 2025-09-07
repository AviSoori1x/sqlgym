#!/usr/bin/env python3
"""Generate normalized schema for crypto exchange custody."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common import ddl_validators as dv

DDL = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    client_code TEXT NOT NULL UNIQUE,
    risk_tier TEXT NOT NULL CHECK(risk_tier IN ('LOW','MEDIUM','HIGH')),
    country TEXT NOT NULL CHECK(length(country)=2)
);
CREATE TABLE IF NOT EXISTS wallets (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id),
    asset_symbol TEXT NOT NULL CHECK(asset_symbol IN ('BTC','ETH','USDC')),
    address TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK(status IN ('HOT','COLD'))
);
CREATE INDEX IF NOT EXISTS idx_wallets_client_asset ON wallets(client_id, asset_symbol);
CREATE TABLE IF NOT EXISTS cold_storage_batches (
    id INTEGER PRIMARY KEY,
    batch_code TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('OPEN','SEALED'))
);
CREATE TABLE IF NOT EXISTS custody_transfers (
    id INTEGER PRIMARY KEY,
    wallet_id INTEGER NOT NULL REFERENCES wallets(id),
    tx_hash TEXT NOT NULL UNIQUE,
    transfer_ts TEXT NOT NULL,
    amount_sats INTEGER NOT NULL,
    direction TEXT NOT NULL CHECK(direction IN ('DEPOSIT','WITHDRAWAL')),
    status TEXT NOT NULL CHECK(status IN ('PENDING','COMPLETED'))
);
CREATE INDEX IF NOT EXISTS idx_transfers_wallet_ts ON custody_transfers(wallet_id, transfer_ts);
CREATE INDEX IF NOT EXISTS idx_transfers_txhash ON custody_transfers(tx_hash);
CREATE TABLE IF NOT EXISTS cold_storage_moves (
    id INTEGER PRIMARY KEY,
    batch_id INTEGER NOT NULL REFERENCES cold_storage_batches(id),
    wallet_id INTEGER NOT NULL REFERENCES wallets(id),
    amount_sats INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_moves_batch_wallet ON cold_storage_moves(batch_id, wallet_id);
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
