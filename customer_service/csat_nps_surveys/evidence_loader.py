#!/usr/bin/env python3
"""Load evidence files into CSAT/NPS surveys database."""
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
    
    # Load survey best practices JSON
    practices_path = evidence_dir / "survey_best_practices.json"
    if practices_path.exists():
        with open(practices_path) as f:
            practices_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("survey_best_practices", practices_data)
        )
    
    # Load NPS targets JSON
    targets_path = evidence_dir / "nps_targets.json"
    if targets_path.exists():
        with open(targets_path) as f:
            targets_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("nps_targets", targets_data)
        )
    
    conn.commit()
    conn.close()
    print("Evidence files loaded successfully!")

if __name__ == "__main__":
    main()
