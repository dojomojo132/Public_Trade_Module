# -*- coding: utf-8 -*-
from __future__ import annotations

from tests.conftest import BARCODE, WH


def test_inv_page_html(client) -> None:
    resp = client.get("/inv")
    assert resp.status_code == 200
    assert "Переучёт" in resp.text
    assert "/static/app.css" in resp.text
    assert "/inv/static/inv.js" in resp.text
    client.cookies.clear()
    resp = client.get("/inv", follow_redirects=False)
    assert resp.status_code in {302, 307}
    assert "/login" in resp.headers.get("location", "")


def test_api_requires_login_json(client) -> None:
    client.cookies.clear()
    resp = client.get("/inv/status")
    assert resp.status_code == 401
    body = resp.json()
    assert body["success"] is False
    assert body["login"] == "/login"


def test_status_after_login(client) -> None:
    r = client.get("/inv/status")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["ibConfigured"] is True
    assert body["barcodeCount"] == 1


def test_unknown_barcode(client) -> None:
    created = client.post("/inv/docs", json={"warehouse": WH, "comment": "Молочка", "author": "Иван"})
    assert created.status_code == 200, created.text
    doc_id = created.json()["id"]
    resp = client.post("/inv/scan", json={"id": doc_id, "barcode": "000"})
    assert resp.status_code == 404
    assert client.get("/inv/doc", params={"id": doc_id}).json()["items"] == []


def test_scan_creates_zero_qty_then_replace(client) -> None:
    doc_id = client.post("/inv/docs", json={"warehouse": WH, "comment": "А", "author": "Иван"}).json()["id"]
    scan1 = client.post("/inv/scan", json={"id": doc_id, "barcode": BARCODE})
    assert scan1.json()["created"] is True
    assert scan1.json()["qty"] == 0
    line = scan1.json()["line"]
    client.post("/inv/qty", json={"id": doc_id, "line": line, "qty": 4.5})
    scan2 = client.post("/inv/scan", json={"id": doc_id, "barcode": BARCODE})
    assert scan2.json()["created"] is False
    assert scan2.json()["qty"] == 4.5
    client.post("/inv/qty", json={"id": doc_id, "line": line, "qty": 2})
    items = client.get("/inv/doc", params={"id": doc_id}).json()["items"]
    assert len(items) == 1
    assert items[0]["qty"] == 2


def test_duplicate_comment(client) -> None:
    assert client.post("/inv/docs", json={"warehouse": WH, "comment": "Отдел", "author": "А"}).status_code == 200
    assert client.post("/inv/docs", json={"warehouse": WH, "comment": "Отдел", "author": "Б"}).status_code == 409


def test_delete_draft(client) -> None:
    doc_id = client.post("/inv/docs", json={"warehouse": WH, "comment": "X", "author": "Иван"}).json()["id"]
    gone = client.delete("/inv/docs", params={"id": doc_id})
    assert gone.status_code == 200
    listed = client.get("/inv/docs", params={"warehouse": WH})
    assert listed.json()["items"] == []


def test_scan_works_when_1c_offline(client, fake_ptm) -> None:
    fake_ptm.health = False
    doc_id = client.post("/inv/docs", json={"warehouse": WH, "comment": "Офлайн-скан", "author": "Иван"}).json()["id"]
    resp = client.post("/inv/scan", json={"id": doc_id, "barcode": BARCODE})
    assert resp.status_code == 200
    assert client.get("/inv/status").json()["online"] is False


def test_users_do_not_share_cache(client) -> None:
    created = client.post("/inv/docs", json={"warehouse": WH, "comment": "Только админ", "author": "Иван"})
    assert created.status_code == 200
    conn = client.app.state.conn
    conn.execute("INSERT INTO users(username, password) VALUES (?, ?)", ("other", "pw"))
    conn.commit()
    client.cookies.clear()
    login = client.post("/login", json={"username": "other", "password": "pw"})
    assert login.status_code == 200, login.text
    warehouses = client.get("/inv/warehouses")
    assert warehouses.status_code == 200
    assert warehouses.json()["items"] == []
    listed = client.get("/inv/docs", params={"warehouse": WH})
    assert listed.json()["items"] == []


def test_sync_without_ib_settings(client_no_ib) -> None:
    status = client_no_ib.get("/inv/status").json()
    assert status["ibConfigured"] is False
    assert status["online"] is False
    synced = client_no_ib.post("/inv/sync")
    assert synced.status_code == 503
    assert "ИБ" in synced.json()["error"]
