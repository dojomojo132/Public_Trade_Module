# -*- coding: utf-8 -*-
"""Тест get_document_movements - движения документа."""
import json
import urllib.request

MCP_URL = "http://localhost/PTM_Clean/hs/mcp/mcp"

def call_tool(tool_name, arguments):
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
        "id": 1
    }
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(MCP_URL, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))

# 1. Найти проведённый документ
print("=== 1. Поиск проведённого документа ЧекККМ ===")
r = call_tool("execute_query", {
    "queryText": "ВЫБРАТЬ ПЕРВЫЕ 1 Номер, Дата ИЗ Документ.ЧекККМ ГДЕ Проведен = ИСТИНА УПОРЯДОЧИТЬ ПО Дата УБЫВ",
    "maxRows": 1
})
for item in r.get("result", {}).get("content", []):
    print(item.get("text", ""))

# Вытащим номер из результата
text = r.get("result", {}).get("content", [{}])[0].get("text", "")
lines = text.strip().split('\n')
if len(lines) >= 3:
    number = lines[2].split('|')[0].strip()
    print(f"\nНайден номер: '{number}'")
else:
    number = "000000001"
    print(f"\nИспользуем номер по умолчанию: '{number}'")

# 2. Тестируем get_document_movements
print(f"\n=== 2. get_document_movements (ЧекККМ N{number}) ===")
r = call_tool("get_document_movements", {
    "documentType": "ЧекККМ",
    "documentNumber": number,
    "maxRows": 10
})
result = r.get("result", {})
is_error = result.get("isError", False)
for item in result.get("content", []):
    print(item.get("text", "")[:3000])

if is_error:
    print("\n>>> ОШИБКА!")
else:
    print("\n>>> УСПЕХ!")

# 3. Тестируем get_register_data с Turnovers
print(f"\n=== 3. get_register_data (ОстаткиТоваров, Turnovers) ===")
r = call_tool("get_register_data", {
    "registerType": "AccumulationRegisters",
    "name": "ОстаткиТоваров",
    "mode": "Turnovers",
    "maxRows": 3
})
result = r.get("result", {})
is_error = result.get("isError", False)
for item in result.get("content", []):
    print(item.get("text", "")[:2000])

if is_error:
    print("\n>>> ОШИБКА!")
else:
    print("\n>>> УСПЕХ!")
