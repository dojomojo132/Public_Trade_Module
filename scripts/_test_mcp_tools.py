# -*- coding: utf-8 -*-
"""Тестирование MCP-инструментов через HTTP."""
import json
import urllib.request
import sys

MCP_URL = "http://localhost/PTM_Clean/hs/mcp/mcp"

def call_tool(tool_name, arguments):
    """Вызвать MCP-инструмент и вернуть результат."""
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        },
        "id": 1
    }
    
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        MCP_URL,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        return {"error": f"HTTP {e.code}", "body": body}
    except Exception as e:
        return {"error": str(e)}


def print_result(name, result):
    """Красиво вывести результат."""
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    
    if "error" in result:
        print(f"ОШИБКА: {result['error']}")
        if "body" in result:
            print(f"Тело: {result['body'][:500]}")
        return False
    
    r = result.get("result", {})
    is_error = r.get("isError", False)
    
    content = r.get("content", [])
    for item in content:
        text = item.get("text", "")
        print(text[:1000])
    
    if is_error:
        print("\n>>> ОШИБКА в инструменте!")
        return False
    else:
        print("\n>>> УСПЕХ!")
        return True


# === ТЕСТЫ ===

print("=" * 60)
print("ТЕСТИРОВАНИЕ MCP-ИНСТРУМЕНТОВ")
print("=" * 60)

results = {}

# 1. execute_query — простой запрос
r = call_tool("execute_query", {
    "queryText": "ВЫБРАТЬ ПЕРВЫЕ 5 Наименование, Код ИЗ Справочник.Номенклатура",
    "maxRows": 5
})
results["execute_query"] = print_result("execute_query (Номенклатура)", r)

# 2. get_register_data — All
r = call_tool("get_register_data", {
    "registerType": "InformationRegisters",
    "name": "ЦеныНоменклатуры",
    "mode": "SliceLast",
    "maxRows": 5
})
results["get_register_data(SliceLast)"] = print_result("get_register_data (ЦеныНоменклатуры, SliceLast)", r)

# 3. get_register_data — Balance
r = call_tool("get_register_data", {
    "registerType": "AccumulationRegisters",
    "name": "ОстаткиТоваров",
    "mode": "Balance",
    "maxRows": 5
})
results["get_register_data(Balance)"] = print_result("get_register_data (ОстаткиТоваров, Balance)", r)

# 4. list_enum_values
r = call_tool("list_enum_values", {
    "name": "ВидыОплаты"
})
results["list_enum_values"] = print_result("list_enum_values (ВидыОплаты)", r)

# 5. get_predefined_values
r = call_tool("get_predefined_values", {
    "metaType": "Catalogs",
    "name": "Номенклатура"
})
results["get_predefined_values"] = print_result("get_predefined_values (Номенклатура)", r)

# 6. list_metadata_objects (уже существовал)
r = call_tool("list_metadata_objects", {
    "metaType": "Documents",
    "maxItems": 5
})
results["list_metadata_objects"] = print_result("list_metadata_objects (Documents)", r)

# === Phase 2 инструменты ===

# 7. get_object_module — модуль общего модуля
r = call_tool("get_object_module", {
    "metaType": "CommonModules",
    "name": "РаботаСТорговымОборудованием",
    "moduleType": "ObjectModule"
})
results["get_object_module"] = print_result("get_object_module (CommonModules.РаботаСТорговымОборудованием)", r)

# 8. execute_code — простой код
r = call_tool("execute_code", {
    "code": "Результат = 2 + 3;"
})
results["execute_code"] = print_result("execute_code (2+3)", r)

# 9. get_users_list
r = call_tool("get_users_list", {})
results["get_users_list"] = print_result("get_users_list", r)

# 10. get_event_log
r = call_tool("get_event_log", {
    "level": "Error",
    "lastMinutes": 60,
    "maxRows": 10
})
results["get_event_log"] = print_result("get_event_log (Error, 60min)", r)

# === ИТОГО ===
print("\n" + "=" * 60)
print("ИТОГО:")
print("=" * 60)
for name, ok in results.items():
    status = "✓ OK" if ok else "✗ FAIL"
    print(f"  {status}  {name}")
