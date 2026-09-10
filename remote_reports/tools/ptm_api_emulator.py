# -*- coding: utf-8 -*-
"""PTM_API emulator — stands in for a live 1С:Предприятие publication.

Implements the frozen ``/hs/ptm/v1`` contract (see ``Документация/API/openapi-v1.yaml``)
closely enough for the remote_reports host to talk to it over real HTTP:

* ``X-Api-Key`` auth on every route except ``/health``
* ``ListMeta`` envelope (``items/count/limit/offset/total``) with pagination
* mandatory period on ``/sales`` (``400 period_required`` otherwise)
* idempotent ``POST /inventories`` (upsert by ``externalId``) and ``PUT /inventories/{id}``

Read endpoints also carry denormalised name fields (``productName``,
``warehouseName``, ``cashRegisterName``, ``priceTypeName``) plus a ``qty`` alias
next to the contract ``quantity`` so the reports tables render populated.

Run:
    python -m uvicorn tools.ptm_api_emulator:build --factory --host 127.0.0.1 --port 18091
Env:
    PTM_API_KEY   shared secret expected in X-Api-Key (default: demo-key-123)
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

API_KEY = os.environ.get("PTM_API_KEY", "demo-key-123")
VERSION = "1.0.0-emulator"

WH_MAIN = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
WH_HALL = "dddddddd-dddd-dddd-dddd-dddddddddddd"
PID_MILK = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
PID_BREAD = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"
PID_WATER = "ffffffff-ffff-ffff-ffff-ffffffffffff"
CR_MAIN = "11111111-1111-1111-1111-111111111111"
PT_RETAIL = "22222222-2222-2222-2222-222222222222"

PRODUCTS = [
    {"id": PID_MILK, "code": "0001", "name": "Молоко 2.5% 1л", "unit": "шт", "deletionMark": False, "isFolder": False},
    {"id": PID_BREAD, "code": "0002", "name": "Хлеб Бородинский", "unit": "шт", "deletionMark": False, "isFolder": False},
    {"id": PID_WATER, "code": "0003", "name": "Вода негаз. 0.5л", "unit": "шт", "deletionMark": False, "isFolder": False},
]
PRODUCT_NAME = {p["id"]: p["name"] for p in PRODUCTS}

WAREHOUSES = [
    {"id": WH_MAIN, "code": "000000001", "name": "Основной склад", "deletionMark": False},
    {"id": WH_HALL, "code": "000000002", "name": "Торговый зал", "deletionMark": False},
]
WAREHOUSE_NAME = {w["id"]: w["name"] for w in WAREHOUSES}

CASH_REGISTERS = [{"id": CR_MAIN, "code": "000000001", "name": "Касса 1", "deletionMark": False}]
CASH_NAME = {c["id"]: c["name"] for c in CASH_REGISTERS}
PRICE_TYPES = [{"id": PT_RETAIL, "code": "000000001", "name": "Розничная", "deletionMark": False}]
PRICE_TYPE_NAME = {p["id"]: p["name"] for p in PRICE_TYPES}

BARCODES = [
    {"barcode": "4820001111111", "productId": PID_MILK, "productCode": "0001", "productName": "Молоко 2.5% 1л"},
    {"barcode": "4820002222222", "productId": PID_BREAD, "productCode": "0002", "productName": "Хлеб Бородинский"},
    {"barcode": "4820003333333", "productId": PID_WATER, "productCode": "0003", "productName": "Вода негаз. 0.5л"},
]

PRICES = [
    {"productId": PID_MILK, "productName": "Молоко 2.5% 1л", "priceTypeId": PT_RETAIL, "priceTypeName": "Розничная", "price": 42.50},
    {"productId": PID_BREAD, "productName": "Хлеб Бородинский", "priceTypeId": PT_RETAIL, "priceTypeName": "Розничная", "price": 28.90},
    {"productId": PID_WATER, "productName": "Вода негаз. 0.5л", "priceTypeId": PT_RETAIL, "priceTypeName": "Розничная", "price": 15.00},
]

STOCKS = [
    {"warehouseId": WH_MAIN, "productId": PID_MILK, "quantity": 120, "warehouseName": "Основной склад", "productName": "Молоко 2.5% 1л"},
    {"warehouseId": WH_MAIN, "productId": PID_BREAD, "quantity": 64, "warehouseName": "Основной склад", "productName": "Хлеб Бородинский"},
    {"warehouseId": WH_HALL, "productId": PID_WATER, "quantity": 210, "warehouseName": "Торговый зал", "productName": "Вода негаз. 0.5л"},
]

CASH_BALANCES = [{"cashRegisterId": CR_MAIN, "cashRegisterName": "Касса 1", "amount": 15230.75}]

# In-memory inventory store: id -> record; externalId -> id
_INV_BY_ID: dict[str, dict] = {}
_INV_BY_EXT: dict[str, str] = {}
_INV_SEQ = 0


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _err(request: Request, code: str, message: str, status: int) -> JSONResponse:
    rid = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    return JSONResponse({"code": code, "message": message, "requestId": rid}, status_code=status, headers={"X-Request-Id": rid})


def _auth_ok(request: Request) -> bool:
    return request.headers.get("X-Api-Key", "") == API_KEY


def _page(request: Request, rows: list[dict]) -> JSONResponse:
    qp = request.query_params
    try:
        limit = min(int(qp.get("limit", 100)), 1000)
        offset = int(qp.get("offset", 0))
    except ValueError:
        return _err(request, "validation_error", "limit/offset must be integers", 400)
    window = rows[offset : offset + limit]
    rid = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    return JSONResponse(
        {"items": window, "count": len(window), "limit": limit, "offset": offset, "total": len(rows)},
        headers={"X-Request-Id": rid},
    )


def _guard(handler):
    async def wrapped(request: Request):
        if not _auth_ok(request):
            return _err(request, "unauthorized", "Missing or invalid X-Api-Key", 401)
        return await handler(request)

    return wrapped


async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "version": VERSION, "time": _now()})


@_guard
async def products(request: Request):
    return _page(request, PRODUCTS)


@_guard
async def warehouses(request: Request):
    return _page(request, WAREHOUSES)


@_guard
async def cash_registers(request: Request):
    return _page(request, CASH_REGISTERS)


@_guard
async def price_types(request: Request):
    return _page(request, PRICE_TYPES)


@_guard
async def barcodes(request: Request):
    return _page(request, BARCODES)


@_guard
async def prices(request: Request):
    return _page(request, PRICES)


@_guard
async def stocks(request: Request):
    rows = [dict(r, qty=r["quantity"], onDate=_now()) for r in STOCKS]
    return _page(request, rows)


@_guard
async def cash_balances(request: Request):
    rows = [dict(r, onDate=_now()) for r in CASH_BALANCES]
    return _page(request, rows)


@_guard
async def sales(request: Request):
    qp = request.query_params
    date_from = qp.get("dateFrom")
    date_to = qp.get("dateTo")
    if not date_from or not date_to:
        return _err(request, "period_required", "dateFrom and dateTo are required for /sales", 400)
    day = str(date_from)[:10]
    rows = [
        {"productId": PID_MILK, "productName": "Молоко 2.5% 1л", "cashRegisterId": CR_MAIN,
         "cashRegisterName": "Касса 1", "quantity": 18, "qty": 18, "amount": 765.0, "date": day, "period": date_from},
        {"productId": PID_BREAD, "productName": "Хлеб Бородинский", "cashRegisterId": CR_MAIN,
         "cashRegisterName": "Касса 1", "quantity": 25, "qty": 25, "amount": 722.5, "date": day, "period": date_from},
    ]
    return _page(request, rows)


def _inv_response(request: Request, rec: dict, status: int) -> JSONResponse:
    rid = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    body = {"id": rec["id"], "number": rec["number"], "externalId": rec.get("externalId"), "created": status == 201}
    headers = {"X-Request-Id": rid}
    if status == 201:
        headers["Location"] = f"/hs/ptm/v1/inventories/{rec['id']}"
    return JSONResponse(body, status_code=status, headers=headers)


def _validate_inv(body: dict) -> tuple[str, str] | None:
    if not isinstance(body, dict):
        return "validation_error", "body must be an object"
    if not str(body.get("warehouseId") or "").strip():
        return "validation_error", "warehouseId is required"
    if str(body.get("warehouseId")) not in WAREHOUSE_NAME:
        return "validation_error", f"unknown warehouseId {body.get('warehouseId')}"
    for item in body.get("items") or []:
        pid = str(item.get("productId") or "")
        if pid and pid not in PRODUCT_NAME:
            return "validation_error", f"unknown productId {pid}"
        try:
            if float(item.get("qty", 0)) < 0:
                return "validation_error", "qty must be >= 0"
        except (TypeError, ValueError):
            return "validation_error", "qty must be a number"
    return None


@_guard
async def inventories_create(request: Request):
    global _INV_SEQ
    try:
        body = await request.json()
    except Exception:
        return _err(request, "validation_error", "invalid JSON", 400)
    problem = _validate_inv(body)
    if problem:
        return _err(request, problem[0], problem[1], 400)
    ext = str(body.get("externalId") or "").strip()
    if ext and ext in _INV_BY_EXT:
        inv_id = _INV_BY_EXT[ext]
        rec = _INV_BY_ID[inv_id]
        rec.update(warehouseId=body["warehouseId"], comment=body.get("comment", ""),
                   authorName=body.get("authorName", ""), items=body.get("items") or [], updatedAt=_now())
        return _inv_response(request, rec, 200)
    _INV_SEQ += 1
    inv_id = str(uuid.uuid4())
    rec = {
        "id": inv_id, "number": f"{_INV_SEQ:09d}", "externalId": ext or None,
        "warehouseId": body["warehouseId"], "comment": body.get("comment", ""),
        "authorName": body.get("authorName", ""), "items": body.get("items") or [],
        "posted": False, "createdAt": _now(),
    }
    _INV_BY_ID[inv_id] = rec
    if ext:
        _INV_BY_EXT[ext] = inv_id
    return _inv_response(request, rec, 201)


@_guard
async def inventory_replace(request: Request):
    inv_id = request.path_params["id"]
    rec = _INV_BY_ID.get(inv_id)
    if rec is None:
        return _err(request, "not_found", f"inventory {inv_id} not found", 404)
    if rec.get("posted"):
        return _err(request, "conflict", "inventory is posted and not writable", 409)
    try:
        body = await request.json()
    except Exception:
        return _err(request, "validation_error", "invalid JSON", 400)
    problem = _validate_inv(body)
    if problem:
        return _err(request, problem[0], problem[1], 400)
    rec.update(warehouseId=body["warehouseId"], comment=body.get("comment", ""),
               authorName=body.get("authorName", ""), items=body.get("items") or [], updatedAt=_now())
    return _inv_response(request, rec, 200)


def build() -> Starlette:
    routes = [
        Route("/hs/ptm/v1/health", health, methods=["GET"]),
        Route("/hs/ptm/v1/products", products, methods=["GET"]),
        Route("/hs/ptm/v1/warehouses", warehouses, methods=["GET"]),
        Route("/hs/ptm/v1/cash-registers", cash_registers, methods=["GET"]),
        Route("/hs/ptm/v1/price-types", price_types, methods=["GET"]),
        Route("/hs/ptm/v1/barcodes", barcodes, methods=["GET"]),
        Route("/hs/ptm/v1/prices", prices, methods=["GET"]),
        Route("/hs/ptm/v1/stocks", stocks, methods=["GET"]),
        Route("/hs/ptm/v1/cash-balances", cash_balances, methods=["GET"]),
        Route("/hs/ptm/v1/sales", sales, methods=["GET"]),
        Route("/hs/ptm/v1/inventories", inventories_create, methods=["POST"]),
        Route("/hs/ptm/v1/inventories/{id}", inventory_replace, methods=["PUT"]),
    ]
    return Starlette(routes=routes)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(build(), host="127.0.0.1", port=int(os.environ.get("PORT", "18091")))
