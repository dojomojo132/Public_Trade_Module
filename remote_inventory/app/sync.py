# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from typing import Protocol

from app import catalog, db, inventory
from app.ptm_client import PtmApiError, PtmClient


class ClientFactory(Protocol):
    def __call__(self) -> PtmClient: ...


async def pull_catalog(conn: sqlite3.Connection, client: PtmClient) -> dict:
    barcodes = await client.pull_barcodes()
    warehouses = await client.pull_warehouses()
    try:
        products = await client.pull_products()
    except PtmApiError:
        products = []
    result = catalog.apply_catalog(conn, barcodes, warehouses, products)
    return result


async def push_dirty(conn: sqlite3.Connection, client: PtmClient) -> dict:
    pushed = 0
    errors = 0
    for row in inventory.dirty_sessions(conn):
        inventory.mark_syncing(conn, row["id"])
        body = inventory.session_payload(conn, row)
        try:
            if row["onec_id"]:
                payload = await client.replace_inventory(str(row["onec_id"]), body)
            else:
                payload = await client.create_inventory(body)
            onec_id = str(payload.get("id") or row["onec_id"] or "")
            if not onec_id:
                raise PtmApiError("PTM API did not return inventory id")
            inventory.mark_synced(conn, row["id"], onec_id)
            pushed += 1
        except PtmApiError as exc:
            inventory.mark_error(conn, row["id"], str(exc))
            errors += 1
    db.meta_set(conn, "last_push_at", catalog.utcnow())
    db.meta_set(conn, "last_push_ok", "1" if errors == 0 else "0")
    return {"pushed": pushed, "errors": errors}


async def sync_now(conn: sqlite3.Connection, client: PtmClient, *, pull: bool = True, push: bool = True) -> dict:
    result: dict = {"pull": None, "push": None, "online": True}
    try:
        if pull:
            result["pull"] = await pull_catalog(conn, client)
        if push:
            result["push"] = await push_dirty(conn, client)
    except PtmApiError as exc:
        result["online"] = False
        result["error"] = str(exc)
    return result
