# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3

from itsdangerous import BadSignature, URLSafeTimedSerializer

COOKIE_NAME = "ptm_inv_session"
COOKIE_MAX_AGE = 60 * 60 * 12


def _serializer(secret: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(secret, salt="ptm-remote-inventory")


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
    return salt.hex() + ":" + digest.hex()


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split(":", 1)
    except ValueError:
        return False
    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(digest_hex)
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
    return hmac.compare_digest(actual, expected)


def create_user(conn: sqlite3.Connection, username: str, password: str, display_name: str = "") -> int:
    cur = conn.execute(
        "INSERT INTO users (username, password_hash, display_name) VALUES (?, ?, ?)",
        (username.strip(), hash_password(password), display_name.strip()),
    )
    conn.commit()
    return int(cur.lastrowid)


def user_count(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()
    return int(row["n"])


def authenticate(conn: sqlite3.Connection, username: str, password: str) -> sqlite3.Row | None:
    row = conn.execute(
        "SELECT id, username, password_hash, display_name FROM users WHERE username = ?",
        (username.strip(),),
    ).fetchone()
    if row is None or not verify_password(password, row["password_hash"]):
        return None
    return row


def get_user(conn: sqlite3.Connection, user_id: int) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT id, username, display_name FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()


def make_session_value(secret: str, user_id: int) -> str:
    return _serializer(secret).dumps({"uid": int(user_id)})


def read_session_value(secret: str, token: str) -> int | None:
    try:
        data = _serializer(secret).loads(token, max_age=COOKIE_MAX_AGE)
    except (BadSignature, TypeError, ValueError):
        return None
    try:
        return int(data["uid"])
    except (KeyError, TypeError, ValueError):
        return None
