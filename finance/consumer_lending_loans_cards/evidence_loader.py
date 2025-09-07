#!/usr/bin/env python3
"""Load evidence files into consumer lending database."""
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
    
    # Load underwriting policy JSON
    policy_path = evidence_dir / "underwriting_policy.json"
    if policy_path.exists():
        with open(policy_path) as f:
            policy_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("underwriting_policy", policy_data)
        )
    
    # Load credit scoring model markdown
    scoring_path = evidence_dir / "credit_scoring_model.md"
    if scoring_path.exists():
        with open(scoring_path) as f:
            scoring_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("credit_scoring_model", scoring_data)
        )
    
    conn.commit()
    conn.close()
    print("Evidence files loaded successfully!")

if __name__ == "__main__":
    main()
