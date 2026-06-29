# -*- coding: utf-8 -*-
"""Общая логика MCP handshake для stdio-серверов проекта."""

from __future__ import annotations

from typing import Any

SUPPORTED_PROTOCOLS = ("2024-11-05", "2025-03-26", "2025-06-18")


def negotiate_protocol_version(params: dict[str, Any] | None) -> str:
    """Вернуть версию протокола, согласованную с клиентом (Grok/Cursor/VS Code)."""
    requested = (params or {}).get("protocolVersion", "")
    if requested in SUPPORTED_PROTOCOLS:
        return requested
    return SUPPORTED_PROTOCOLS[-1]