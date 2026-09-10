# -*- coding: utf-8 -*-
from __future__ import annotations

from tests.conftest import PID, WH, login


def test_push_create_then_replace(client, fake_ptm) -> None:
    login(client)
    doc_id = client.post("/inv/docs", json={"warehouse": WH, "comment": "Синк", "author": "Иван"}).json()["id"]
    scan = client.post("/inv/scan", json={"id": doc_id, "barcode": "4820001111111"})
    client.post("/inv/qty", json={"id": doc_id, "line": scan.json()["line"], "qty": 3})
    synced = client.post("/inv/sync")
    assert synced.status_code == 200
    assert len(fake_ptm.created) == 1
    payload = fake_ptm.created[0]
    assert payload["externalId"] == doc_id
    assert payload["warehouseId"] == WH
    assert payload["items"][0]["productId"] == PID
    assert payload["items"][0]["qty"] == 3
    doc = client.get("/inv/doc", params={"id": doc_id}).json()
    assert doc["status"] == "synced"
    assert doc["onecId"]

    client.post("/inv/qty", json={"id": doc_id, "line": scan.json()["line"], "qty": 8})
    synced2 = client.post("/inv/sync")
    assert synced2.status_code == 200
    assert len(fake_ptm.created) == 1
    assert len(fake_ptm.replaced) == 1
    assert fake_ptm.replaced[0][0] == doc["onecId"]
    assert fake_ptm.replaced[0][1]["items"][0]["qty"] == 8


def test_push_keeps_cache_on_1c_error(client, fake_ptm) -> None:
    login(client)
    fake_ptm.fail_create = True
    doc_id = client.post("/inv/docs", json={"warehouse": WH, "comment": "Офлайн", "author": "Иван"}).json()["id"]
    scan = client.post("/inv/scan", json={"id": doc_id, "barcode": "4820001111111"})
    client.post("/inv/qty", json={"id": doc_id, "line": scan.json()["line"], "qty": 1})
    resp = client.post("/inv/sync")
    assert resp.status_code == 200
    doc = client.get("/inv/doc", params={"id": doc_id}).json()
    assert doc["status"] == "error"
    assert doc["items"][0]["qty"] == 1
    scan_again = client.post("/inv/scan", json={"id": doc_id, "barcode": "4820001111111"})
    assert scan_again.status_code == 200
