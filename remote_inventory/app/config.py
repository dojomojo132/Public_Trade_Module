# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = val.strip()


_load_dotenv()


@dataclass(frozen=True)
class Settings:
    secret: str
    db_path: Path
    port: int
    cookie_secure: bool
    ptm_base_url: str
    ptm_api_key: str
    pull_sec: int
    push_sec: int


def load_settings() -> Settings:
    db_raw = os.environ.get("INV_DB", str(ROOT / "data" / "app.db"))
    secure_raw = os.environ.get("INV_COOKIE_SECURE", "").strip().lower()
    return Settings(
        secret=os.environ.get("INV_SECRET", "dev-change-me"),
        db_path=Path(db_raw),
        port=int(os.environ.get("INV_PORT", "8091")),
        cookie_secure=secure_raw in {"1", "true", "yes"},
        ptm_base_url=os.environ.get("PTM_BASE_URL", "").rstrip("/"),
        ptm_api_key=os.environ.get("PTM_API_KEY", ""),
        pull_sec=int(os.environ.get("INV_PULL_SEC", "900")),
        push_sec=int(os.environ.get("INV_PUSH_SEC", "180")),
    )
