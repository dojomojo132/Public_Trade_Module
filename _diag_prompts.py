# -*- coding: utf-8 -*-
"""Диагностика ошибки prompts/list"""
import json, urllib.request, base64

URL = "http://localhost/PTM_Clean/hs/mcp/mcp"
AUTH = base64.b64encode(b"Admin:").decode()

body = {"jsonrpc": "2.0", "id": 1, "method": "prompts/list"}
data = json.dumps(body, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request(URL, data=data,
    headers={"Content-Type": "application/json; charset=utf-8",
             "Authorization": f"Basic {AUTH}"})
try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        print("OK:", json.dumps(result, ensure_ascii=False, indent=2)[:2000])
except urllib.error.HTTPError as e:
    body_err = e.read().decode("utf-8", errors="replace")
    print(f"HTTP {e.code}: {body_err[:3000]}")
