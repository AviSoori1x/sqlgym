"""Index built SQLite databases for easy discovery."""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main() -> None:
    dbs = sorted(ROOT.glob("**/*_normalized.db")) + sorted(ROOT.glob("**/*_denormalized.db"))
    index_md = ROOT / "DATASET_INDEX.md"
    index_json = ROOT / "datasets.json"

    lines = ["# Dataset Index\n"]
    data = []
    for db in dbs:
        rel = db.relative_to(ROOT)
        lines.append(f"- `{rel}`\n")
        data.append({"path": str(rel)})
    index_md.write_text("".join(lines), encoding="utf-8")
    index_json.write_text(json.dumps(data, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
