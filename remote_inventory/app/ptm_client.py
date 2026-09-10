# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any

import httpx

PAGE_LIMIT = 1000


class PtmApiError(Exception):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


class PtmClient:
    def __init__(self, http: httpx.AsyncClient, base_url: str, api_key: str) -> None:
        self._http = http
        self._base = base_url.rstrip("/")
        self._api_key = api_key

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json", "Content-Type": "application/json; charset=utf-8"}
        if self._api_key:
            headers["X-Api-Key"] = self._api_key
        return headers

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict:
        url = f"{self._base}{path}"
        try:
            response = await self._http.request(method, url, headers=self._headers(), **kwargs)
        except httpx.HTTPError as exc:
            raise PtmApiError(f"PTM API unreachable: {exc}") from exc
        if response.status_code >= 400:
            detail = response.text[:400]
            raise PtmApiError(f"PTM API {response.status_code}: {detail}", status_code=response.status_code)
        if not response.content:
            return {}
        try:
            data = response.json()
        except ValueError as exc:
            raise PtmApiError("PTM API returned non-JSON") from exc
        if not isinstance(data, dict):
            raise PtmApiError("PTM API returned unexpected payload")
        return data

    async def fetch_all_pages(self, path: str, params: dict[str, Any] | None = None) -> list[dict]:
        offset = 0
        items: list[dict] = []
        while True:
            page_params = dict(params or {})
            page_params["limit"] = PAGE_LIMIT
            page_params["offset"] = offset
            payload = await self._request("GET", path, params=page_params)
            page = payload.get("items") or []
            items.extend(page)
            total = int(payload.get("total") or 0)
            count = int(payload.get("count") or len(page))
            if not page or offset + count >= total or count < PAGE_LIMIT:
                break
            offset += count
        return items

    async def ping_health(self) -> bool:
        try:
            payload = await self._request("GET", "/health")
        except PtmApiError:
            return False
        return str(payload.get("status") or "") == "ok"

    async def pull_barcodes(self) -> list[dict]:
        return await self.fetch_all_pages("/barcodes")

    async def pull_warehouses(self) -> list[dict]:
        return await self.fetch_all_pages("/warehouses")

    async def pull_products(self) -> list[dict]:
        return await self.fetch_all_pages("/products")

    async def create_inventory(self, body: dict) -> dict:
        return await self._request("POST", "/inventories", json=body)

    async def replace_inventory(self, inventory_id: str, body: dict) -> dict:
        return await self._request("PUT", f"/inventories/{inventory_id}", json=body)
