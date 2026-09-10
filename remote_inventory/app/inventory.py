# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
import uuid

from app.catalog import find_barcode, utcnow


class InventoryError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


def _session(conn: sqlite3.Connection, session_id: str) -> sqlite3.Row:
    row = conn.execute(
        "SELECT * FROM sessions WHERE id = ? AND deleted = 0",
        (session_id,),
    ).fetchone()
    if row is None:
        raise InventoryError("Документ не найден", 404)
    return row


def _assert_writable(row: sqlite3.Row) -> None:
    if row["status"] == "syncing":
        raise InventoryError("Документ сейчас синхронизируется", 409)


def list_docs(conn: sqlite3.Connection, warehouse_id: str) -> list[dict]:
    rows = conn.execute(
        """
        SELECT s.id, s.comment, s.author, s.status, s.onec_id,
               (SELECT COUNT(*) FROM lines l WHERE l.session_id = s.id) AS lines
        FROM sessions s
        WHERE s.warehouse_id = ? AND s.deleted = 0
        ORDER BY s.created_at DESC
        """,
        (warehouse_id,),
    ).fetchall()
    return [
        {
            "id": row["id"],
            "comment": row["comment"],
            "author": row["author"],
            "status": row["status"],
            "onecId": row["onec_id"],
            "lines": int(row["lines"]),
        }
        for row in rows
    ]


def create_doc(conn: sqlite3.Connection, warehouse_id: str, comment: str, author: str) -> dict:
    comment = comment.strip()
    author = author.strip()
    if not warehouse_id:
        raise InventoryError("Не указан склад", 400)
    if not comment:
        raise InventoryError("Не указан комментарий", 400)
    if not author:
        raise InventoryError("Не указан автор", 400)
    wh = conn.execute("SELECT id FROM warehouses WHERE id = ?", (warehouse_id,)).fetchone()
    if wh is None:
        raise InventoryError("Склад не найден в кеше", 404)
    dup = conn.execute(
        "SELECT id FROM sessions WHERE warehouse_id = ? AND comment = ? AND deleted = 0",
        (warehouse_id, comment),
    ).fetchone()
    if dup is not None:
        raise InventoryError("Комментарий уже используется на этом складе", 409)
    session_id = str(uuid.uuid4())
    now = utcnow()
    conn.execute(
        "INSERT INTO sessions(id, warehouse_id, comment, author, status, dirty_at, created_at) "
        "VALUES (?, ?, ?, ?, 'draft', ?, ?)",
        (session_id, warehouse_id, comment, author, now, now),
    )
    conn.commit()
    return {"id": session_id, "comment": comment, "author": author}


def delete_doc(conn: sqlite3.Connection, session_id: str) -> None:
    row = _session(conn, session_id)
    _assert_writable(row)
    conn.execute(
        "UPDATE sessions SET deleted = 1, status = 'deleted', dirty_at = NULL WHERE id = ?",
        (session_id,),
    )
    conn.commit()


def get_doc(conn: sqlite3.Connection, session_id: str) -> dict:
    row = _session(conn, session_id)
    items = conn.execute(
        "SELECT line, barcode, name, qty FROM lines WHERE session_id = ? ORDER BY line",
        (session_id,),
    ).fetchall()
    return {
        "id": row["id"],
        "comment": row["comment"],
        "author": row["author"],
        "status": row["status"],
        "onecId": row["onec_id"],
        "warehouse": row["warehouse_id"],
        "error": row["last_error"],
        "items": [
            {"line": int(item["line"]), "barcode": item["barcode"], "name": item["name"], "qty": item["qty"]}
            for item in items
        ],
    }


