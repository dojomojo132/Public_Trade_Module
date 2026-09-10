# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3

from itsdangerous import BadSignature, URLSafeTimedSerializer
from starlette.requests import Request
from starlette.responses import Response

COOKIE = "ptm_session"
COOKIE_MAX_AGE = 60 * 60 * 12
_SALT = "ptm-reports"


def _ser(secret: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(secret, salt=_SALT)


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("ascii"), 120_000)
    return f"pbkdf2${salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    stored = stored or ""
    if stored.startswith("pbkdf2$"):
        try:
            _, salt, hexdigest = stored.split("$", 2)
        except ValueError:
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("ascii"), 120_000)
        return hmac.compare_digest(digest.hex(), hexdigest)
    return hmac.compare_digest(stored, password)


def user_count(conn: sqlite3.Connection) -> int:
    return int(conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"])


def create_user(conn: sqlite3.Connection, username: str, password: str) -> int:
    cur = conn.execute(
        "INSERT INTO users(username, password_hash) VALUES (?, ?)",
        (username, hash_password(password)),
    )
    conn.commit()
    return int(cur.lastrowid)


def authenticate(conn: sqlite3.Connection, username: str, password: str) -> sqlite3.Row | None:
    row = conn.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    if row is None or not verify_password(password, row["password_hash"]):
        return None
    return row


def current_user(request: Request):
    token = request.cookies.get(COOKIE)
    if not token:
        return None
    try:
        data = _ser(request.app.state.secret).loads(token, max_age=COOKIE_MAX_AGE)
        uid = int(data["uid"])
    except (BadSignature, KeyError, TypeError, ValueError):
        return None
    return request.app.state.conn.execute(
        "SELECT id, username FROM users WHERE id = ?", (uid,)
    ).fetchone()


def set_session(response: Response, secret: str, user_id: int, secure: bool) -> None:
    response.set_cookie(
        COOKIE,
        _ser(secret).dumps({"uid": int(user_id)}),
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=secure,
        path="/",
    )


def clear_session(response: Response) -> None:
    response.delete_cookie(COOKIE, path="/")
