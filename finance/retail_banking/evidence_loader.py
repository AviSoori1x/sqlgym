#!/usr/bin/env python3
"""Load evidence files into evidence_kv for portable access."""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

SCALE = 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.execute("CREATE TABLE IF NOT EXISTS evidence_kv (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    ev_dir = Path(__file__).parent / "evidence"
    for path in ev_dir.glob("*"):
        if path.suffix not in {".json", ".md"}:
            continue
        if path.suffix == ".json":
            text = path.read_text(encoding="utf-8")
            json.loads(text)
        else:
            text = json.dumps(path.read_text(encoding="utf-8"))
        conn.execute("INSERT OR REPLACE INTO evidence_kv VALUES (?, ?)", (path.stem, text))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