def scan(conn: sqlite3.Connection, session_id: str, barcode: str) -> dict:
    barcode = barcode.strip()
    if not barcode:
        raise InventoryError("Не указан barcode", 400)
    row = _session(conn, session_id)
    _assert_writable(row)
    found = find_barcode(conn, barcode)
    if found is None:
        raise InventoryError("Товар не найден", 404)
    conn.execute("BEGIN IMMEDIATE")
    try:
        existing = conn.execute(
            "SELECT line, qty FROM lines WHERE session_id = ? AND product_id = ?",
            (session_id, found["product_id"]),
        ).fetchone()
        created = existing is None
        if existing is None:
            max_line = conn.execute(
                "SELECT COALESCE(MAX(line), 0) AS n FROM lines WHERE session_id = ?",
                (session_id,),
            ).fetchone()["n"]
            line = int(max_line) + 1
            conn.execute(
                "INSERT INTO lines(session_id, line, product_id, barcode, name, qty, updated_at) "
                "VALUES (?, ?, ?, ?, ?, 0, ?)",
                (session_id, line, found["product_id"], found["barcode"], found["product_name"], utcnow()),
            )
            qty = 0.0
        else:
            line = int(existing["line"])
            qty = float(existing["qty"])
            conn.execute(
                "UPDATE lines SET barcode = ?, name = ?, updated_at = ? WHERE session_id = ? AND line = ?",
                (found["barcode"], found["product_name"], utcnow(), session_id, line),
            )
        conn.execute(
            "UPDATE sessions SET dirty_at = ?, status = 'draft', last_error = '' WHERE id = ?",
            (utcnow(), session_id),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return {
        "line": line,
        "name": found["product_name"],
        "qty": qty,
        "created": created,
        "barcode": found["barcode"],
    }


def set_qty(conn: sqlite3.Connection, session_id: str, line: int, qty: float) -> dict:
    if qty < 0:
        raise InventoryError("Количество не может быть меньше нуля", 400)
    row = _session(conn, session_id)
    _assert_writable(row)
    conn.execute("BEGIN IMMEDIATE")
    try:
        existing = conn.execute(
            "SELECT line FROM lines WHERE session_id = ? AND line = ?",
            (session_id, line),
        ).fetchone()
        if existing is None:
            conn.rollback()
            raise InventoryError("Строка не найдена", 404)
        conn.execute(
            "UPDATE lines SET qty = ?, updated_at = ? WHERE session_id = ? AND line = ?",
            (qty, utcnow(), session_id, line),
        )
        conn.execute(
            "UPDATE sessions SET dirty_at = ?, status = 'draft', last_error = '' WHERE id = ?",
            (utcnow(), session_id),
        )
        conn.commit()
    except InventoryError:
        raise
    except Exception:
        conn.rollback()
        raise
    return {"line": int(line), "qty": qty}


def dirty_sessions(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM sessions WHERE deleted = 0 AND dirty_at IS NOT NULL AND status != 'syncing'"
    ).fetchall()


def session_payload(conn: sqlite3.Connection, row: sqlite3.Row) -> dict:
    items = conn.execute(
        "SELECT product_id, barcode, qty FROM lines WHERE session_id = ? ORDER BY line",
        (row["id"],),
    ).fetchall()
    return {
        "externalId": row["id"],
        "warehouseId": row["warehouse_id"],
        "comment": row["comment"],
        "authorName": row["author"],
        "items": [
            {"productId": item["product_id"], "barcode": item["barcode"], "qty": item["qty"]}
            for item in items
        ],
    }


def mark_syncing(conn: sqlite3.Connection, session_id: str) -> None:
    conn.execute("UPDATE sessions SET status = 'syncing' WHERE id = ?", (session_id,))
    conn.commit()


def mark_synced(conn: sqlite3.Connection, session_id: str, onec_id: str) -> None:
    conn.execute(
        "UPDATE sessions SET status = 'synced', onec_id = ?, dirty_at = NULL, last_error = '' WHERE id = ?",
        (onec_id, session_id),
    )
    conn.commit()


def mark_error(conn: sqlite3.Connection, session_id: str, message: str) -> None:
    conn.execute(
        "UPDATE sessions SET status = 'error', last_error = ? WHERE id = ?",
        (message[:400], session_id),
    )
    conn.commit()
