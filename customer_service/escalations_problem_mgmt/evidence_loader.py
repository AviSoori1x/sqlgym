#!/usr/bin/env python3
"""Load evidence files into escalations problem management database."""
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
    
    # Load escalation matrix JSON
    matrix_path = evidence_dir / "escalation_matrix.json"
    if matrix_path.exists():
        with open(matrix_path) as f:
            matrix_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("escalation_matrix", matrix_data)
        )
    
    # Load SLA policy JSON
    sla_path = evidence_dir / "sla_policy.json"
    if sla_path.exists():
        with open(sla_path) as f:
            sla_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("sla_policy", sla_data)
        )
    
    conn.commit()
    conn.close()
    print("Evidence files loaded successfully!")

if __name__ == "__main__":
    main()
