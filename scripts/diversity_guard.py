"""Check schema diversity and absence of generic names."""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORBIDDEN = {"entities", "related_entities", "facts"}


def check_schema(path: pathlib.Path) -> list[str]:
    text = path.read_text(encoding="utf-8").lower()
    errors = []
    for name in FORBIDDEN:
        if name in text:
            errors.append(f"Forbidden table name '{name}' in {path}")
    table_count = text.count("create table")
    if table_count < 3:
        errors.append(f"Too few tables in {path}")
    return errors


def main() -> None:
    errors = []
    for schema in ROOT.glob("**/schema_normalized.sql"):
        errors.extend(check_schema(schema))
    if errors:
        for e in errors:
            print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
