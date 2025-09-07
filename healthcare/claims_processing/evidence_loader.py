#!/usr/bin/env python3
"""Load evidence files into claims processing database."""
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
    
    # Load claims processing guidelines JSON
    guidelines_path = evidence_dir / "claims_processing_guidelines.json"
    if guidelines_path.exists():
        with open(guidelines_path) as f:
            guidelines_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("claims_processing_guidelines", guidelines_data)
        )
    
    # Load existing coding guidelines if present
    coding_path = evidence_dir / "coding_guidelines.md"
    if coding_path.exists():
        with open(coding_path) as f:
            coding_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("coding_guidelines", coding_data)
        )
    
    conn.commit()
    conn.close()
    print("Evidence files loaded successfully!")

if __name__ == "__main__":
    main()