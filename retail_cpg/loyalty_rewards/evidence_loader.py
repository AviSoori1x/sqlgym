#!/usr/bin/env python3
"""Load evidence files into loyalty rewards database."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    args = parser.parse_args()
    
    conn = sqlite3.connect(args.db)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS evidence_kv (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    
    # Create sample evidence entry
    conn.execute(
        "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
        ("loyalty_program_rules", '{"tier_benefits": {"Gold": ["2x points", "free shipping"]}}')
    )
    
    conn.commit()
    conn.close()
    print("Evidence loaded!")

if __name__ == "__main__":
    main()
