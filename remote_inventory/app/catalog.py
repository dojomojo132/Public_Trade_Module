# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def apply_catalog(
    conn: sqlite3.Connection,
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
        conn.execute("DELETE FROM barcodes")
        for item in barcodes:
            barcode = str(item.get("barcode") or "").strip()
            product_id = str(item.get("productId") or "").strip()
            if not barcode or not product_id:
                continue
            name = str(item.get("productName") or "").strip() or names.get(product_id, "")
            code = str(item.get("productCode") or "").strip() or codes.get(product_id, "")
            conn.execute(
                "INSERT OR REPLACE INTO barcodes(barcode, product_id, product_name, product_code, pulled_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (barcode, product_id, name, code, pulled),
            )
        conn.execute("DELETE FROM warehouses")
        for item in warehouses:
            wid = str(item.get("id") or "").strip()
            if not wid:
                continue
            conn.execute(
                "INSERT OR REPLACE INTO warehouses(id, name, code, pulled_at) VALUES (?, ?, ?, ?)",
                (
                    wid,
                    str(item.get("name") or "").strip(),
                    str(item.get("code") or "").strip(),
                    pulled,
                ),
            )
        conn.execute(
            "INSERT INTO sync_meta(key, value) VALUES('catalog_pulled_at', ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (pulled,),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return {
        "barcodes": conn.execute("SELECT COUNT(*) AS n FROM barcodes").fetchone()["n"],
        "warehouses": conn.execute("SELECT COUNT(*) AS n FROM warehouses").fetchone()["n"],
        "pulled_at": pulled,
    }


def list_warehouses(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT id, name, code FROM warehouses ORDER BY name COLLATE NOCASE").fetchall()
    return [{"id": row["id"], "name": row["name"], "code": row["code"]} for row in rows]


def find_barcode(conn: sqlite3.Connection, barcode: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT barcode, product_id, product_name, product_code FROM barcodes WHERE barcode = ?",
        (barcode.strip(),),
    ).fetchone()
