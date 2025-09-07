"""Run sanity_checks.sql for each subdomain database."""
from __future__ import annotations

import argparse
import pathlib
import sqlite3
import subprocess

from scaffold import parse_domains  # type: ignore

ROOT = pathlib.Path(__file__).resolve().parent.parent


def run_sql(db: pathlib.Path, sql_file: pathlib.Path) -> None:
    subprocess.run(["sqlite3", str(db), f".read {sql_file}"], check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", help="Top-level domain filter", default=None)
    args = parser.parse_args()

    domains = parse_domains(ROOT / "domains.yaml")
    errors = []
    for top, subs in domains.items():
        if args.domain and args.domain != top:
            continue
        for sub in subs:
            subdir = ROOT / top.lower() / sub
            db = subdir / f"{sub}_normalized.db"
            sql_file = subdir / "sanity_checks.sql"
            if not db.exists():
                errors.append(f"{subdir}: {db.name} missing; build first")
                continue
            if sql_file.exists():
                run_sql(db, sql_file)
    if errors:
        for e in errors:
            print(e)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
