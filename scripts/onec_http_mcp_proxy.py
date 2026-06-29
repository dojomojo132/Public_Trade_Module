# -*- coding: utf-8 -*-
"""
onec-mcp — stdio MCP-прокси к HTTP MCP 1С.

Cursor/Grok CallMcpTool не поднимает url/sse-серверы из .cursor/mcp.json.
Этот скрипт проксирует tools/list и tools/call на HTTP endpoint ИБ.

Env (опционально):
  ONEC_MCP_URL  — default из project-config.yml mcp.onec.url
"""
from __future__ import annotations

import base64
import io
import json
import logging
import pathlib
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stdin, "buffer"):
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _mcp_protocol import negotiate_protocol_version

LOG = pathlib.Path(__file__).resolve().parent.parent / "logs" / "onec_http_mcp_proxy.log"
LOG.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(LOG),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("onec-mcp-proxy")

SERVER_INFO = {"name": "onec-mcp-proxy", "version": "0.1.0"}
CAPABILITIES = {"tools": {}}
_TOOLS_CACHE: list[dict] | None = None


def _load_http_config() -> tuple[str, str]:
    import os
    from _project_config import get

    url = (os.environ.get("ONEC_MCP_URL") or get("mcp.onec.url") or "").rstrip("/")
    if not url:
        raise RuntimeError("ONEC_MCP_URL / mcp.onec.url не задан")

    auth_user = get("mcp.onec.auth_user") or "Admin"
    auth_password = get("mcp.onec.auth_password") or ""
    token = base64.b64encode(f"{auth_user}:{auth_password}".encode("utf-8")).decode("ascii")
    return url, f"Basic {token}"


def _http_call(method: str, params: dict | None = None, req_id: int = 1) -> dict:
    url, auth = _load_http_config()
    body = json.dumps(
        {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params or {}},
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": auth,
            "Accept": "application/json, text/event-stream",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8", errors="replace").strip()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"HTTP {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"URL error: {e}") from e

    # Ответ может быть JSON или SSE (data: {...})
    if raw.startswith("data:"):
        for line in raw.splitlines():
            if line.startswith("data:"):
                raw = line[5:].strip()
                break
    payload = json.loads(raw)
    if "error" in payload:
        err = payload["error"]
        raise RuntimeError(err.get("message", str(err)))
    return payload.get("result", payload)


def _tools() -> list[dict]:
    global _TOOLS_CACHE
    if _TOOLS_CACHE is None:
        result = _http_call("tools/list")
        _TOOLS_CACHE = result.get("tools", [])
        logger.info("tools/list cached: %s tools", len(_TOOLS_CACHE))
    return _TOOLS_CACHE


def make_response(req_id: Any, result: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def make_error(req_id: Any, code: int, message: str) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def handle_request(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    method = request.get("method", "")
    params = request.get("params", {}) or {}
    req_id = request.get("id")
    logger.info("Request: %s (id=%s)", method, req_id)

    if method == "initialize":
        return make_response(
            req_id,
            {
                "protocolVersion": negotiate_protocol_version(params),
                "capabilities": CAPABILITIES,
                "serverInfo": SERVER_INFO,
            },
        )

    if method == "notifications/initialized":
        return None

    if method == "ping":
        return make_response(req_id, {})

    if method == "tools/list":
        try:
            return make_response(req_id, {"tools": _tools()})
        except Exception as e:  # noqa: BLE001
            return make_error(req_id, -32000, str(e))

    if method == "tools/call":
        name = params.get("name", "")
        arguments = params.get("arguments", {}) or {}
        try:
            result = _http_call(
                "tools/call",
                {"name": name, "arguments": arguments},
                req_id if isinstance(req_id, int) else 99,
            )
            return make_response(req_id, result)
        except Exception as e:  # noqa: BLE001
            return make_response(
                req_id,
                {
                    "content": [{"type": "text", "text": json.dumps({"error": str(e)}, ensure_ascii=False)}],
                    "isError": True,
                },
            )

    if req_id is not None:
        return make_error(req_id, -32601, f"Method not found: {method}")
    return None


def run_stdio() -> None:
    logger.info("onec-mcp proxy starting")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as e:
            resp = make_error(None, -32700, f"Parse error: {e}")
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
            continue
        response = handle_request(request)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_stdio()