#!/usr/bin/env python3
"""Load evidence files into mortgage servicing database."""
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
    
    # Load servicing policies
    policies_path = evidence_dir / "servicing_policies.json"
    if policies_path.exists():
        with open(policies_path) as f:
            conn.execute(
                "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
                ("servicing_policies", f.read())
            )
    
    conn.commit()
    conn.close()
    print("Evidence loaded!")

if __name__ == "__main__":
    main()
