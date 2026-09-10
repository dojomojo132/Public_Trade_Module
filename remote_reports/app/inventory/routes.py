# -*- coding: utf-8 -*-
"""Drop-in inventory routes for reports.dojomyassiste.uno."""
from __future__ import annotations

from pathlib import Path

from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from app.inventory import catalog, service, sync
from app.inventory.ptm import PtmApiError, ReportsPtmAdapter
from app.inventory.schema import meta_get
from app.inventory.service import InventoryError

STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX_HTML = STATIC_DIR / "index.html"


def _json_ok(payload: dict, status: int = 200) -> JSONResponse:
    body = {"success": True}
    body.update(payload)
    return JSONResponse(body, status_code=status)


def _json_err(message: str, status: int) -> JSONResponse:
    body = {"success": False, "error": message}
    if status == 401:
        body["login"] = "/login"
    return JSONResponse(body, status_code=status)


async def _read_json(request: Request) -> dict:
    try:
        data = await request.json()
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _user(request: Request):
    getter = getattr(request.app.state, "inventory_user", None)
    if getter is None:
        return None
    return getter(request)


def _user_id(user) -> int:
    if user is None:
        raise InventoryError("Нужна авторизация", 401)
    if isinstance(user, dict):
        return int(user["id"])
    return int(user["id"])


def _ptm(request: Request, user):
    factory = getattr(request.app.state, "inventory_ptm", None)
    if factory is None:
        return None
    raw = factory(request, user)
    if raw is None:
        return None
    if all(hasattr(raw, name) for name in ("pull_barcodes", "create_inventory")):
        return raw
    return ReportsPtmAdapter(raw)


async def index(request: Request):
    if _user(request) is None:
        return RedirectResponse("/login", status_code=302)
    return HTMLResponse(INDEX_HTML.read_text(encoding="utf-8"))


async def status_get(request: Request) -> JSONResponse:
    try:
        user = _user(request)
        uid = _user_id(user)
        conn = request.app.state.conn
        client = _ptm(request, user)
        online = False
        if client is not None:
            try:
                online = await client.ping_health()
            except PtmApiError:
                online = False
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM inv_barcodes WHERE user_id = ?", (uid,)
        ).fetchone()["n"]
        return _json_ok(
            {
                "online": online,
                "ibConfigured": client is not None,
                "catalogPulledAt": meta_get(conn, uid, "catalog_pulled_at"),
                "lastPushAt": meta_get(conn, uid, "last_push_at"),
                "barcodeCount": count,
            }
        )
    except InventoryError as exc:
        return _json_err(str(exc), exc.status_code)


async def warehouses_get(request: Request) -> JSONResponse:
    try:
        uid = _user_id(_user(request))
        return _json_ok({"items": catalog.list_warehouses(request.app.state.conn, uid)})
    except InventoryError as exc:
        return _json_err(str(exc), exc.status_code)


async def docs_get(request: Request) -> JSONResponse:
    try:
        uid = _user_id(_user(request))
        warehouse = str(request.query_params.get("warehouse") or "").strip()
        if not warehouse:
            return _json_err("Не указан warehouse", 400)
        return _json_ok({"items": service.list_docs(request.app.state.conn, uid, warehouse)})
    except InventoryError as exc:
        return _json_err(str(exc), exc.status_code)


async def docs_post(request: Request) -> JSONResponse:
    try:
        uid = _user_id(_user(request))
        data = await _read_json(request)
        created = service.create_doc(
            request.app.state.conn,
            uid,
            str(data.get("warehouse") or ""),
            str(data.get("comment") or ""),
            str(data.get("author") or ""),
        )
        return _json_ok(created)
    except InventoryError as exc:
        return _json_err(str(exc), exc.status_code)


async def docs_delete(request: Request) -> JSONResponse:
    try:
        uid = _user_id(_user(request))
        doc_id = str(request.query_params.get("id") or "").strip()
        if not doc_id:
            return _json_err("Не указан id", 400)
        service.delete_doc(request.app.state.conn, uid, doc_id)
        return _json_ok({})
    except InventoryError as exc:
        return _json_err(str(exc), exc.status_code)


async def doc_get(request: Request) -> JSONResponse:
    try:
        uid = _user_id(_user(request))
        doc_id = str(request.query_params.get("id") or "").strip()
        if not doc_id:
            return _json_err("Не указан id", 400)
        return _json_ok(service.get_doc(request.app.state.conn, uid, doc_id))
    except InventoryError as exc:
        return _json_err(str(exc), exc.status_code)


async def scan_post(request: Request) -> JSONResponse:
    try:
        uid = _user_id(_user(request))
        data = await _read_json(request)
        result = service.scan(
            request.app.state.conn,
            uid,
            str(data.get("id") or ""),
            str(data.get("barcode") or ""),
        )
        return _json_ok(result)
    except InventoryError as exc:
        return _json_err(str(exc), exc.status_code)


async def qty_post(request: Request) -> JSONResponse:
    try:
        uid = _user_id(_user(request))
        data = await _read_json(request)
        try:
            line = int(data.get("line"))
            qty = float(data.get("qty"))
        except (TypeError, ValueError):
            return _json_err("Некорректные line или qty", 400)
        result = service.set_qty(request.app.state.conn, uid, str(data.get("id") or ""), line, qty)
        return _json_ok(result)
    except InventoryError as exc:
        return _json_err(str(exc), exc.status_code)


async def sync_post(request: Request) -> JSONResponse:
    try:
        user = _user(request)
        uid = _user_id(user)
        client = _ptm(request, user)
        if client is None:
            return _json_err("В настройках не задана ссылка на ИБ", 503)
        result = await sync.sync_now(request.app.state.conn, uid, client)
        status = 200 if result.get("online") else 503
        return JSONResponse({"success": bool(result.get("online")), **result}, status_code=status)
    except InventoryError as exc:
        return _json_err(str(exc), exc.status_code)


def inventory_routes() -> list:
    return [
        Route("/inv", index),
        Route("/inv/status", status_get),
        Route("/inv/warehouses", warehouses_get),
        Route("/inv/docs", docs_get, methods=["GET"]),
        Route("/inv/docs", docs_post, methods=["POST"]),
        Route("/inv/docs", docs_delete, methods=["DELETE"]),
        Route("/inv/doc", doc_get),
        Route("/inv/scan", scan_post, methods=["POST"]),
        Route("/inv/qty", qty_post, methods=["POST"]),
        Route("/inv/sync", sync_post, methods=["POST"]),
        Mount("/inv/static", StaticFiles(directory=str(STATIC_DIR)), name="inv-static"),
    ]
