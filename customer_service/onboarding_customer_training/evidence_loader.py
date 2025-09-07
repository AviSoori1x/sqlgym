#!/usr/bin/env python3
"""Load evidence files into onboarding customer training database."""
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
    
    # Load onboarding paths JSON
    paths_path = evidence_dir / "onboarding_paths.json"
    if paths_path.exists():
        with open(paths_path) as f:
            paths_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("onboarding_paths", paths_data)
        )
    
    # Load tier targets JSON
    targets_path = evidence_dir / "tier_targets.json"
    if targets_path.exists():
        with open(targets_path) as f:
            targets_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("tier_targets", targets_data)
        )
    
    conn.commit()
    conn.close()
    print("Evidence files loaded successfully!")

if __name__ == "__main__":
    main()
