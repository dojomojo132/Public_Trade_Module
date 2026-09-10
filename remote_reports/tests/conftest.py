# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from app.inventory.catalog import apply_catalog
from app.inventory.demo_app import create_demo_app
from app.inventory.ptm import PtmApiError

WH = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
PID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
BARCODE = "4820001111111"
CATALOG_BC = [{"barcode": BARCODE, "productId": PID, "productName": "Молоко", "productCode": "0001"}]
CATALOG_WH = [{"id": WH, "name": "Основной", "code": "000000001"}]


class FakePtm:
    def __init__(self) -> None:
        self.health = True
        self.created: list[dict] = []
        self.replaced: list[tuple[str, dict]] = []
        self.fail_create = False

    async def ping_health(self) -> bool:
        return self.health

    async def pull_barcodes(self) -> list[dict]:
        return list(CATALOG_BC)

    async def pull_warehouses(self) -> list[dict]:
        return list(CATALOG_WH)

    async def pull_products(self) -> list[dict]:
        return [{"id": PID, "name": "Молоко", "code": "0001"}]

    async def create_inventory(self, body: dict) -> dict:
        if self.fail_create:
            raise PtmApiError("1C down", status_code=502)
        self.created.append(body)
        return {"id": "cccccccc-cccc-cccc-cccc-cccccccccccc", "number": "000000001", "created": True}

    async def replace_inventory(self, inventory_id: str, body: dict) -> dict:
        self.replaced.append((inventory_id, body))
        return {"id": inventory_id, "number": "000000001", "created": False}


def _conn(tmp_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(tmp_path / "t.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@pytest.fixture
def fake_ptm() -> FakePtm:
    return FakePtm()


@pytest.fixture
def client(tmp_path: Path, fake_ptm: FakePtm) -> TestClient:
    conn = _conn(tmp_path)
    app = create_demo_app(conn, "test-secret", lambda: fake_ptm)
    with TestClient(app) as test_client:
        test_client.post("/login", json={"username": "admin", "password": "secret"})
        uid = int(conn.execute("SELECT id FROM users WHERE username = 'admin'").fetchone()["id"])
        apply_catalog(conn, uid, CATALOG_BC, CATALOG_WH)
        yield test_client


@pytest.fixture
def client_no_ib(tmp_path: Path) -> TestClient:
    conn = _conn(tmp_path)
    app = create_demo_app(conn, "test-secret", lambda: None)
    with TestClient(app) as test_client:
        test_client.post("/login", json={"username": "admin", "password": "secret"})
        yield test_client
