# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import pytest
from starlette.testclient import TestClient

from app.catalog import apply_catalog
from app.config import Settings
from app.db import connect, init_schema
from app.main import create_app

WH = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
PID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"


class FakePtm:
    def __init__(self) -> None:
        self.health = True
        self.created: list[dict] = []
        self.replaced: list[tuple[str, dict]] = []
        self.fail_create = False

    async def ping_health(self) -> bool:
        return self.health

    async def pull_barcodes(self) -> list[dict]:
        return [{"barcode": "4820001111111", "productId": PID, "productName": "Молоко", "productCode": "0001"}]

    async def pull_warehouses(self) -> list[dict]:
        return [{"id": WH, "name": "Основной", "code": "000000001"}]

    async def pull_products(self) -> list[dict]:
        return [{"id": PID, "name": "Молоко", "code": "0001"}]

    async def create_inventory(self, body: dict) -> dict:
        if self.fail_create:
            from app.ptm_client import PtmApiError

            raise PtmApiError("1C down", status_code=502)
        self.created.append(body)
        return {"id": "cccccccc-cccc-cccc-cccc-cccccccccccc", "number": "000000001", "created": True}

    async def replace_inventory(self, inventory_id: str, body: dict) -> dict:
        self.replaced.append((inventory_id, body))
        return {"id": inventory_id, "number": "000000001", "created": False}


@pytest.fixture
def fake_ptm() -> FakePtm:
    return FakePtm()


@pytest.fixture
def client(tmp_path: Path, fake_ptm: FakePtm) -> TestClient:
    conn = connect(tmp_path / "test.db")
    init_schema(conn)
    apply_catalog(
        conn,
        [{"barcode": "4820001111111", "productId": PID, "productName": "Молоко", "productCode": "0001"}],
        [{"id": WH, "name": "Основной", "code": "000000001"}],
    )
    settings = Settings(
        secret="test-secret",
        db_path=tmp_path / "test.db",
        port=8091,
        cookie_secure=False,
        ptm_base_url="http://example.invalid/hs/ptm/v1",
        ptm_api_key="k",
        pull_sec=900,
        push_sec=180,
    )
    app = create_app(settings=settings, conn=conn, client_factory=lambda: fake_ptm, enable_background=False)
    with TestClient(app) as test_client:
        yield test_client


def login(client: TestClient) -> None:
    resp = client.post("/login", json={"username": "admin", "password": "secret"})
    assert resp.status_code == 200, resp.text
