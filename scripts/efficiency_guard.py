"""Validate that fast queries use indexes and slow ones perform scans."""
from __future__ import annotations

import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

SQL_BLOCK_RE = re.compile(r"```sql (fast|slow)\n(.*?)```", re.DOTALL)


def extract_pairs(tasks: str) -> list[tuple[str, str]]:
    blocks = SQL_BLOCK_RE.findall(tasks)
    pairs = []
    fast = slow = None
    for tag, sql in blocks:
        if tag == "fast":
            fast = sql.strip()
        elif tag == "slow":
            slow = sql.strip()
        if fast and slow:
            pairs.append((fast, slow))
            fast = slow = None
    return pairs


def check_file(subdir: pathlib.Path) -> list[str]:
    errors = []
    db = subdir / f"{subdir.name}_normalized.db"
    tasks_file = subdir / "sample_text_to_sql_tasks.md"
    if not db.exists():
        errors.append(f"{db} missing; no DB to check; build first")
        return errors
    if not tasks_file.exists():
        errors.append(f"Missing tasks file {tasks_file}")
        return errors
    pairs = extract_pairs(tasks_file.read_text(encoding="utf-8"))
    if not pairs:
        errors.append(f"No fast/slow pairs in {tasks_file}")
        return errors
    conn = sqlite3.connect(db)
    try:
        for fast, slow in pairs:
            fast_plan = conn.execute(f"EXPLAIN QUERY PLAN {fast}").fetchall()
            slow_plan = conn.execute(f"EXPLAIN QUERY PLAN {slow}").fetchall()
            fast_ok = any("USING INDEX" in str(r) for r in fast_plan)
            slow_bad = any("SCAN" in str(r) for r in slow_plan)
            if not (fast_ok and slow_bad):
                errors.append(f"Inefficient pair in {tasks_file}")
    finally:
        conn.close()
    return errors


def main() -> None:
    errors = []
    for tasks in ROOT.glob("**/sample_text_to_sql_tasks.md"):
        errors.extend(check_file(tasks.parent))
    if errors:
        for e in errors:
            print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
