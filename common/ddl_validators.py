"""Helpers to validate generated SQLite DDL."""
from __future__ import annotations

import sqlite3
from typing import Iterable


def pragma_foreign_keys_on(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys=ON")


def has_indexes(conn: sqlite3.Connection, table: str, expected: Iterable[str]) -> bool:
    cur = conn.execute("PRAGMA index_list(%s)" % table)
    existing = {row[1] for row in cur.fetchall()}
    return all(idx in existing for idx in expected)


def table_has_pk(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute(f"PRAGMA table_info({table})")
    return any(row[5] == 1 for row in cur.fetchall())


def table_has_fk(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute(f"PRAGMA foreign_key_list({table})")
    return bool(cur.fetchall())

