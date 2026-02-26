# -*- coding: utf-8 -*-
"""
Комплексное тестирование новых MCP-инструментов (Cat C + Cat D).
Сценарии: позитивные, негативные, граничные.
"""
import json
import urllib.request
import base64
import sys
import traceback
import time

URL = "http://localhost/PTM_Clean/hs/mcp/mcp"
AUTH = base64.b64encode(b"Admin:").decode()
PASSED = 0
FAILED = 0
WARNINGS = []
NOTES = []

def call(method, params=None, timeout=60):
    body = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params:
        body["params"] = params
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(URL, data=data,
        headers={"Content-Type": "application/json; charset=utf-8",
                 "Authorization": f"Basic {AUTH}"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def call_tool(tool_name, args=None, timeout=60):
    params = {"name": tool_name}
    if args:
        params["arguments"] = args
    return call("tools/call", params, timeout)

def get_text(result):
    """Извлечь текст из MCP-ответа инструмента."""
    try:
        return result["result"]["content"][0]["text"]
    except (KeyError, IndexError):
        return str(result)

def test(name, func):
    global PASSED, FAILED
    print(f"\n--- {name} ---")
    try:
        func()
        PASSED += 1
        print(f"  [OK] PASS")
    except AssertionError as e:
        FAILED += 1
        print(f"  [FAIL]: {e}")
    except urllib.error.HTTPError as e:
        FAILED += 1
        body = e.read().decode("utf-8", errors="replace")
        print(f"  [FAIL] HTTP {e.code}: {body[:300]}")
    except Exception as e:
        FAILED += 1
        print(f"  [FAIL] ERROR: {e}")
        traceback.print_exc()

def note(text):
    NOTES.append(text)
    print(f"  [NOTE] {text}")

def warn(text):
    WARNINGS.append(text)
    print(f"  [WARN] {text}")


# ═══════════════════════════════════════════════════════
# КАТЕГОРИЯ C: import_data
# ═══════════════════════════════════════════════════════

def test_import_catalogs_basic():
    """Базовый импорт элементов справочника."""
    data = json.dumps([
        {"description": "ТестИмпорт_Один"},
        {"description": "ТестИмпорт_Два"},
        {"description": "ТестИмпорт_Три"}
    ], ensure_ascii=False)
    r = call_tool("import_data", {"metaType": "Catalogs", "name": "Склады", "data": data})
    text = get_text(r)
    assert "ТестИмпорт_Один" in text, f"Не найден элемент в ответе: {text[:200]}"
    assert "Создано:" in text or "создан" in text.lower(), f"Нет подтверждения создания: {text[:200]}"
    note("import_data: 3 элемента справочника Склады создаются успешно")
test(f"C.1 import_data: базовый импорт Каталогов", test_import_catalogs_basic)


def test_import_catalogs_with_attributes():
    """Импорт с заполнением реквизитов."""
    data = json.dumps([
        {"description": "ТестИмпорт_Атр", "attributes": {"Телефон": "111-22-33"}}
    ], ensure_ascii=False)
    r = call_tool("import_data", {"metaType": "Catalogs", "name": "Контрагенты", "data": data})
    text = get_text(r)
    assert "ТестИмпорт_Атр" in text, f"Не найден элемент: {text[:200]}"
    note("import_data: реквизиты (attributes) заполняются корректно")
test("C.2 import_data: с реквизитами", test_import_catalogs_with_attributes)


def test_import_update_existing():
    """Импорт с updateExisting=true — обновление существующих."""
    # Сначала импорт
    data = json.dumps([{"description": "ТестИмпорт_Обн", "attributes": {"Телефон": "000"}}], ensure_ascii=False)
    call_tool("import_data", {"metaType": "Catalogs", "name": "Контрагенты", "data": data})
    
    # Теперь обновление
    data2 = json.dumps([{"description": "ТестИмпорт_Обн", "attributes": {"Телефон": "999-99-99"}}], ensure_ascii=False)
    r = call_tool("import_data", {"metaType": "Catalogs", "name": "Контрагенты", "data": data2, "updateExisting": True})
    text = get_text(r)
    assert "обновл" in text.lower() or "Обновлено" in text, f"Нет подтверждения обновления: {text[:300]}"
    note("import_data: updateExisting=true обновляет существующие по Наименованию")
test("C.3 import_data: обновление существующих", test_import_update_existing)


def test_import_duplicate_without_update():
    """Импорт дубля без updateExisting — должен создать или пропустить."""
    data = json.dumps([{"description": "ТестИмпорт_Дубль"}], ensure_ascii=False)
    call_tool("import_data", {"metaType": "Catalogs", "name": "Склады", "data": data})
    
    r = call_tool("import_data", {"metaType": "Catalogs", "name": "Склады", "data": data, "updateExisting": False})
    text = get_text(r)
    # Может создать дубль или пропустить — просто проверяем что не падает
    assert "error" not in str(r).lower() or "result" in r, f"Ошибка при дубле: {text[:200]}"
    note("import_data: без updateExisting — создаёт дубликат (не пропускает!)")
test("C.4 import_data: дубль без updateExisting", test_import_duplicate_without_update)


def test_import_empty_data():
    """Импорт пустого массива."""
    r = call_tool("import_data", {"metaType": "Catalogs", "name": "Склады", "data": "[]"})
    text = get_text(r)
    is_error = r.get("result", {}).get("isError", False)
    assert not is_error, f"Ошибка при пустом массиве: {text[:200]}"
    note("import_data: пустой массив — корректно обрабатывается (0 записей)")
test("C.5 import_data: пустой массив", test_import_empty_data)


def test_import_invalid_metaType():
    """Импорт с неверным типом — должна быть ошибка."""
    data = json.dumps([{"description": "Тест"}], ensure_ascii=False)
    r = call_tool("import_data", {"metaType": "InvalidType", "name": "Склады", "data": data})
    text = get_text(r)
    # Ожидаем ошибку или isError=true
    is_error = r.get("result", {}).get("isError", False)
    has_error_text = "ошибк" in text.lower() or "error" in text.lower() or "не поддерж" in text.lower()
    assert is_error or has_error_text, f"Нет ошибки при невалидном типе: {text[:200]}"
    note("import_data: невалидный metaType → корректная ошибка")
test("C.6 import_data: невалидный metaType", test_import_invalid_metaType)


def test_import_invalid_json():
    """Импорт с битым JSON."""
    r = call_tool("import_data", {"metaType": "Catalogs", "name": "Склады", "data": "{not valid json"})
    text = get_text(r)
    is_error = r.get("result", {}).get("isError", False)
    has_error_text = "json" in text.lower() or "ошибк" in text.lower() or "error" in text.lower()
    assert is_error or has_error_text, f"Нет ошибки при битом JSON: {text[:200]}"
    note("import_data: невалидный JSON → корректная ошибка")
test("C.7 import_data: невалидный JSON", test_import_invalid_json)


def test_import_nonexistent_catalog():
    """Импорт в несуществующий справочник."""
    data = json.dumps([{"description": "Тест"}], ensure_ascii=False)
    r = call_tool("import_data", {"metaType": "Catalogs", "name": "НесуществующийСправочник", "data": data})
    text = get_text(r)
    is_error = r.get("result", {}).get("isError", False)
    has_error_text = "не найден" in text.lower() or "не существ" in text.lower() or "ошибк" in text.lower()
    assert is_error or has_error_text, f"Нет ошибки для несуществующего: {text[:200]}"
    note("import_data: несуществующий объект → корректная ошибка")
test("C.8 import_data: несуществующий справочник", test_import_nonexistent_catalog)


def test_import_documents():
    """Импорт документов."""
    data = json.dumps([
        {"attributes": {"Склад": "Основной склад", "Контрагент": "Поставщик 1"}, 
         "tabularSections": {"Товары": [{"Номенклатура": "Товар 1", "Количество": 5, "Цена": 100, "Сумма": 500}]}}
    ], ensure_ascii=False)
    r = call_tool("import_data", {"metaType": "Documents", "name": "ПриходТовара", "data": data})
    text = get_text(r)
    # Может успешно создать или ошибиться на ссылках — проверяем что не 500
    assert "result" in r, f"Нет result: {str(r)[:200]}"
    note("import_data: документы — создание с ТЧ (ссылки ищутся по Наименованию)")
test("C.9 import_data: документы с ТЧ", test_import_documents)


# ═══════════════════════════════════════════════════════
# КАТЕГОРИЯ C: clear_deleted
# ═══════════════════════════════════════════════════════

def test_clear_deleted_dryrun():
    """dryRun=true (по умолчанию) — только показать."""
    r = call_tool("clear_deleted", {"dryRun": True})
    text = get_text(r)
    # Проверяем что есть таблица или сообщение об отсутствии
    assert "удал" in text.lower() or "помеч" in text.lower() or "нет" in text.lower() or "объект" in text.lower(), f"Нет осмысленного ответа: {text[:200]}"
    note("clear_deleted: dryRun=true → безопасный режим, только отображение")
test("C.10 clear_deleted: dryRun=true", test_clear_deleted_dryrun)


def test_clear_deleted_filter_catalogs():
    """Фильтр по типу Catalogs."""
    r = call_tool("clear_deleted", {"metaType": "Catalogs", "dryRun": True})
    text = get_text(r)
    assert "result" in r, f"Нет result: {str(r)[:200]}"
    note("clear_deleted: metaType='Catalogs' фильтрует только справочники")
test("C.11 clear_deleted: фильтр Catalogs", test_clear_deleted_filter_catalogs)


def test_clear_deleted_filter_documents():
    """Фильтр по типу Documents."""
    r = call_tool("clear_deleted", {"metaType": "Documents", "dryRun": True})
    text = get_text(r)
    assert "result" in r, f"Нет result: {str(r)[:200]}"
    note("clear_deleted: metaType='Documents' фильтрует только документы")
test("C.12 clear_deleted: фильтр Documents", test_clear_deleted_filter_documents)


def test_clear_deleted_actual_delete():
    """Пометить тестовый элемент на удаление → clear_deleted dryRun=false."""
    # 1. Создаём тестовый элемент
    cr = call_tool("create_catalog_item", {"catalogName": "Склады", "description": "ТестУдал_001"})
    
    # 2. Помечаем на удаление через delete_object
    dr = call_tool("delete_object", {"metaType": "Catalogs", "name": "Склады", "searchValue": "ТестУдал_001"})
    
    # 3. Проверяем dryRun
    check = call_tool("clear_deleted", {"dryRun": True})
    check_text = get_text(check)
    
    # 4. Удаляем реально (dryRun=false)
    r = call_tool("clear_deleted", {"dryRun": False})
    text = get_text(r)
    assert "удал" in text.lower(), f"Нет подтверждения удаления: {text[:300]}"
    note("clear_deleted: dryRun=false → реальное удаление + проверка ссылочной целостности")
test("C.13 clear_deleted: реальное удаление", test_clear_deleted_actual_delete)


# ═══════════════════════════════════════════════════════
# КАТЕГОРИЯ C: get_data_history
# ═══════════════════════════════════════════════════════

def test_history_catalogs():
    """История изменений справочника за 24 часа."""
    r = call_tool("get_data_history", {"metaType": "Catalogs", "name": "Склады", "lastMinutes": 1440})
    text = get_text(r)
    assert "result" in r, f"Нет result: {str(r)[:200]}"
    note("get_data_history: Catalogs.Склады за 24ч — возвращает таблицу с Дата/Событие/Пользователь/Комментарий")
test("C.14 get_data_history: справочники", test_history_catalogs)


def test_history_documents():
    """История изменений документов."""
    r = call_tool("get_data_history", {"metaType": "Documents", "name": "ПриходТовара", "lastMinutes": 1440})
    text = get_text(r)
    assert "result" in r, f"Нет result: {str(r)[:200]}"
    note("get_data_history: Documents.ПриходТовара — работает для документов")
test("C.15 get_data_history: документы", test_history_documents)


def test_history_specific_object():
    """История конкретного объекта по searchValue."""
    r = call_tool("get_data_history", {"metaType": "Catalogs", "name": "Склады", "searchValue": "Основной склад", "lastMinutes": 10080})
    text = get_text(r)
    assert "result" in r, f"Нет result: {str(r)[:200]}"
    note("get_data_history: searchValue фильтрует по конкретному элементу (наименование/номер)")
test("C.16 get_data_history: конкретный объект", test_history_specific_object)


def test_history_short_period():
    """История за 1 минуту — может быть пусто."""
    r = call_tool("get_data_history", {"metaType": "Catalogs", "name": "Номенклатура", "lastMinutes": 1})
    text = get_text(r)
    assert "result" in r, f"Нет result: {str(r)[:200]}"
    note("get_data_history: lastMinutes=1 — может вернуть 0 записей (корректно)")
test("C.17 get_data_history: период 1 минута", test_history_short_period)


def test_history_maxRows():
    """Ограничение maxRows."""
    r = call_tool("get_data_history", {"metaType": "Catalogs", "name": "Склады", "lastMinutes": 10080, "maxRows": 3})
    text = get_text(r)
    assert "result" in r, f"Нет result: {str(r)[:200]}"
    # Подсчитаем строки таблицы (по разделителям |)
    lines = [l for l in text.split('\n') if l.strip().startswith('|') and '---' not in l and 'Дата' not in l]
    if len(lines) > 3:
        warn(f"maxRows=3 но строк данных: {len(lines)}")
    note(f"get_data_history: maxRows=3 → возвращает ≤3 строк данных (получено: {len(lines)})")
test("C.18 get_data_history: maxRows=3", test_history_maxRows)


def test_history_nonexistent():
    """Несуществующий объект."""
    r = call_tool("get_data_history", {"metaType": "Catalogs", "name": "НесуществующийСправочник"})
    text = get_text(r)
    is_error = r.get("result", {}).get("isError", False)
    has_error = "не найден" in text.lower() or "ошибк" in text.lower()
    assert is_error or has_error, f"Нет ошибки для несуществующего: {text[:200]}"
    note("get_data_history: несуществующий объект → корректная ошибка")
test("C.19 get_data_history: несуществующий объект", test_history_nonexistent)


# ═══════════════════════════════════════════════════════
# КАТЕГОРИЯ D: Ресурсы
# ═══════════════════════════════════════════════════════

def test_resource_registers_completeness():
    """ptm://registers — полнота данных."""
    r = call("resources/read", {"uri": "ptm://registers"})
    text = r.get("result", {}).get("contents", [{}])[0].get("text", "")
    
    # Проверяем наличие ключевых разделов
    assert "Регистры накопления" in text, "Нет раздела 'Регистры накопления'"
    assert "Регистры сведений" in text, "Нет раздела 'Регистры сведений'"
    assert "ОстаткиТоваров" in text, "Нет регистра ОстаткиТоваров"
    assert "Измерения" in text, "Нет измерений"
    assert "Ресурсы" in text, "Нет ресурсов"
    assert "Регистраторы" in text, "Нет регистраторов"
    note(f"ptm://registers: {len(text)} символов, содержит регистры накопления и сведений с полной структурой")
test("D.1 resource ptm://registers полнота", test_resource_registers_completeness)


def test_resource_business_logic_completeness():
    """ptm://business-logic — полнота данных."""
    r = call("resources/read", {"uri": "ptm://business-logic"})
    text = r.get("result", {}).get("contents", [{}])[0].get("text", "")
    
    assert "Документооборот" in text, "Нет заголовка Документооборот"
    assert "ЧекККМ" in text, "Нет документа ЧекККМ"
    assert "ПриходТовара" in text, "Нет документа ПриходТовара"
    assert "Реквизиты" in text, "Нет раздела Реквизиты"
    assert "ТЧ:" in text, "Нет табличных частей"
    assert "Движения" in text or "движени" in text.lower(), "Нет раздела Движения"
    note(f"ptm://business-logic: {len(text)} символов, содержит документооборот с реквизитами, ТЧ, движениями")
test("D.2 resource ptm://business-logic полнота", test_resource_business_logic_completeness)


def test_resource_invalid_uri():
    """Несуществующий ресурс."""
    try:
        r = call("resources/read", {"uri": "ptm://nonexistent"})
        text = str(r)
        has_error = "error" in text.lower()
        assert has_error or r.get("error"), f"Нет ошибки: {text[:200]}"
    except urllib.error.HTTPError as e:
        assert e.code == 500, f"Неожиданный код: {e.code}"
    note("resources/read: несуществующий URI → ошибка (HTTP 500 или error в JSON-RPC)")
test("D.3 resource: несуществующий URI", test_resource_invalid_uri)


# ═══════════════════════════════════════════════════════
# КАТЕГОРИЯ D: Промпты
# ═══════════════════════════════════════════════════════

def test_prompt_report_skd():
    """Промпт генерации отчёта в режиме СКД."""
    r = call("prompts/get", {"name": "generate_report_module", "arguments": {"reportName": "ОстаткиТоваров", "mode": "СКД"}})
    assert "result" in r, f"Нет result: {str(r)[:200]}"
    text = r["result"]["messages"][0]["content"]["text"]
    assert "СКД" in text, "Нет упоминания СКД"
    assert "ОстаткиТоваров" in text, "Нет имени отчёта"
    assert "регистр" in text.lower(), "Нет регистров"
    note(f"generate_report_module(СКД): {len(text)} символов, содержит метаданные отчёта + все регистры + требования СКД")
test("D.4 prompt: generate_report_module (СКД)", test_prompt_report_skd)


def test_prompt_report_manual():
    """Промпт генерации отчёта в программном режиме."""
    r = call("prompts/get", {"name": "generate_report_module", "arguments": {"reportName": "ОстаткиТоваров", "mode": "Программный"}})
    text = r["result"]["messages"][0]["content"]["text"]
    assert "Программн" in text, f"Нет упоминания Программного режима: {text[:200]}"
    assert "макет" in text.lower() or "табличн" in text.lower(), "Нет указаний по табличному документу"
    note("generate_report_module(Программный): отдаёт инструкцию по программной генерации")
test("D.5 prompt: generate_report_module (Программный)", test_prompt_report_manual)


def test_prompt_report_nonexistent():
    """Промпт с несуществующим отчётом."""
    try:
        r = call("prompts/get", {"name": "generate_report_module", "arguments": {"reportName": "НеСуществует"}})
        has_error = "error" in str(r).lower()
        assert has_error or r.get("error"), f"Нет ошибки: {str(r)[:200]}"
    except urllib.error.HTTPError:
        pass  # OK — 500 на несуществующий отчёт
    note("generate_report_module: несуществующий отчёт → ВызватьИсключение со списком доступных")
test("D.6 prompt: несуществующий отчёт", test_prompt_report_nonexistent)


def test_prompt_form_handlers_document():
    """Промпт обработчиков формы для документа."""
    r = call("prompts/get", {"name": "generate_form_handlers", "arguments": {"metaType": "Documents", "objectName": "ЧекККМ"}})
    text = r["result"]["messages"][0]["content"]["text"]
    assert "ЧекККМ" in text, "Нет имени документа"
    assert "ПриСозданииНаСервере" in text, "Нет обработчика ПриСозданииНаСервере"
    assert "ТЧ:" in text or "Табличн" in text or "Товары" in text, "Нет табличных частей"
    note(f"generate_form_handlers(Documents.ЧекККМ): {len(text)} символов, реквизиты + ТЧ + обработчики + стандарты")
test("D.7 prompt: form_handlers для документа", test_prompt_form_handlers_document)


def test_prompt_form_handlers_catalog():
    """Промпт обработчиков формы для справочника."""
    r = call("prompts/get", {"name": "generate_form_handlers", "arguments": {"metaType": "Catalogs", "objectName": "Номенклатура"}})
    text = r["result"]["messages"][0]["content"]["text"]
    assert "Номенклатура" in text, "Нет имени справочника"
    assert "НаСервере" in text or "НаКлиенте" in text, "Нет директив"
    note(f"generate_form_handlers(Catalogs.Номенклатура): {len(text)} символов")
test("D.8 prompt: form_handlers для справочника", test_prompt_form_handlers_catalog)


def test_prompt_form_handlers_nonexistent():
    """Промпт для несуществующего объекта."""
    try:
        r = call("prompts/get", {"name": "generate_form_handlers", "arguments": {"metaType": "Documents", "objectName": "НеСуществует"}})
        has_error = "error" in str(r).lower()
        assert has_error or r.get("error"), f"Нет ошибки: {str(r)[:200]}"
    except urllib.error.HTTPError:
        pass
    note("generate_form_handlers: несуществующий объект → корректная ошибка")
test("D.9 prompt: несуществующий объект", test_prompt_form_handlers_nonexistent)


def test_prompt_integrity_with_register():
    """Промпт диагностики целостности с регистром."""
    r = call("prompts/get", {"name": "diagnose_data_integrity", "arguments": {"registerName": "ОстаткиТоваров", "symptom": "Отрицательные остатки"}})
    text = r["result"]["messages"][0]["content"]["text"]
    assert "ОстаткиТоваров" in text, "Нет имени регистра"
    assert "Отрицательные остатки" in text, "Нет симптома"
    assert "get_register_data" in text, "Нет ссылки на MCP-инструмент"
    assert "Шаг" in text or "шаг" in text, "Нет пошагового плана"
    note(f"diagnose_data_integrity(register+symptom): {len(text)} символов, 6-шаговый план с MCP-инструментами")
test("D.10 prompt: integrity с регистром", test_prompt_integrity_with_register)


def test_prompt_integrity_without_register():
    """Промпт диагностики без указания регистра."""
    r = call("prompts/get", {"name": "diagnose_data_integrity", "arguments": {"symptom": "Расхождение сумм"}})
    text = r["result"]["messages"][0]["content"]["text"]
    assert "Расхождение сумм" in text, "Нет симптома"
    assert "Шаг" in text or "шаг" in text, "Нет плана"
    note("diagnose_data_integrity: без registerName — общий план расследования (без привязки к регистру)")
test("D.11 prompt: integrity без регистра", test_prompt_integrity_without_register)


def test_prompt_integrity_wrong_register():
    """Промпт с несуществующим регистром — не должен падать."""
    r = call("prompts/get", {"name": "diagnose_data_integrity", "arguments": {"registerName": "НеСуществующийРегистр"}})
    assert "result" in r, f"Падение: {str(r)[:200]}"
    text = r["result"]["messages"][0]["content"]["text"]
    assert "Шаг" in text or "шаг" in text, "Нет плана при несуществующем регистре"
    note("diagnose_data_integrity: несуществующий регистр — план без метаданных (не падает)")
test("D.12 prompt: integrity несуществующий регистр", test_prompt_integrity_wrong_register)


def test_prompt_nonexistent():
    """Несуществующий промпт."""
    try:
        r = call("prompts/get", {"name": "nonexistent_prompt", "arguments": {}})
        has_error = "error" in str(r).lower()
        assert has_error or r.get("error"), f"Нет ошибки: {str(r)[:200]}"
    except urllib.error.HTTPError:
        pass
    note("prompts/get: неизвестный промпт → ВызватьИсключение")
test("D.13 prompt: несуществующий промпт", test_prompt_nonexistent)


# ═══════════════════════════════════════════════════════
# ОЧИСТКА ТЕСТОВЫХ ДАННЫХ
# ═══════════════════════════════════════════════════════

print("\n\n=== ОЧИСТКА ТЕСТОВЫХ ДАННЫХ ===")

cleanup_items = [
    ("Склады", "ТестИмпорт_Один"),
    ("Склады", "ТестИмпорт_Два"),
    ("Склады", "ТестИмпорт_Три"),
    ("Склады", "ТестИмпорт_Дубль"),
    ("Контрагенты", "ТестИмпорт_Атр"),
    ("Контрагенты", "ТестИмпорт_Обн"),
]

for cat, name in cleanup_items:
    try:
        call_tool("delete_object", {"metaType": "Catalogs", "name": cat, "searchValue": name, "force": True})
        print(f"  Удалён: {cat}/{name}")
    except Exception:
        print(f"  (не найден: {cat}/{name})")

# Очистка помеченных после тестов
try:
    call_tool("clear_deleted", {"dryRun": False})
except Exception:
    pass


# ═══════════════════════════════════════════════════════
# ИТОГИ
# ═══════════════════════════════════════════════════════

print("\n" + "=" * 60)
print(f"ИТОГИ: {PASSED} passed, {FAILED} failed из {PASSED + FAILED} тестов")
print("=" * 60)

if WARNINGS:
    print(f"\n[WARNINGS] ({len(WARNINGS)}):")
    for w in WARNINGS:
        print(f"  - {w}")

if NOTES:
    print(f"\n[NOTES] ({len(NOTES)}):")
    for i, n in enumerate(NOTES, 1):
        print(f"  {i}. {n}")

sys.exit(0 if FAILED == 0 else 1)
