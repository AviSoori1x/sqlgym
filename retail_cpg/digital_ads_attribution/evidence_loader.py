#!/usr/bin/env python3
"""Load evidence files into digital ads attribution database."""
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
    
    # Load campaign optimization rules JSON
    rules_path = evidence_dir / "campaign_optimization_rules.json"
    if rules_path.exists():
        with open(rules_path) as f:
            rules_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("campaign_optimization_rules", rules_data)
        )
    
    # Load attribution methodology markdown
    methodology_path = evidence_dir / "attribution_methodology.md"
    if methodology_path.exists():
        with open(methodology_path) as f:
            methodology_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("attribution_methodology", methodology_data)
        )
    
    conn.commit()
    conn.close()
    print("Evidence files loaded successfully!")

if __name__ == "__main__":
    main()
