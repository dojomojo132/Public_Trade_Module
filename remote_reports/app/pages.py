# -*- coding: utf-8 -*-
"""HTML pages for the reports host (login, home, settings, PTM tables)."""
from __future__ import annotations

from datetime import date

from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response

from app import db, htmlkit
from app.auth import (
    authenticate,
    clear_session,
    create_user,
    current_user,
    set_session,
    user_count,
)
from app.htmlkit import e
from app.inventory.ptm import ReportsPtmAdapter
from app.ptm_client import PtmApiError

REPORT_CATALOG = [
    {
        "id": "inventory",
        "title": "Переучёт",
        "blurb": "Скан в кеш этого сервера. В 1С черновик уходит по кнопке «Синхронизировать».",
        "href": "/inv",
        "go": "Открыть →",
    },
    {
        "id": "sales",
        "title": "Продажи",
        "blurb": "Обороты продаж за период через тот же туннель PTM_API.",
        "href": "/reports/sales",
        "go": "Открыть →",
    },
    {
        "id": "stocks",
        "title": "Остатки",
        "blurb": "Срез остатков на дату.",
        "href": "/reports/stocks",
        "go": "Открыть →",
    },
    {
        "id": "cash",
        "title": "Касса",
        "blurb": "Остатки по кассам.",
        "href": "/reports/cash",
        "go": "Открыть →",
    },
    {
        "id": "prices",
        "title": "Цены",
        "blurb": "Актуальный срез цен.",
        "href": "/reports/prices",
        "go": "Открыть →",
    },
]


def _ptm_for(request: Request, user):
    factory = getattr(request.app.state, "inventory_ptm", None)
    if factory is None:
        return None
    return factory(request, user)


async def _ib_view(request: Request, user) -> tuple[str, str]:
    client = _ptm_for(request, user)
    if client is None:
        return "unset", "Нет 1С"
    try:
        online = await client.ping_health()
    except Exception:
        online = False
    if online:
        return "online", "1С"
    return "offline", "Офлайн"


def require_user(request: Request):
    user = current_user(request)
    if user is None:
        return None
    request.state.user = user
    return user


async def login_get(request: Request) -> HTMLResponse:
    body = """
<div class="auth-card">
  <a class="brand" href="/login"><span class="mark">P</span> Отчёты PTM</a>
  <h1>Вход</h1>
  <p class="lede">Учётка сервиса, не пользователь 1С.</p>
  <form method="post" action="/login" class="stack">
    <label>Логин <input name="username" autocomplete="username" required></label>
    <label>Пароль <input name="password" type="password" autocomplete="current-password" required></label>
    <button class="btn" type="submit">Войти</button>
  </form>
  <p class="auth-foot">Нет аккаунта? <a href="/register">Регистрация</a></p>
</div>
"""
    return htmlkit.render(request, "Вход", body, auth=True)


async def register_get(request: Request) -> HTMLResponse:
    body = """
<div class="auth-card">
  <a class="brand" href="/login"><span class="mark">P</span> Отчёты PTM</a>
  <h1>Регистрация</h1>
  <p class="lede">Учётка сервиса, не пользователь 1С.</p>
  <form method="post" action="/register" class="stack">
    <label>Логин <input name="username" autocomplete="username" required></label>
    <label>Пароль <input name="password" type="password" autocomplete="new-password" required minlength="6"></label>
    <button class="btn" type="submit">Создать</button>
  </form>
  <p class="auth-foot">Уже есть аккаунт? <a href="/login">Вход</a></p>
</div>
"""
    return htmlkit.render(request, "Регистрация", body, auth=True)


async def _login_user(request: Request, username: str, password: str) -> Response:
    username = str(username or "").strip()
    password = str(password or "")
    conn = request.app.state.conn
    if not username or not password:
        return JSONResponse({"success": False, "error": "Укажите логин и пароль"}, 400)
    row = authenticate(conn, username, password)
    if row is None:
        if user_count(conn) == 0:
            uid = create_user(conn, username, password)
        else:
            return JSONResponse({"success": False, "error": "Неверный логин или пароль"}, 401)
    else:
        uid = int(row["id"])
    resp = JSONResponse({"success": True, "user": username})
    set_session(resp, request.app.state.secret, uid, request.app.state.cookie_secure)
    return resp


