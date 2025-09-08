#!/usr/bin/env python3
"""Load evidence files into EHR encounters and orders database."""
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
    
    evidence_dir = Path(__file__).parent / "evidence"
    
    # Load existing lab codes if present
    lab_codes_path = evidence_dir / "lab_codes.md"
    if lab_codes_path.exists():
        with open(lab_codes_path) as f:
            conn.execute(
                "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
                ("lab_codes", f.read())
            )
    
    # Create sample clinical protocols
    conn.execute(
        "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
        ("clinical_protocols", '{"laboratory_protocols": {"stat_turnaround_target": 1, "routine_turnaround_target": 4}}')
    )
    
    conn.commit()
    conn.close()
    print("Evidence loaded!")

if __name__ == "__main__":
    main()