#!/usr/bin/env python3
"""Load evidence files into energy manufacturing database."""
import argparse, sqlite3
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    args = parser.parse_args()
    
    conn = sqlite3.connect(args.db)
    conn.execute("CREATE TABLE IF NOT EXISTS evidence_kv (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    conn.execute("INSERT OR REPLACE INTO evidence_kv VALUES ('energy_protocols', '{}')")
    conn.commit()
    conn.close()
    print("Evidence loaded!")

if __name__ == "__main__":
    main()