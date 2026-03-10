# -*- coding: utf-8 -*-
"""Проверка доступности PTM MCP HTTP-сервиса."""
import urllib.request
import json
import sys

BASE_URL = "http://localhost/PTM_Clean/hs/mcp/mcp"

def call_mcp(method, params=None):
    """Вызов MCP-метода через JSON-RPC."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            if body:
                return json.loads(body)
            return {"status": resp.status, "body": "(empty)"}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"error": f"HTTP {e.code}", "body": body[:500]}
    except Exception as e:
        return {"error": str(e)}


print("=== PTM MCP Server Check ===\n")

# 1. tools/list
print("1. tools/list:")
result = call_mcp("tools/list")
print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])
print()

# 2. Прямой вызов get_configuration_overview
print("2. tools/call - get_configuration_overview:")
result = call_mcp("tools/call", {
    "name": "get_configuration_overview",
    "arguments": {}
})
print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])
print()

# 3. resources/list
print("3. resources/list:")
result = call_mcp("resources/list")
print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])
print()

# 4. prompts/list
print("4. prompts/list:")
result = call_mcp("prompts/list")
print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])