async def login_post(request: Request) -> Response:
    ctype = (request.headers.get("content-type") or "").lower()
    if "application/json" in ctype:
        data = await request.json()
        return await _login_user(request, data.get("username"), data.get("password"))
    form = await request.form()
    username = str(form.get("username") or "").strip()
    password = str(form.get("password") or "")
    conn = request.app.state.conn
    if not username or not password:
        request.state.user = None
        body = f"""
<div class="auth-card">
  <a class="brand" href="/login"><span class="mark">P</span> Отчёты PTM</a>
  <h1>Вход</h1>
  {htmlkit.flash_err("Укажите логин и пароль")}
  <form method="post" action="/login" class="stack">
    <label>Логин <input name="username" autocomplete="username" required></label>
    <label>Пароль <input name="password" type="password" required></label>
    <button class="btn" type="submit">Войти</button>
  </form>
</div>
"""
        return htmlkit.render(request, "Вход", body, auth=True)
    row = authenticate(conn, username, password)
    if row is None:
        if user_count(conn) == 0:
            uid = create_user(conn, username, password)
        else:
            body = f"""
<div class="auth-card">
  <a class="brand" href="/login"><span class="mark">P</span> Отчёты PTM</a>
  <h1>Вход</h1>
  {htmlkit.flash_err("Неверный логин или пароль")}
  <form method="post" action="/login" class="stack">
    <label>Логин <input name="username" value="{e(username)}" required></label>
    <label>Пароль <input name="password" type="password" required></label>
    <button class="btn" type="submit">Войти</button>
  </form>
</div>
"""
            return htmlkit.render(request, "Вход", body, auth=True)
    else:
        uid = int(row["id"])
    resp = RedirectResponse("/", status_code=303)
    set_session(resp, request.app.state.secret, uid, request.app.state.cookie_secure)
    return resp


async def register_post(request: Request) -> Response:
    form = await request.form()
    username = str(form.get("username") or "").strip()
    password = str(form.get("password") or "")
    err = ""
    if not username or len(password) < 6:
        err = "Логин и пароль от 6 символов"
    else:
        existing = request.app.state.conn.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        if existing is not None:
            err = "Такой логин уже есть"
    if err:
        body = f"""
<div class="auth-card">
  <a class="brand" href="/login"><span class="mark">P</span> Отчёты PTM</a>
  <h1>Регистрация</h1>
  {htmlkit.flash_err(err)}
  <form method="post" action="/register" class="stack">
    <label>Логин <input name="username" value="{e(username)}" required></label>
    <label>Пароль <input name="password" type="password" required minlength="6"></label>
    <button class="btn" type="submit">Создать</button>
  </form>
</div>
"""
        return htmlkit.render(request, "Регистрация", body, auth=True)
    uid = create_user(request.app.state.conn, username, password)
    resp = RedirectResponse("/", status_code=303)
    set_session(resp, request.app.state.secret, uid, request.app.state.cookie_secure)
    return resp


async def logout_post(request: Request) -> Response:
    resp = RedirectResponse("/login", status_code=302)
    clear_session(resp)
    return resp


async def home(request: Request) -> Response:
    user = require_user(request)
    if user is None:
        return RedirectResponse("/login", 302)
    request.state.ib_state, request.state.ib_label = await _ib_view(request, user)
    cards = "".join(
        f'<a class="panel report-card" href="{e(item["href"])}">'
        f'<h2>{e(item["title"])}</h2><p>{e(item["blurb"])}</p>'
        f'<span class="go">{e(item["go"])}</span></a>'
        for item in REPORT_CATALOG
    )
    body = f"""
<div class="page-head">
  <h1>Отчёты</h1>
  <p class="lede">Туннель до 1С задаётся в Настройках. Переучёт пишет в кеш и не ходит в ИБ на каждый скан.</p>
</div>
<div class="report-grid">{cards}</div>
"""
    return htmlkit.render(request, "Отчёты PTM", body, nav="home")


async def settings_get(request: Request) -> Response:
    user = require_user(request)
    if user is None:
        return RedirectResponse("/login", 302)
    request.state.ib_state, request.state.ib_label = await _ib_view(request, user)
    row = db.get_connection(request.app.state.conn, user["id"])
    location = row["ib_location"] if row else ""
    api_key = row["api_key"] if row else ""
    saved = request.query_params.get("saved") == "1"
    body = f"""
<div class="page-head">
  <p class="crumb"><a href="/">Отчёты</a> / Настройки</p>
  <h1>Настройки</h1>
  <p class="lede">Ссылка на публикацию PTM_API через SSH-туннель. Телефон 1С не видит — только этот сервер.</p>
</div>
{htmlkit.flash_ok("Сохранено") if saved else ""}
<div class="settings">
  <form method="post" action="/settings" class="panel form-card stack">
    <h2>Информационная база</h2>
    <label>Адрес PTM_API
      <input name="ib_location" value="{e(location)}" placeholder="http://127.0.0.1:18091/DB/hs/ptm/v1">
    </label>
    <p class="hint">Только localhost/туннель, не публичный URL файловой ИБ.</p>
    <label>Ключ API
      <input name="api_key" value="{e(api_key)}" autocomplete="off">
    </label>
    <p class="hint">Константа Апи_Ключ. Заголовок X-Api-Key.</p>
    <button class="btn" type="submit">Сохранить</button>
  </form>
</div>
"""
    return htmlkit.render(request, "Настройки", body, nav="settings")


