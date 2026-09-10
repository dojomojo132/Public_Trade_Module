# -*- coding: utf-8 -*-
from __future__ import annotations

from tests.conftest import BARCODE, PID, WH


def test_push_create_then_replace(client, fake_ptm) -> None:
    doc_id = client.post("/inv/docs", json={"warehouse": WH, "comment": "Синк", "author": "Иван"}).json()["id"]
    scan = client.post("/inv/scan", json={"id": doc_id, "barcode": BARCODE})
    client.post("/inv/qty", json={"id": doc_id, "line": scan.json()["line"], "qty": 3})
    synced = client.post("/inv/sync")
    assert synced.status_code == 200, synced.text
    assert len(fake_ptm.created) == 1
    assert fake_ptm.created[0]["externalId"] == doc_id
    assert fake_ptm.created[0]["items"][0]["productId"] == PID
    doc = client.get("/inv/doc", params={"id": doc_id}).json()
    assert doc["status"] == "synced"
    client.post("/inv/qty", json={"id": doc_id, "line": scan.json()["line"], "qty": 8})
    assert client.post("/inv/sync").status_code == 200
    assert len(fake_ptm.replaced) == 1
    assert fake_ptm.replaced[0][1]["items"][0]["qty"] == 8


def test_push_keeps_cache_on_1c_error(client, fake_ptm) -> None:
    fake_ptm.fail_create = True
    doc_id = client.post("/inv/docs", json={"warehouse": WH, "comment": "Офлайн", "author": "Иван"}).json()["id"]
    scan = client.post("/inv/scan", json={"id": doc_id, "barcode": BARCODE})
    client.post("/inv/qty", json={"id": doc_id, "line": scan.json()["line"], "qty": 1})
    client.post("/inv/sync")
    doc = client.get("/inv/doc", params={"id": doc_id}).json()
    assert doc["status"] == "error"
    assert doc["items"][0]["qty"] == 1
    assert client.post("/inv/scan", json={"id": doc_id, "barcode": BARCODE}).status_code == 200
