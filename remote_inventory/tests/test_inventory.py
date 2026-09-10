# -*- coding: utf-8 -*-
from __future__ import annotations

from tests.conftest import PID, WH, login


def test_unknown_barcode(client) -> None:
    login(client)
    created = client.post("/inv/docs", json={"warehouse": WH, "comment": "Молочка", "author": "Иван"})
    assert created.status_code == 200
    doc_id = created.json()["id"]
    resp = client.post("/inv/scan", json={"id": doc_id, "barcode": "000"})
    assert resp.status_code == 404
    assert resp.json()["success"] is False
    doc = client.get("/inv/doc", params={"id": doc_id})
    assert doc.json()["items"] == []


def test_scan_creates_zero_qty_then_replace(client) -> None:
    login(client)
    doc_id = client.post("/inv/docs", json={"warehouse": WH, "comment": "А", "author": "Иван"}).json()["id"]
    scan1 = client.post("/inv/scan", json={"id": doc_id, "barcode": "4820001111111"})
    assert scan1.status_code == 200
    body = scan1.json()
    assert body["created"] is True
    assert body["qty"] == 0
    line = body["line"]
    qty = client.post("/inv/qty", json={"id": doc_id, "line": line, "qty": 4.5})
    assert qty.json()["qty"] == 4.5
    scan2 = client.post("/inv/scan", json={"id": doc_id, "barcode": "4820001111111"})
    assert scan2.json()["created"] is False
    assert scan2.json()["qty"] == 4.5
    assert scan2.json()["line"] == line
    client.post("/inv/qty", json={"id": doc_id, "line": line, "qty": 2})
    items = client.get("/inv/doc", params={"id": doc_id}).json()["items"]
    assert len(items) == 1
    assert items[0]["qty"] == 2


def test_duplicate_comment(client) -> None:
    login(client)
    first = client.post("/inv/docs", json={"warehouse": WH, "comment": "Отдел", "author": "А"})
    assert first.status_code == 200
    second = client.post("/inv/docs", json={"warehouse": WH, "comment": "Отдел", "author": "Б"})
    assert second.status_code == 409


def test_delete_draft(client) -> None:
    login(client)
    doc_id = client.post("/inv/docs", json={"warehouse": WH, "comment": "X", "author": "Иван"}).json()["id"]
    gone = client.delete("/inv/docs", params={"id": doc_id})
    assert gone.status_code == 200
    listed = client.get("/inv/docs", params={"warehouse": WH})
    assert listed.json()["items"] == []
