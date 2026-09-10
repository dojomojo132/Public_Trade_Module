# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from app.inventory.schema import meta_set


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def apply_catalog(
    conn: sqlite3.Connection,
    user_id: int,
    barcodes: list[dict],
    warehouses: list[dict],
    products: list[dict] | None = None,
) -> dict:
    names: dict[str, str] = {}
    codes: dict[str, str] = {}
    for item in products or []:
        pid = str(item.get("id") or "").strip()
        if not pid:
            continue
        names[pid] = str(item.get("name") or "").strip()
        codes[pid] = str(item.get("code") or "").strip()

    pulled = utcnow()
    conn.execute("BEGIN IMMEDIATE")
    try:
        conn.execute("DELETE FROM inv_barcodes WHERE user_id = ?", (user_id,))
        for item in barcodes:
            barcode = str(item.get("barcode") or "").strip()
            product_id = str(item.get("productId") or "").strip()
            if not barcode or not product_id:
                continue
            name = str(item.get("productName") or "").strip() or names.get(product_id, "")
            code = str(item.get("productCode") or "").strip() or codes.get(product_id, "")
            conn.execute(
                "INSERT INTO inv_barcodes(user_id, barcode, product_id, product_name, product_code, pulled_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, barcode, product_id, name, code, pulled),
            )
        conn.execute("DELETE FROM inv_warehouses WHERE user_id = ?", (user_id,))
        for item in warehouses:
            wid = str(item.get("id") or "").strip()
            if not wid:
                continue
            conn.execute(
                "INSERT INTO inv_warehouses(user_id, id, name, code, pulled_at) VALUES (?, ?, ?, ?, ?)",
                (user_id, wid, str(item.get("name") or "").strip(), str(item.get("code") or "").strip(), pulled),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    meta_set(conn, user_id, "catalog_pulled_at", pulled)
    n_barcodes = conn.execute(
        "SELECT COUNT(*) AS n FROM inv_barcodes WHERE user_id = ?", (user_id,)
    ).fetchone()["n"]
    n_wh = conn.execute(
        "SELECT COUNT(*) AS n FROM inv_warehouses WHERE user_id = ?", (user_id,)
    ).fetchone()["n"]
    return {"barcodes": n_barcodes, "warehouses": n_wh, "pulled_at": pulled}


def list_warehouses(conn: sqlite3.Connection, user_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT id, name, code FROM inv_warehouses WHERE user_id = ? ORDER BY name COLLATE NOCASE",
        (user_id,),
    ).fetchall()
    return [{"id": row["id"], "name": row["name"], "code": row["code"]} for row in rows]


def find_barcode(conn: sqlite3.Connection, user_id: int, barcode: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT barcode, product_id, product_name, product_code FROM inv_barcodes "
        "WHERE user_id = ? AND barcode = ?",
        (user_id, barcode.strip()),
    ).fetchone()
