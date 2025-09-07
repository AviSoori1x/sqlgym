"""Index built SQLite databases for easy discovery."""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main() -> None:
    datasets: dict[str, dict[str, str]] = {}
    for db in ROOT.glob("**/*_normalized.db"):
        rel = db.relative_to(ROOT)
        key = str(rel.parent)
        datasets.setdefault(key, {})["normalized"] = str(rel)
    for db in ROOT.glob("**/*_denormalized.db"):
        rel = db.relative_to(ROOT)
        key = str(rel.parent)
        datasets.setdefault(key, {})["denormalized"] = str(rel)

    index_md = ROOT / "DATASET_INDEX.md"
    index_json = ROOT / "datasets.json"

    grouped: dict[str, list[tuple[str, dict[str, str]]]] = {}
    for key, val in datasets.items():
        top = key.split("/")[0]
        grouped.setdefault(top, []).append((key, val))

    lines = ["# Dataset Index\n"]
    for top in sorted(grouped):
        lines.append(f"## {top}\n")
        for key, paths in sorted(grouped[top]):
            if "normalized" in paths:
                lines.append(f"- `{paths['normalized']}`\n")
            if "denormalized" in paths:
                lines.append(f"- `{paths['denormalized']}`\n")

    index_md.write_text("".join(lines), encoding="utf-8")
    index_json.write_text(json.dumps(datasets, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

