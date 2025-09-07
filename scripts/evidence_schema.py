"""Validate that evidence files referenced by tasks exist and have proper format."""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
EVIDENCE_RE = re.compile(r"evidence/([\w_.-]+)")


def check_sub(subdir: pathlib.Path) -> list[str]:
    errors = []
    tasks = subdir / "sample_text_to_sql_tasks.md"
    if not tasks.exists():
        return errors
    text = tasks.read_text(encoding="utf-8")
    for match in EVIDENCE_RE.findall(text):
        ev = subdir / "evidence" / match
        if not ev.exists():
            errors.append(f"Missing evidence file {ev}")
            continue
        if ev.suffix == ".json":
            try:
                json.loads(ev.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                errors.append(f"Invalid JSON in {ev}")
    return errors


def main() -> None:
    errors = []
    for tasks in ROOT.glob("**/sample_text_to_sql_tasks.md"):
        errors.extend(check_sub(tasks.parent))
    if errors:
        for e in errors:
            print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
