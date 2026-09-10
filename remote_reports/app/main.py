# -*- coding: utf-8 -*-
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from app import db, pages
from app.auth import current_user
from app.config import Settings, load_settings
from app.inventory.ptm import ReportsPtmAdapter
from app.inventory.routes import inventory_routes
from app.ptm_client import PtmClient

STATIC_DIR = Path(__file__).resolve().parent / "static"


def _inventory_ptm_factory(client_factory):
    def inventory_ptm(request, user):
        if client_factory is not None:
            return client_factory()
        row = db.get_connection(request.app.state.conn, int(user["id"]))
        if not row or not str(row["ib_location"] or "").strip():
            return None
        http = getattr(request.app.state, "http", None)
        if http is None:
            return None
        return ReportsPtmAdapter(PtmClient(http, row["ib_location"], row["api_key"]))

    return inventory_ptm


def create_app(
    settings: Settings | None = None,
    conn=None,
    client_factory=None,
) -> Starlette:
    settings = settings or load_settings()
    if conn is None:
        conn = db.connect(settings.db_path)
        db.init_schema(conn)
    else:
        db.init_schema(conn)

    @asynccontextmanager
    async def lifespan(app: Starlette):
        app.state.http = httpx.AsyncClient(timeout=60.0)
        yield
        await app.state.http.aclose()

    routes = [
        Route("/", pages.home),
        Route("/health", pages.health),
        Route("/login", pages.login_get, methods=["GET"]),
        Route("/login", pages.login_post, methods=["POST"]),
        Route("/register", pages.register_get, methods=["GET"]),
        Route("/register", pages.register_post, methods=["POST"]),
        Route("/logout", pages.logout_post, methods=["GET", "POST"]),
        Route("/settings", pages.settings_get, methods=["GET"]),
        Route("/settings", pages.settings_post, methods=["POST"]),
        Route("/ib-status", pages.ib_status),
        Route("/reports/sales", pages.sales_report),
        Route("/reports/stocks", pages.stocks_report),
        Route("/reports/cash", pages.cash_report),
        Route("/reports/prices", pages.prices_report),
        Mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static"),
        *inventory_routes(),
    ]
    app = Starlette(lifespan=lifespan, routes=routes)
    app.state.settings = settings
    app.state.conn = conn
    app.state.secret = settings.secret
    app.state.cookie_secure = settings.cookie_secure
    app.state.inventory_user = current_user
    app.state.inventory_ptm = _inventory_ptm_factory(client_factory)
    return app
