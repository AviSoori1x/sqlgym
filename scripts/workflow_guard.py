"""Validate multi-SQL workflow task files."""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLOCK_RE = re.compile(r"```sql\n(.*?)```", re.DOTALL)
STEP_RE = re.compile(r"--\s*step:\s*(\w+)")
DEP_RE = re.compile(r"--\s*depends:\s*([\w, ]+)")


def check_file(path: pathlib.Path) -> list[str]:
    errors = []
    text = path.read_text(encoding="utf-8")
    seen: set[str] = set()
    for block in BLOCK_RE.findall(text):
        step_match = STEP_RE.search(block)
        if not step_match:
            errors.append(f"Missing step name in {path}")
            continue
        step = step_match.group(1)
        dep_match = DEP_RE.search(block)
        if dep_match:
            deps = {d.strip() for d in dep_match.group(1).split(',') if d.strip()}
            missing = deps - seen
            if missing:
                errors.append(f"Step {step} depends on missing {missing} in {path}")
        seen.add(step)
    return errors


def main() -> None:
    errors = []
    for wf in ROOT.glob("*/workflow_tasks.md"):
        errors.extend(check_file(wf))
    if errors:
        for e in errors:
            print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
