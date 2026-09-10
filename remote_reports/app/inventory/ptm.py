# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Protocol


class PtmApiError(Exception):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


class InventoryPtm(Protocol):
    async def ping_health(self) -> bool: ...
    async def pull_barcodes(self) -> list[dict]: ...
    async def pull_warehouses(self) -> list[dict]: ...
    async def pull_products(self) -> list[dict]: ...
    async def create_inventory(self, body: dict) -> dict: ...
    async def replace_inventory(self, inventory_id: str, body: dict) -> dict: ...


class ReportsPtmAdapter:
    """Wraps remote_reports PtmClient (fetch_all_pages + _http)."""

    def __init__(self, client: Any) -> None:
        self._c = client

    async def ping_health(self) -> bool:
        if not hasattr(self._c, "ping_health"):
            return False
        try:
            return bool(await self._c.ping_health())
        except Exception:
            return False

    async def pull_barcodes(self) -> list[dict]:
        return await self._c.fetch_all_pages("/barcodes")

    async def pull_warehouses(self) -> list[dict]:
        return await self._c.fetch_all_pages("/warehouses")

    async def pull_products(self) -> list[dict]:
        return await self._c.fetch_all_pages("/products")

    async def create_inventory(self, body: dict) -> dict:
        return await self._json("POST", "/inventories", json=body)

    async def replace_inventory(self, inventory_id: str, body: dict) -> dict:
        return await self._json("PUT", f"/inventories/{inventory_id}", json=body)

    async def _json(self, method: str, path: str, **kwargs: Any) -> dict:
        try:
            if hasattr(self._c, "_request"):
                data = await self._c._request(method, path, **kwargs)
            else:
                data = await self._http_fallback(method, path, **kwargs)
        except PtmApiError:
            raise
        except Exception as exc:
            status = getattr(exc, "status_code", 502)
            try:
                status = int(status)
            except (TypeError, ValueError):
                status = 502
            raise PtmApiError(str(exc), status) from exc
        if not isinstance(data, dict):
            raise PtmApiError("PTM API returned unexpected payload")
        return data

    async def _http_fallback(self, method: str, path: str, **kwargs: Any) -> dict:
        http = getattr(self._c, "_http", None)
        base = str(getattr(self._c, "_base", "")).rstrip("/")
        if http is None or not base:
            raise PtmApiError("PTM client cannot write inventories")
        headers = self._c._headers() if hasattr(self._c, "_headers") else {}
        try:
            response = await http.request(method, base + path, headers=headers, **kwargs)
        except Exception as exc:
            raise PtmApiError(f"PTM API unreachable: {exc}") from exc
        if response.status_code >= 400:
            raise PtmApiError(
                f"PTM API {response.status_code}: {response.text[:400]}",
                response.status_code,
            )
        if not getattr(response, "content", b"1"):
            return {}
        data = response.json()
        if not isinstance(data, dict):
            raise PtmApiError("PTM API returned unexpected payload")
        return data
