# -*- coding: utf-8 -*-
from __future__ import annotations


def test_home_has_inventory_card(client) -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Переучёт" in resp.text
    assert 'href="/inv"' in resp.text
    assert 'href="/reports/sales"' in resp.text


def test_settings_saves_ib(client) -> None:
    get = client.get("/settings")
    assert get.status_code == 200
    assert "Информационная база" in get.text
    saved = client.post(
        "/settings",
        data={"ib_location": "http://127.0.0.1:18091/DB/hs/ptm/v1", "api_key": "k"},
        follow_redirects=False,
    )
    assert saved.status_code == 303
    again = client.get("/settings")
    assert "18091" in again.text


def test_ib_status_online_with_fake(client) -> None:
    resp = client.get("/ib-status")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_ib_status_unset_without_client(client_no_ib) -> None:
    resp = client_no_ib.get("/ib-status")
    assert resp.status_code == 200
    assert resp.json()["status"] == "unset"


def test_login_page_matches_live_copy(client) -> None:
    client.cookies.clear()
    resp = client.get("/login")
    assert resp.status_code == 200
    assert "Учётка сервиса, не пользователь 1С" in resp.text
    assert 'name="username"' in resp.text
