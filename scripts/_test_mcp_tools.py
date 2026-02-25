# -*- coding: utf-8 -*-
"""Тестирование MCP-инструментов через HTTP."""
import json
import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

MCP_URL = "http://localhost/PTM_Clean/hs/mcp/mcp"

def call_tool(tool_name, arguments):
    """Вызвать MCP-инструмент и вернуть результат."""
    return call_mcp("tools/call", {"name": tool_name, "arguments": arguments})


def call_mcp(method, params):
    """Вызвать любой MCP-метод и вернуть результат."""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
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

# === Phase 3 инструменты ===

# 11. get_form_structure — структура формы документа
r = call_tool("get_form_structure", {
    "metaType": "Documents",
    "name": "ЧекККМ"
})
results["get_form_structure(list)"] = print_result("get_form_structure (Documents.ЧекККМ — список форм)", r)

# 12. get_form_structure — конкретная форма
r = call_tool("get_form_structure", {
    "metaType": "Documents",
    "name": "ЧекККМ",
    "formName": "ФормаДокумента"
})
results["get_form_structure(form)"] = print_result("get_form_structure (Documents.ЧекККМ.ФормаДокумента)", r)

# 13. get_subsystem_content — состав подсистемы
r = call_tool("get_subsystem_content", {
    "name": "Торговля"
})
results["get_subsystem_content"] = print_result("get_subsystem_content (Торговля)", r)

# 14. post_document — проведение документа (может не быть документов, допускаем ошибку)
r = call_tool("post_document", {
    "documentType": "ЧекККМ",
    "documentNumber": "000000001",
    "action": "post"
})
results["post_document"] = print_result("post_document (ЧекККМ, 000000001)", r)

# 15. find_references — поиск ссылок
r = call_tool("find_references", {
    "metaType": "Catalogs",
    "name": "Номенклатура",
    "searchValue": "000002078"
})
results["find_references"] = print_result("find_references (Справочник.Номенклатура, код 000002078)", r)

# === Phase 4 инструменты ===

# 16. get_configuration_overview
r = call_tool("get_configuration_overview", {})
results["get_configuration_overview"] = print_result("get_configuration_overview", r)

# 17. get_connected_objects
r = call_tool("get_connected_objects", {
    "metaType": "Catalogs",
    "name": "Номенклатура"
})
results["get_connected_objects"] = print_result("get_connected_objects (Номенклатура)", r)

# 18. validate_metadata_integrity
r = call_tool("validate_metadata_integrity", {
    "metaType": "Catalogs"
})
results["validate_metadata_integrity"] = print_result("validate_metadata_integrity (Catalogs)", r)

# 19. check_document_posting
r = call_tool("check_document_posting", {
    "documentType": "ЧекККМ"
})
results["check_document_posting"] = print_result("check_document_posting (ЧекККМ)", r)

# === Phase 5 инструменты ===

# 20. get_metadata_structure
r = call_tool("get_metadata_structure", {
    "metaType": "Documents",
    "name": "ЧекККМ"
})
results["get_metadata_structure"] = print_result("get_metadata_structure (Documents.ЧекККМ)", r)

# === Phase 6: Resources & Prompts ===

# 21. resources/list
r = call_mcp("resources/list", {})
print(f"\n{'='*60}")
print(f"  resources/list")
print(f"{'='*60}")
if "error" in r:
    print(f"ОШИБКА: {r['error']}")
    results["resources/list"] = False
else:
    res_list = r.get("result", {}).get("resources", [])
    print(f"Найдено ресурсов: {len(res_list)}")
    for res_item in res_list:
        print(f"  - {res_item.get('uri', '?')} ({res_item.get('name', '?')})")
    results["resources/list"] = len(res_list) > 0
    print("\n>>> УСПЕХ!" if results["resources/list"] else "\n>>> ОШИБКА: 0 ресурсов!")

# 22. resources/read (ptm://datamodel)
r = call_mcp("resources/read", {"uri": "ptm://datamodel"})
print(f"\n{'='*60}")
print(f"  resources/read (ptm://datamodel)")
print(f"{'='*60}")
if "error" in r:
    print(f"ОШИБКА: {r['error']}")
    results["resources/read"] = False
else:
    contents = r.get("result", {}).get("contents", [])
    if contents:
        text = contents[0].get("text", "")
        print(text[:800])
        results["resources/read"] = len(text) > 50
    else:
        print("Пустой ответ")
        results["resources/read"] = False
    print("\n>>> УСПЕХ!" if results["resources/read"] else "\n>>> ОШИБКА!")

# 23. prompts/list
r = call_mcp("prompts/list", {})
print(f"\n{'='*60}")
print(f"  prompts/list")
print(f"{'='*60}")
if "error" in r:
    print(f"ОШИБКА: {r['error']}")
    results["prompts/list"] = False
else:
    prompts_list = r.get("result", {}).get("prompts", [])
    print(f"Найдено промптов: {len(prompts_list)}")
    for p in prompts_list:
        args_list = [a.get("name", "?") for a in p.get("arguments", [])]
        print(f"  - {p.get('name', '?')} ({', '.join(args_list)})")
    results["prompts/list"] = len(prompts_list) >= 3
    print("\n>>> УСПЕХ!" if results["prompts/list"] else "\n>>> ОШИБКА: < 3 промптов!")

# 24. prompts/get (generate_posting_module)
r = call_mcp("prompts/get", {"name": "generate_posting_module", "arguments": {"documentName": "ЧекККМ"}})
print(f"\n{'='*60}")
print(f"  prompts/get (generate_posting_module, ЧекККМ)")
print(f"{'='*60}")
if "error" in r:
    print(f"ОШИБКА: {r['error']}")
    results["prompts/get"] = False
else:
    messages = r.get("result", {}).get("messages", [])
    if messages:
        text = messages[0].get("content", {}).get("text", "")
        print(text[:800])
        results["prompts/get"] = len(text) > 50
    else:
        print("Нет сообщений в ответе")
        results["prompts/get"] = False
    print("\n>>> УСПЕХ!" if results["prompts/get"] else "\n>>> ОШИБКА!")

# === ИТОГО ===
print("\n" + "=" * 60)
print("ИТОГО:")
print("=" * 60)
passed = 0
failed = 0
for name, ok in results.items():
    status = "✓ OK" if ok else "✗ FAIL"
    print(f"  {status}  {name}")
    if ok:
        passed += 1
    else:
        failed += 1
print(f"\n  Всего: {passed + failed} | Успешно: {passed} | Ошибки: {failed}")
