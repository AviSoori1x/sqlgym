"""Build all subdomain datasets by generating schema and populating."""
from __future__ import annotations

import argparse
import pathlib
import subprocess

from scripts.scaffold import parse_domains

ROOT = pathlib.Path(__file__).resolve().parent.parent


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def build_sub(top: str, sub: str) -> None:
    subdir = ROOT / top / sub
    gen = subdir / "generate_schema_normalized.py"
    pop = subdir / "populate_normalized.py"
    if gen.exists():
        run(["python3", str(gen), "--db", f"{subdir}/{sub}_normalized.db", "--out", str(subdir / "schema_normalized.sql")])
    if pop.exists():
        run(["python3", str(pop), "--db", f"{subdir}/{sub}_normalized.db"])
    evidence_loader = subdir / "evidence_loader.py"
    if evidence_loader.exists():
        run(["python3", str(evidence_loader), "--db", f"{subdir}/{sub}_normalized.db"])
    denorm_pop = subdir / "populate_denormalized.py"
    if denorm_pop.exists():
        run(["python3", str(denorm_pop), "--db", f"{subdir}/{sub}_denormalized.db"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", help="Top-level domain filter", default=None)
    args = parser.parse_args()

    domains = parse_domains(ROOT / "domains.yaml")
    for top, subs in domains.items():
        if args.domain and args.domain != top:
            continue
        for sub in subs:
            build_sub(top.lower(), sub)


if __name__ == "__main__":
    main()
