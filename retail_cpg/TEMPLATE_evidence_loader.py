#!/usr/bin/env python3
"""Template: Load evidence files into retail CPG subdomain database."""
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
    
    # TEMPLATE: Load JSON evidence files
    # Replace 'config_file.json' with your actual filename
    config_path = evidence_dir / "domain_configuration.json"
    if config_path.exists():
        with open(config_path) as f:
            config_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("domain_configuration", config_data)
        )
    
    # TEMPLATE: Load markdown evidence files  
    # Replace 'guidelines.md' with your actual filename
    guidelines_path = evidence_dir / "domain_guidelines.md"
    if guidelines_path.exists():
        with open(guidelines_path) as f:
            guidelines_data = f.read()
        conn.execute(
            "INSERT OR REPLACE INTO evidence_kv (key, value) VALUES (?, ?)",
            ("domain_guidelines", guidelines_data)
        )
    
    # ADD MORE EVIDENCE FILES AS NEEDED:
    # - Business rules JSON
    # - Policy documents (MD)  
    # - Configuration files (JSON)
    # - Lookup tables (JSON)
    
    conn.commit()
    conn.close()
    print("Evidence files loaded successfully!")

if __name__ == "__main__":
    main()

# INSTRUCTIONS:
# 1. Copy this file to your subdomain directory
# 2. Replace template filenames with actual evidence files
# 3. Update the evidence_kv key names to be descriptive
# 4. Add additional file loading as needed
# 5. Ensure evidence files exist in the evidence/ subdirectory
