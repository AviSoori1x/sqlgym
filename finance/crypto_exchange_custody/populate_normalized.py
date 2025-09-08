#!/usr/bin/env python3
"""Populate normalized crypto exchange custody schema with deterministic synthetic data."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import get_rng, batch

CLIENTS = 500
WALLETS_PER_CLIENT = 3
TRANSFERS_PER_WALLET = 200
BATCHES = 50


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")

    # clients
    clients = []
    for cid in range(1, CLIENTS + 1):
        clients.append(
            (cid, f"Client {cid}", f"C{cid:05d}", rng.choice(["LOW", "MEDIUM", "HIGH"]), "US")
        )
    conn.executemany("INSERT INTO clients VALUES (?,?,?,?,?)", clients)

    # wallets
    wallets = []
    wid = 1
    for c in clients:
        for _ in range(WALLETS_PER_CLIENT):
            wallets.append(
                (
                    wid,
                    c[0],
                    rng.choice(["BTC", "ETH", "USDC"]),
                    f"addr{wid:08d}",
                    rng.choice(["HOT", "COLD"]),
                )
            )
            wid += 1
    conn.executemany("INSERT INTO wallets VALUES (?,?,?,?,?)", wallets)

    # cold storage batches
    batches = []
    for bid in range(1, BATCHES + 1):
        batches.append((bid, f"B{bid:04d}", f"2024-01-{(bid % 30) + 1:02d}", "OPEN"))
    conn.executemany("INSERT INTO cold_storage_batches VALUES (?,?,?,?)", batches)

    # transfers and moves
    transfers = []
    moves = []
    tid = 1
    move_id = 1
    for w in wallets:
        for t in range(TRANSFERS_PER_WALLET):
            ts = f"2024-02-{(t % 28) + 1:02d}T12:{rng.randint(0,59):02d}:00"
            amt = rng.randint(1, 1_000_000)
            direction = rng.choice(["DEPOSIT", "WITHDRAWAL"])
            status = rng.choice(["PENDING", "COMPLETED"])
            transfers.append((tid, w[0], f"tx{tid:064x}", ts, amt, direction, status))
            if rng.random() < 0.05:
                moves.append((move_id, rng.randint(1, BATCHES), w[0], amt // 2))
                move_id += 1
            tid += 1
    for chunk in batch(transfers, 1000):
        conn.executemany(
            "INSERT INTO custody_transfers VALUES (?,?,?,?,?,?,?)", chunk
        )
    if moves:
        conn.executemany("INSERT INTO cold_storage_moves VALUES (?,?,?,?)", moves)

    conn.commit()

    # create heavy indexes after load
    conn.executescript(
        """
        CREATE INDEX IF NOT EXISTS idx_wallets_client_asset ON wallets(client_id, asset_symbol);
        CREATE INDEX IF NOT EXISTS idx_transfers_wallet_ts ON custody_transfers(wallet_id, transfer_ts);
        CREATE INDEX IF NOT EXISTS idx_transfers_txhash ON custody_transfers(tx_hash);
        CREATE INDEX IF NOT EXISTS idx_moves_batch_wallet ON cold_storage_moves(batch_id, wallet_id);
        """
    )
    conn.commit()
    print("rows", len(clients), len(wallets), len(transfers))
    conn.close()


if __name__ == "__main__":
    main()
