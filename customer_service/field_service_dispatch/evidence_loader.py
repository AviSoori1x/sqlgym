#!/usr/bin/env python3
"""Load evidence files into field service dispatch database."""
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
    
    # Load service SLA JSON
    sla_path = evidence_dir / "service_sla.json"
    if sla_path.exists():
        with open(sla_path) as f:
            sla_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("service_sla", sla_data)
        )
    
    # Load service skills JSON
    skills_path = evidence_dir / "service_skills.json"
    if skills_path.exists():
        with open(skills_path) as f:
            skills_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("service_skills", skills_data)
        )
    
    conn.commit()
    conn.close()
    print("Evidence files loaded successfully!")

if __name__ == "__main__":
    main()
