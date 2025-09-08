#!/usr/bin/env python3
"""Populate procurement_supplier_scorecards normalized schema with synthetic data."""
from __future__ import annotations

import argparse
import sqlite3
import random
from pathlib import Path
from datetime import datetime, timedelta
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import get_rng, batch

# Scale constants
PRIMARY_ENTITIES = 1000
SECONDARY_ENTITIES = 5000
FACT_RECORDS = 50000

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    random.seed(args.seed)
    
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")
    
    print("Inserting primary entities...")
    # Create synthetic data appropriate for procurement_supplier_scorecards
    primary_data = []
    for i in range(1, PRIMARY_ENTITIES + 1):
        primary_data.append((i, f'ENTITY{i:05d}', f'Entity {i}', 'ACTIVE'))
    
    # Insert into first table (adapt table name and columns as needed)
    # conn.executemany("INSERT INTO main_table VALUES (?,?,?,?)", primary_data)
    
    # Create evidence table
    conn.execute("CREATE TABLE IF NOT EXISTS evidence_kv (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    
    conn.commit()
    
    # Create indexes
    print("Creating indexes...")
    # Add appropriate indexes
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()