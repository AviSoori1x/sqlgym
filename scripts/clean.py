"""Remove generated SQLite database files."""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main() -> None:
    for db in ROOT.glob("**/*.db"):
        db.unlink()


if __name__ == "__main__":
    main()
