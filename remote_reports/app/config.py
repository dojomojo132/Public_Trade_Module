# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    secret: str
    db_path: Path
    cookie_secure: bool
    port: int


def load_settings() -> Settings:
    return Settings(
        secret=os.environ.get("REPORTS_SECRET") or os.environ.get("INV_SECRET") or "change-me",
        db_path=Path(os.environ.get("REPORTS_DB") or os.environ.get("INV_DB") or "data/app.db"),
        cookie_secure=os.environ.get("REPORTS_COOKIE_SECURE", "0") in {"1", "true", "yes"},
        port=int(os.environ.get("PORT") or os.environ.get("INV_PORT") or "8000"),
    )
