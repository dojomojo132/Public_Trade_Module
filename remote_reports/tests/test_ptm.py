# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio

import pytest

from app.inventory.ptm import PtmApiError, ReportsPtmAdapter


class ReportsLikeClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    async def ping_health(self) -> bool:
        return True

    async def fetch_all_pages(self, path: str, params=None):
        if path == "/barcodes":
            return [{"barcode": "1", "productId": "p"}]
        if path == "/warehouses":
            return [{"id": "w", "name": "Склад"}]
        return []

    async def _request(self, method: str, path: str, **kwargs):
        self.calls.append((method, path))
        if method == "POST":
            return {"id": "inv-1", "created": True}
        return {"id": "inv-1", "created": False}


def test_adapter_uses_reports_ptm_client() -> None:
    raw = ReportsLikeClient()
    client = ReportsPtmAdapter(raw)

    async def run() -> None:
        assert await client.ping_health() is True
        assert await client.pull_barcodes() == [{"barcode": "1", "productId": "p"}]
        created = await client.create_inventory({"externalId": "s1"})
        assert created["id"] == "inv-1"
        assert raw.calls == [("POST", "/inventories")]
        replaced = await client.replace_inventory("inv-1", {"externalId": "s1"})
        assert replaced["created"] is False

    asyncio.run(run())


def test_adapter_maps_write_errors() -> None:
    class Boom:
        async def _request(self, method, path, **kwargs):
            err = RuntimeError("PTM API 400: unknown product")
            err.status_code = 400
            raise err

    async def run() -> None:
        with pytest.raises(PtmApiError) as caught:
            await ReportsPtmAdapter(Boom()).create_inventory({})
        assert caught.value.status_code == 400

    asyncio.run(run())
