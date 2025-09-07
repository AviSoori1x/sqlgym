#!/usr/bin/env python3
"""Load evidence files into customer 360 segmentation database."""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True, help="Path to SQLite database")
    args = parser.parse_args()
    
    conn = sqlite3.connect(args.db)
    
    # Create evidence_kv table if it doesn't exist
    conn.execute("""
        CREATE TABLE IF NOT EXISTS evidence_kv (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    
    evidence_dir = Path(__file__).parent / "evidence"
    
    # Load customer segmentation config JSON
    config_path = evidence_dir / "customer_segmentation_config.json"
    if config_path.exists():
        with open(config_path) as f:
            config_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("customer_segmentation_config", config_data)
        )
    
    # Load personalization strategy markdown
    strategy_path = evidence_dir / "personalization_strategy.md"
    if strategy_path.exists():
        with open(strategy_path) as f:
            strategy_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("personalization_strategy", strategy_data)
        )
    
    conn.commit()
    conn.close()
    print("Evidence files loaded successfully!")

if __name__ == "__main__":
    main()
