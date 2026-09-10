# -*- coding: utf-8 -*-
"""Minimal host that mimics reports.dojomyassiste.uno auth + IB connection hooks."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from itsdangerous import BadSignature, URLSafeTimedSerializer
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from app.inventory.routes import inventory_routes
from app.inventory.schema import init_inventory_schema

COOKIE = "ptm_session"
DEMO_CSS_DIR = Path(__file__).resolve().parent / "_demo_static"


def _ser(secret: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(secret, salt="ptm-reports")


def current_user(request: Request):
    token = request.cookies.get(COOKIE)
    if not token:
        return None
    try:
        data = _ser(request.app.state.secret).loads(token, max_age=60 * 60 * 12)
        uid = int(data["uid"])
    except (BadSignature, KeyError, TypeError, ValueError):
        return None
    return request.app.state.conn.execute(
        "SELECT id, username FROM users WHERE id = ?", (uid,)
    ).fetchone()


async def login_get(request: Request):
    return HTMLResponse(
        "<form method='post' action='/login'>"
        "<input name='username'><input name='password' type='password'>"
        "<button type='submit'>Войти</button></form>"
    )


async def _do_login(request: Request, username: str, password: str, html: bool):
    username = str(username or "").strip()
    password = str(password or "")
    if not username or not password:
        if html:
            return HTMLResponse("empty", status_code=400)
        return JSONResponse({"success": False, "error": "empty"}, status_code=400)
    conn = request.app.state.conn
    row = conn.execute(
        "SELECT id FROM users WHERE username = ? AND password = ?",
        (username, password),
    ).fetchone()
    if row is None:
        count = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]
        if count == 0:
            cur = conn.execute(
                "INSERT INTO users(username, password) VALUES (?, ?)",
                (username, password),
            )
            conn.commit()
            uid = int(cur.lastrowid)
        else:
            if html:
                return HTMLResponse("bad login", status_code=401)
            return JSONResponse({"success": False, "error": "Неверный логин"}, status_code=401)
    else:
        uid = int(row["id"])
    if html:
        resp = RedirectResponse("/", status_code=303)
    else:
        resp = JSONResponse({"success": True, "user": username})
    resp.set_cookie(COOKIE, _ser(request.app.state.secret).dumps({"uid": uid}), httponly=True, path="/")
    return resp


async def login_post(request: Request):
    ctype = (request.headers.get("content-type") or "").lower()
    if "application/json" in ctype:
        data = await request.json()
        return await _do_login(request, data.get("username"), data.get("password"), False)
    form = await request.form()
    return await _do_login(request, form.get("username"), form.get("password"), True)


async def home(request: Request):
    if current_user(request) is None:
        return RedirectResponse("/login", 302)
    return HTMLResponse("<a href='/inv'>Переучёт</a>")


def create_demo_app(conn: sqlite3.Connection, secret: str, ptm_factory) -> Starlette:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users "
        "(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)"
    )
    conn.commit()
    init_inventory_schema(conn)
    css_dir = DEMO_CSS_DIR
    css_dir.mkdir(exist_ok=True)
    if not (css_dir / "app.css").exists():
        (css_dir / "app.css").write_text(
            ":root { --line:#e4e3de; --accent:#0f6b5c; --accent-soft:#e8f3ef; }\n",
            encoding="utf-8",
        )
    routes = [
        Route("/", home),
        Route("/login", login_get, methods=["GET"]),
        Route("/login", login_post, methods=["POST"]),
        Mount("/static", StaticFiles(directory=str(css_dir)), name="static"),
        *inventory_routes(),
    ]
    app = Starlette(routes=routes)
    app.state.conn = conn
    app.state.secret = secret
    app.state.inventory_user = current_user
    app.state.inventory_ptm = lambda request, user: ptm_factory()
    return app
