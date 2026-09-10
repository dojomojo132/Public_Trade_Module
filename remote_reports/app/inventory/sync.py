# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3

from app.inventory import catalog, service
from app.inventory.ptm import InventoryPtm, PtmApiError
from app.inventory.schema import meta_set


async def pull_catalog(conn: sqlite3.Connection, user_id: int, client: InventoryPtm) -> dict:
    barcodes = await client.pull_barcodes()
    warehouses = await client.pull_warehouses()
    try:
        products = await client.pull_products()
    except PtmApiError:
        products = []
    return catalog.apply_catalog(conn, user_id, barcodes, warehouses, products)


async def push_dirty(conn: sqlite3.Connection, user_id: int, client: InventoryPtm) -> dict:
    pushed = 0
    errors = 0
    for row in service.dirty_sessions(conn, user_id):
        service.mark_syncing(conn, row["id"])
        body = service.session_payload(conn, row)
        try:
            if row["onec_id"]:
                payload = await client.replace_inventory(str(row["onec_id"]), body)
            else:
                payload = await client.create_inventory(body)
            onec_id = str(payload.get("id") or row["onec_id"] or "")
            if not onec_id:
                raise PtmApiError("PTM API did not return inventory id")
            service.mark_synced(conn, row["id"], onec_id)
            pushed += 1
        except PtmApiError as exc:
            service.mark_error(conn, row["id"], str(exc))
            errors += 1
    meta_set(conn, user_id, "last_push_at", catalog.utcnow())
    meta_set(conn, user_id, "last_push_ok", "1" if errors == 0 else "0")
    return {"pushed": pushed, "errors": errors}


async def sync_now(conn: sqlite3.Connection, user_id: int, client: InventoryPtm) -> dict:
    result: dict = {"pull": None, "push": None, "online": True}
    try:
        result["pull"] = await pull_catalog(conn, user_id, client)
        result["push"] = await push_dirty(conn, user_id, client)
    except PtmApiError as exc:
        result["online"] = False
        result["error"] = str(exc)
    return result
