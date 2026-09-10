# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS inv_barcodes (
    user_id INTEGER NOT NULL,
    barcode TEXT NOT NULL,
    product_id TEXT NOT NULL,
    product_name TEXT NOT NULL DEFAULT '',
    product_code TEXT NOT NULL DEFAULT '',
    pulled_at TEXT NOT NULL,
    PRIMARY KEY (user_id, barcode)
);
CREATE TABLE IF NOT EXISTS inv_warehouses (
    user_id INTEGER NOT NULL,
    id TEXT NOT NULL,
    name TEXT NOT NULL DEFAULT '',
    code TEXT NOT NULL DEFAULT '',
    pulled_at TEXT NOT NULL,
    PRIMARY KEY (user_id, id)
);
CREATE TABLE IF NOT EXISTS inv_sessions (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    warehouse_id TEXT NOT NULL,
    comment TEXT NOT NULL DEFAULT '',
    author TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'draft',
    onec_id TEXT,
    dirty_at TEXT,
    last_error TEXT NOT NULL DEFAULT '',
    deleted INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_inv_sessions_user ON inv_sessions(user_id, warehouse_id, deleted);
CREATE TABLE IF NOT EXISTS inv_lines (
    session_id TEXT NOT NULL,
    line INTEGER NOT NULL,
    product_id TEXT NOT NULL,
    barcode TEXT NOT NULL DEFAULT '',
    name TEXT NOT NULL DEFAULT '',
    qty REAL NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (session_id, line),
    UNIQUE (session_id, product_id),
    FOREIGN KEY (session_id) REFERENCES inv_sessions(id)
);
CREATE TABLE IF NOT EXISTS inv_meta (
    user_id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY (user_id, key)
);
"""


def init_inventory_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def meta_get(conn: sqlite3.Connection, user_id: int, key: str) -> str:
    row = conn.execute(
        "SELECT value FROM inv_meta WHERE user_id = ? AND key = ?",
        (user_id, key),
    ).fetchone()
    return str(row["value"]) if row else ""


def meta_set(conn: sqlite3.Connection, user_id: int, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO inv_meta(user_id, key, value) VALUES (?, ?, ?) "
        "ON CONFLICT(user_id, key) DO UPDATE SET value = excluded.value",
        (user_id, key, value),
    )
    conn.commit()
