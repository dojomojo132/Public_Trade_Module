# -*- coding: utf-8 -*-
"""Тест Cat C: import_data, clear_deleted, get_data_history"""
import json, urllib.request, base64

URL = "http://localhost/PTM_Clean/hs/mcp/mcp"
AUTH = base64.b64encode(b"Admin:").decode()

def call(method, params=None):
    body = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params:
        body["params"] = params
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(URL, data=data,
        headers={"Content-Type": "application/json; charset=utf-8",
                 "Authorization": f"Basic {AUTH}"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))

def tool(name, args):
    r = call("tools/call", {"name": name, "arguments": args})
    if "error" in r:
        return f"ERROR: {r['error']}"
    return r["result"]["content"][0]["text"]

# Сначала удалим тестовые данные
print("=== Удаление предыдущих тестовых Склады (ТестИмп) ===")
print(tool("delete_object", {"metaType": "Catalogs", "name": "Склады", "searchValue": "Тестмп_1", "force": True}))
print(tool("delete_object", {"metaType": "Catalogs", "name": "Склады", "searchValue": "Тестмп_2", "force": True}))

print("\n=== ТЕСТ 1: import_data (2 склада) ===")
data = json.dumps([
    {"description": "ТестИмп_Первый"},
    {"description": "ТестИмп_Второй"}
], ensure_ascii=False)
print(tool("import_data", {"metaType": "Catalogs", "name": "Склады", "data": data}))

print("\n=== ТЕСТ 2: clear_deleted (dryRun=true) ===")
print(tool("clear_deleted", {"dryRun": True}))

print("\n=== ТЕСТ 3: get_data_history (Склады, 24ч) ===")
print(tool("get_data_history", {"metaType": "Catalogs", "name": "Склады", "lastMinutes": 1440}))

# Очистка: пометить тестовые на удаление
print("\n=== Очистка: удаление тестовых ===")
print(tool("delete_object", {"metaType": "Catalogs", "name": "Склады", "searchValue": "ТестИмп_Первый", "force": True}))
print(tool("delete_object", {"metaType": "Catalogs", "name": "Склады", "searchValue": "ТестИмп_Второй", "force": True}))
