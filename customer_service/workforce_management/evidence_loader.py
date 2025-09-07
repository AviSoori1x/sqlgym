#!/usr/bin/env python3
"""Load evidence files into workforce management database."""
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
    
    # Load workforce policies JSON
    policies_path = evidence_dir / "workforce_policies.json"
    if policies_path.exists():
        with open(policies_path) as f:
            policies_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("workforce_policies", policies_data)
        )
    
    # Load shift patterns markdown
    patterns_path = evidence_dir / "shift_patterns.md"
    if patterns_path.exists():
        with open(patterns_path) as f:
            patterns_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("shift_patterns", patterns_data)
        )
    
    conn.commit()
    conn.close()
    print("Evidence files loaded successfully!")

if __name__ == "__main__":
    main()