async def settings_post(request: Request) -> Response:
    user = require_user(request)
    if user is None:
        return RedirectResponse("/login", 302)
    form = await request.form()
    db.save_connection(
        request.app.state.conn,
        int(user["id"]),
        str(form.get("ib_location") or ""),
        str(form.get("api_key") or ""),
    )
    return RedirectResponse("/settings?saved=1", status_code=303)


async def ib_status(request: Request) -> JSONResponse:
    user = current_user(request)
    if user is None:
        return JSONResponse({"status": "unset", "label": "Нет 1С"}, status_code=401)
    status, label = await _ib_view(request, user)
    mapped = "ok" if status == "online" else status
    return JSONResponse({"status": mapped, "label": label})


async def health(_: Request) -> JSONResponse:
    return JSONResponse({"ok": True})


def _today_range() -> tuple[str, str]:
    today = date.today().isoformat()
    return today, today


async def _report_table(
    request: Request,
    *,
    title: str,
    path: str,
    columns: list[tuple[str, str]],
    params: dict,
    period: bool,
) -> Response:
    user = require_user(request)
    if user is None:
        return RedirectResponse("/login", 302)
    request.state.ib_state, request.state.ib_label = await _ib_view(request, user)
    client = _ptm_for(request, user)
    err = ""
    rows: list[dict] = []
    if client is None:
        err = "В Настройках не задана ссылка на ИБ"
    else:
        raw = client._c if isinstance(client, ReportsPtmAdapter) else client
        try:
            if hasattr(raw, "fetch_all_pages"):
                rows = await raw.fetch_all_pages(path, params)
            else:
                err = "Клиент PTM не умеет читать отчёты"
        except PtmApiError as exc:
            err = str(exc)
        except Exception as exc:
            err = str(exc)

    date_from = params.get("dateFrom") or ""
    date_to = params.get("dateTo") or ""
    toolbar = ""
    if period:
        toolbar = f"""
<form class="toolbar panel" method="get">
  <label class="field">С
    <input type="date" name="dateFrom" value="{e(date_from)}">
  </label>
  <label class="field">По
    <input type="date" name="dateTo" value="{e(date_to)}">
  </label>
  <button class="btn" type="submit">Показать</button>
</form>
"""
    head = "".join(f"<th>{e(label)}</th>" for _, label in columns)
    body_rows = []
    for item in rows[:500]:
        tds = "".join(f'<td data-label="{e(label)}">{e(item.get(key, ""))}</td>' for key, label in columns)
        body_rows.append(f"<tr>{tds}</tr>")
    table = (
        f'<div class="panel table-wrap"><table><thead><tr>{head}</tr></thead>'
        f'<tbody>{"".join(body_rows) or "<tr><td colspan=\'%d\'>Нет данных</td></tr>" % len(columns)}</tbody></table></div>'
    )
    body = f"""
<div class="page-head">
  <p class="crumb"><a href="/">Отчёты</a> / {e(title)}</p>
  <h1>{e(title)}</h1>
</div>
{toolbar}
{htmlkit.flash_err(err)}
{table}
"""
    return htmlkit.render(request, title, body, nav="home")


async def sales_report(request: Request) -> Response:
    date_from = str(request.query_params.get("dateFrom") or _today_range()[0])
    date_to = str(request.query_params.get("dateTo") or _today_range()[1])
    return await _report_table(
        request,
        title="Продажи",
        path="/sales",
        columns=[
            ("date", "Дата"),
            ("productName", "Товар"),
            ("qty", "Кол-во"),
            ("amount", "Сумма"),
        ],
        params={"dateFrom": date_from, "dateTo": date_to},
        period=True,
    )


async def stocks_report(request: Request) -> Response:
    return await _report_table(
        request,
        title="Остатки",
        path="/stocks",
        columns=[
            ("productName", "Товар"),
            ("warehouseName", "Склад"),
            ("qty", "Остаток"),
        ],
        params={"onlyNonZero": "true"},
        period=False,
    )


async def cash_report(request: Request) -> Response:
    return await _report_table(
        request,
        title="Касса",
        path="/cash-balances",
        columns=[
            ("cashRegisterName", "Касса"),
            ("amount", "Остаток"),
        ],
        params={"onlyNonZero": "true"},
        period=False,
    )


async def prices_report(request: Request) -> Response:
    return await _report_table(
        request,
        title="Цены",
        path="/prices",
        columns=[
            ("productName", "Товар"),
            ("priceTypeName", "Тип цен"),
            ("price", "Цена"),
        ],
        params={},
        period=False,
    )
