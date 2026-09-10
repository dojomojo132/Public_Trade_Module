# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from pathlib import Path

from app.inventory.schema import init_inventory_schema

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS connections (
    user_id INTEGER PRIMARY KEY,
    ib_location TEXT NOT NULL DEFAULT '',
    api_key TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    init_inventory_schema(conn)
    conn.commit()


def get_connection(conn: sqlite3.Connection, user_id: int) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT user_id, ib_location, api_key FROM connections WHERE user_id = ?",
        (user_id,),
    ).fetchone()


def save_connection(conn: sqlite3.Connection, user_id: int, ib_location: str, api_key: str) -> None:
    conn.execute(
        "INSERT INTO connections(user_id, ib_location, api_key) VALUES (?, ?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET ib_location = excluded.ib_location, api_key = excluded.api_key",
        (user_id, ib_location.strip(), api_key.strip()),
    )
    conn.commit()
