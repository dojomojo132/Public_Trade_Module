# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from app import catalog, db, inventory, sync
from app.auth import (
    COOKIE_MAX_AGE,
    COOKIE_NAME,
    authenticate,
    create_user,
    get_user,
    make_session_value,
    read_session_value,
    user_count,
)
from app.config import Settings, load_settings
from app.inventory import InventoryError
from app.ptm_client import PtmApiError, PtmClient

STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX_HTML = STATIC_DIR / "index.html"


def _json_ok(payload: dict, status: int = 200) -> JSONResponse:
    body = {"success": True}
    body.update(payload)
    return JSONResponse(body, status_code=status)


def _json_err(message: str, status: int) -> JSONResponse:
    return JSONResponse({"success": False, "error": message}, status_code=status)


async def _read_json(request: Request) -> dict:
    try:
        data = await request.json()
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def current_user(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    uid = read_session_value(request.app.state.settings.secret, token)
    if uid is None:
        return None
    return get_user(request.app.state.conn, uid)


def require_user(request: Request):
    user = current_user(request)
    if user is None:
        raise InventoryError("Нужна авторизация", 401)
    return user


def _set_cookie(response: Response, request: Request, user_id: int) -> None:
    settings: Settings = request.app.state.settings
    response.set_cookie(
        COOKIE_NAME,
        make_session_value(settings.secret, user_id),
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        path="/",
    )


def _client(request: Request) -> PtmClient | None:
    factory = getattr(request.app.state, "client_factory", None)
    if factory is not None:
        return factory()
    settings: Settings = request.app.state.settings
    if not settings.ptm_base_url:
        return None
    return PtmClient(request.app.state.http, settings.ptm_base_url, settings.ptm_api_key)


async def index(request: Request) -> Response:
    return HTMLResponse(INDEX_HTML.read_text(encoding="utf-8"))


async def login_post(request: Request) -> Response:
    data = await _read_json(request)
    username = str(data.get("username") or "").strip()
    password = str(data.get("password") or "")
    if not username or not password:
        return _json_err("Укажите логин и пароль", 400)
    conn = request.app.state.conn
    if user_count(conn) == 0:
        create_user(conn, username, password, username)
    row = authenticate(conn, username, password)
    if row is None:
        return _json_err("Неверный логин или пароль", 401)
    response = _json_ok({"user": row["username"], "displayName": row["display_name"] or row["username"]})
    _set_cookie(response, request, int(row["id"]))
    return response


async def logout_post(request: Request) -> Response:
    response = _json_ok({})
    response.delete_cookie(COOKIE_NAME, path="/")
    return response


async def me_get(request: Request) -> Response:
    user = current_user(request)
    if user is None:
        return _json_err("Нужна авторизация", 401)
    return _json_ok({"user": user["username"], "displayName": user["display_name"] or user["username"]})


async def status_get(request: Request) -> Response:
    try:
        require_user(request)
    except InventoryError as exc:
        return _json_err(str(exc), exc.status_code)
    conn = request.app.state.conn
    client = _client(request)
    online = False
    if client is not None:
        try:
            online = await client.ping_health()
        except PtmApiError:
            online = False
    return _json_ok(
        {
            "online": online,
            "catalogPulledAt": db.meta_get(conn, "catalog_pulled_at"),
            "lastPushAt": db.meta_get(conn, "last_push_at"),
            "barcodeCount": conn.execute("SELECT COUNT(*) AS n FROM barcodes").fetchone()["n"],
        }
    )


async def warehouses_get(request: Request) -> Response:
    try:
        require_user(request)
        items = catalog.list_warehouses(request.app.state.conn)
        return _json_ok({"items": items})
    except InventoryError as exc:
        return _json_err(str(exc), exc.status_code)


async def docs_get(request: Request) -> Response:
    try:
        require_user(request)
        warehouse = str(request.query_params.get("warehouse") or "").strip()
        if not warehouse:
            return _json_err("Не указан warehouse", 400)
        return _json_ok({"items": inventory.list_docs(request.app.state.conn, warehouse)})
    except InventoryError as exc:
        return _json_err(str(exc), exc.status_code)


async def docs_post(request: Request) -> Response:
    try:
        require_user(request)
        data = await _read_json(request)
        created = inventory.create_doc(
            request.app.state.conn,
            str(data.get("warehouse") or ""),
            str(data.get("comment") or ""),
            str(data.get("author") or ""),
        )
        return _json_ok(created)
    except InventoryError as exc:
        return _json_err(str(exc), exc.status_code)


async def docs_delete(request: Request) -> Response:
    try:
        require_user(request)
        doc_id = str(request.query_params.get("id") or "").strip()
        if not doc_id:
            return _json_err("Не указан id", 400)
        inventory.delete_doc(request.app.state.conn, doc_id)
        return _json_ok({})
    except InventoryError as exc:
        return _json_err(str(exc), exc.status_code)


async def doc_get(request: Request) -> Response:
    try:
        require_user(request)
        doc_id = str(request.query_params.get("id") or "").strip()
        if not doc_id:
            return _json_err("Не указан id", 400)
        return _json_ok(inventory.get_doc(request.app.state.conn, doc_id))
    except InventoryError as exc:
        return _json_err(str(exc), exc.status_code)


async def scan_post(request: Request) -> Response:
    try:
        require_user(request)
        data = await _read_json(request)
        result = inventory.scan(
            request.app.state.conn,
            str(data.get("id") or ""),
            str(data.get("barcode") or ""),
        )
        return _json_ok(result)
    except InventoryError as exc:
        return _json_err(str(exc), exc.status_code)


async def qty_post(request: Request) -> Response:
    try:
        require_user(request)
        data = await _read_json(request)
        try:
            line = int(data.get("line"))
            qty = float(data.get("qty"))
        except (TypeError, ValueError):
            return _json_err("Некорректные line или qty", 400)
        result = inventory.set_qty(request.app.state.conn, str(data.get("id") or ""), line, qty)
        return _json_ok(result)
    except InventoryError as exc:
        return _json_err(str(exc), exc.status_code)


async def sync_post(request: Request) -> Response:
    try:
        require_user(request)
    except InventoryError as exc:
        return _json_err(str(exc), exc.status_code)
    client = _client(request)
    if client is None:
        return _json_err("PTM_BASE_URL не задан", 503)
    result = await sync.sync_now(request.app.state.conn, client)
    status = 200 if result.get("online") else 503
    return JSONResponse({"success": bool(result.get("online")), **result}, status_code=status)


def create_app(
    settings: Settings | None = None,
    conn=None,
    client_factory=None,
    enable_background: bool = True,
) -> Starlette:
    settings = settings or load_settings()
    if conn is None:
        conn = db.connect(settings.db_path)
        db.init_schema(conn)

    @asynccontextmanager
    async def lifespan(app: Starlette):
        app.state.http = httpx.AsyncClient(timeout=60.0)
        stop = asyncio.Event()
        tasks: list[asyncio.Task] = []
        if enable_background and settings.ptm_base_url:

            async def loop_pull() -> None:
                while not stop.is_set():
                    try:
                        client = PtmClient(app.state.http, settings.ptm_base_url, settings.ptm_api_key)
                        await sync.pull_catalog(conn, client)
                    except Exception:
                        pass
                    try:
                        await asyncio.wait_for(stop.wait(), timeout=settings.pull_sec)
                    except asyncio.TimeoutError:
                        continue

            async def loop_push() -> None:
                while not stop.is_set():
                    try:
                        await asyncio.wait_for(stop.wait(), timeout=settings.push_sec)
                    except asyncio.TimeoutError:
                        pass
                    if stop.is_set():
                        break
                    try:
                        client = PtmClient(app.state.http, settings.ptm_base_url, settings.ptm_api_key)
                        await sync.push_dirty(conn, client)
                    except Exception:
                        pass

            tasks = [asyncio.create_task(loop_pull()), asyncio.create_task(loop_push())]
        yield
        stop.set()
        for task in tasks:
            task.cancel()
        await app.state.http.aclose()

    app = Starlette(
        lifespan=lifespan,
        routes=[
            Route("/", index),
            Route("/login", login_post, methods=["POST"]),
            Route("/logout", logout_post, methods=["POST"]),
            Route("/me", me_get),
            Route("/inv/status", status_get),
            Route("/inv/warehouses", warehouses_get),
            Route("/inv/docs", docs_get, methods=["GET"]),
            Route("/inv/docs", docs_post, methods=["POST"]),
            Route("/inv/docs", docs_delete, methods=["DELETE"]),
            Route("/inv/doc", doc_get),
            Route("/inv/scan", scan_post, methods=["POST"]),
            Route("/inv/qty", qty_post, methods=["POST"]),
            Route("/inv/sync", sync_post, methods=["POST"]),
            Mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static"),
        ],
    )
    app.state.settings = settings
    app.state.conn = conn
    app.state.client_factory = client_factory
    return app


app = create_app()
