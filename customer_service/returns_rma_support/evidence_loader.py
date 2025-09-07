#!/usr/bin/env python3
"""Load evidence files into returns RMA support database."""
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
    
    # Load return policy JSON
    policy_path = evidence_dir / "return_policy.json"
    if policy_path.exists():
        with open(policy_path) as f:
            policy_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("return_policy", policy_data)
        )
    
    # Load inspection guidelines markdown
    guidelines_path = evidence_dir / "inspection_guidelines.md"
    if guidelines_path.exists():
        with open(guidelines_path) as f:
            guidelines_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("inspection_guidelines", guidelines_data)
        )
    
    conn.commit()
    conn.close()
    print("Evidence files loaded successfully!")

if __name__ == "__main__":
    main()
