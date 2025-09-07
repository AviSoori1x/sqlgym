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
    sub = path.parent.relative_to(ROOT)
    if name_set in seen:
        other = seen[name_set].parent.relative_to(ROOT)
        errors.append(f"{sub}: duplicate table set {name_set} also used in {other}")
    else:
        seen[name_set] = path
    for name in table_names:
        if name in FORBIDDEN:
            errors.append(f"{sub}: forbidden table name '{name}'")
    if len(table_names) < 3:
        errors.append(f"{sub}: too few tables (found {len(table_names)})")
    check_count = text.count("check")
    if check_count < 2:
        errors.append(f"{sub}: expect at least 2 CHECK constraints (found {check_count})")
    if "unique" not in text:
        errors.append(f"{sub}: missing UNIQUE constraint")
    idx_count = text.count("create index")
    if idx_count < 3:
        errors.append(f"{sub}: need at least 3 indexes (found {idx_count})")
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
