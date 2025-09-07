"""Check schema diversity and absence of generic names."""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORBIDDEN = {"entities", "related_entities", "facts"}
CREATE_TABLE_RE = re.compile(r"create table\s+(\w+)", re.IGNORECASE)


def check_schema(path: pathlib.Path, seen: dict[tuple[str, ...], pathlib.Path]) -> list[str]:
    text = path.read_text(encoding="utf-8").lower()
    errors = []
    table_names = CREATE_TABLE_RE.findall(text)
    name_set = tuple(sorted(table_names))
    if name_set in seen:
        errors.append(f"Duplicate table set {name_set} also used in {seen[name_set]}")
    else:
        seen[name_set] = path
    for name in table_names:
        if name in FORBIDDEN:
            errors.append(f"Forbidden table name '{name}' in {path}")
    if len(table_names) < 3:
        errors.append(f"Too few tables in {path}")
    if text.count("check") < 2:
        errors.append(f"Expect at least 2 CHECK constraints in {path}")
    if "unique" not in text:
        errors.append(f"Missing UNIQUE constraint in {path}")
    if text.count("create index") < 3:
        errors.append(f"Need at least 3 indexes in {path}")
    return errors


def main() -> None:
    errors = []
    seen: dict[tuple[str, ...], pathlib.Path] = {}
    for schema in ROOT.glob("**/schema_normalized.sql"):
        errors.extend(check_schema(schema, seen))
    if errors:
        for e in errors:
            print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
