"""Create directory scaffolds for domains and subdomains listed in domains.yaml."""
from __future__ import annotations

import argparse
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOMAINS_YAML = ROOT / "domains.yaml"

SUB_FILES = [
    "README.md",
    "generate_schema_normalized.py",
    "schema_normalized.sql",
    "schema_denormalized.sql",
    "populate_normalized.py",
    "populate_denormalized.py",
    "sanity_checks.sql",
    "sample_text_to_sql_tasks.md",
    "evidence/.keep",
]

WORKFLOW_FILE = "workflow_tasks.md"

STUB_README = "# {name}\n\nTODO: document entities, indexes and efficiency notes.\n"

STUB_PY = "#!/usr/bin/env python3\n\"\"\"Stub file for {name}. Actual implementation required.\"\"\"\n"

STUB_SQL = "-- TODO: add SQL for {name}\n"

STUB_TASKS = "# Sample Tasks for {name}\n\n<!-- TODO: add multi-turn tasks -->\n"


def parse_domains(path: pathlib.Path) -> dict[str, list[str]]:
    domains: dict[str, list[str]] = {}
    current = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line or line.startswith("#"):
            continue
        if line.endswith(":"):
            current = line[:-1]
            domains[current] = []
        elif line.strip().startswith("-") and current:
            domains[current].append(line.split("-", 1)[1].strip())
    return domains


def ensure_subdomain(top: pathlib.Path, sub: str) -> None:
    subdir = top / sub
    subdir.mkdir(parents=True, exist_ok=True)
    for f in SUB_FILES:
        path = subdir / f
        if path.suffix == ".py":
            path.write_text(STUB_PY.format(name=sub))
        elif path.suffix == ".sql":
            path.write_text(STUB_SQL.format(name=sub))
        elif f.endswith(".md"):
            if f == "README.md":
                path.write_text(STUB_README.format(name=sub))
            else:
                path.write_text(STUB_TASKS.format(name=sub))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()


def ensure_workflow(top: pathlib.Path) -> None:
    wf = top / WORKFLOW_FILE
    if not wf.exists():
        wf.write_text("# Workflow Tasks\n\n<!-- TODO: add multi-step SQL workflows -->\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", help="Top-level domain filter", default=None)
    args = parser.parse_args()

    domains = parse_domains(DOMAINS_YAML)

    for top_name, subs in domains.items():
        if args.domain and args.domain != top_name:
            continue
        top = ROOT / top_name.lower()
        top.mkdir(exist_ok=True)
        ensure_workflow(top)
        for sub in subs:
            ensure_subdomain(top, sub)


if __name__ == "__main__":
    main()
