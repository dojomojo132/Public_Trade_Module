# -*- coding: utf-8 -*-
from __future__ import annotations

import html
from pathlib import Path

from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))


def e(value) -> str:
    return html.escape(str(value or ""), quote=True)


def render(request: Request, title: str, body: str, *, auth: bool = False, nav: str = "home") -> HTMLResponse:
    user = getattr(request.state, "user", None)
    ib_state = getattr(request.state, "ib_state", "offline")
    ib_label = getattr(request.state, "ib_label", "Нет 1С")
    return TEMPLATES.TemplateResponse(
        request,
        "shell.html",
        {
            "title": title,
            "body": body,
            "auth": auth,
            "nav": nav,
            "username": user["username"] if user is not None else "",
            "ib_state": ib_state,
            "ib_label": ib_label,
        },
    )


def flash_err(message: str) -> str:
    if not message:
        return ""
    return f'<p class="flash-err">{e(message)}</p>'


def flash_ok(message: str) -> str:
    if not message:
        return ""
    return f'<p class="flash-ok">{e(message)}</p>'
