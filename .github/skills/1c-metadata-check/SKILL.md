---
name: 1c-metadata-check
description: "Verify 1C:Enterprise metadata objects via MCP before making changes. Use when checking if an object exists, verifying its structure, attributes, tabular sections, forms, or connected objects. Ensures InfoBase is the source of truth, not disk files."
---

# Проверка метаданных 1С через MCP

## Когда использовать

- Перед изменением любого объекта метаданных
- Для проверки существования объекта, реквизита, формы, табличной части
- Для выяснения актуальной структуры объекта (ИБ может отличаться от файлов на диске)
- Перед созданием нового объекта (проверить что такого ещё нет)

## Принцип: ИБ = единственный источник истины

```
Приоритет 1 (высший): MCP-инструменты (ИБ)     — актуальная структура
Приоритет 2:          Техническая спецификация  — бизнес-логика
Приоритет 3 (низший): XML/BSL файлы на диске    — может быть устаревшим!
```

## Процедура проверки

### 1. Синхронизация (ОБЯЗАТЕЛЬНО перед работой)

```powershell
$script = Get-ChildItem -Path "D:\Git\Public_Trade_Module" -Recurse -Filter "deploy-config.ps1" | Select-Object -First 1
powershell -ExecutionPolicy Bypass -File $script.FullName -Action Dump
```

Гарантирует: файлы на диске = ИБ.

### 2. Проверка существования объекта

```
MCP → mcp_mcp_1c_torgov_list_metadata_objects
      metaType: "Catalog" / "Document" / "AccumulationRegister" / ...
      nameMask: "ИмяОбъекта"
```

### 3. Проверка структуры объекта

```
MCP → mcp_mcp_1c_torgov_get_metadata_structure
      metaType: "Catalog" / "Document" / ...
      name: "ИмяОбъекта"
```

Возвращает: реквизиты, табличные части, измерения, ресурсы, типы.

### 4. Проверка форм объекта

```
MCP → mcp_mcp_1c_torgov_get_form_structure
      metaType: "Catalog" / "Document" / ...
      name: "ИмяОбъекта"
      formName: "" (пустой → список всех форм)
```

### 5. Проверка связей

```
MCP → mcp_mcp_1c_torgov_get_connected_objects
      metaType: "Catalog" / "Document" / ...
      name: "ИмяОбъекта"
```

Показывает: кто ссылается на объект, на что ссылается объект.

### 6. Обзор конфигурации

```
MCP → mcp_mcp_1c_torgov_get_configuration_overview
```

Возвращает: все объекты конфигурации с количествами.

## Полная таблица MCP-инструментов

### Метаданные и структура

| Инструмент | Описание | Ключевые параметры |
|-----------|----------|-------------------|
| `list_metadata_objects` | Список объектов метаданных | `metaType` (обяз.), `nameMask`, `maxItems` |
| `get_metadata_structure` | Структура объекта (реквизиты, ТЧ, типы) | `metaType`, `name` (обяз.) |
| `get_configuration_overview` | Обзор конфигурации одним вызовом | — |
| `get_connected_objects` | Граф зависимостей объекта | `metaType`, `name` |
| `get_form_structure` | Структура формы + пути к файлам | `metaType`, `name`, `formName` (опц.) |
| `get_subsystem_content` | Состав подсистемы | `name` |
| `list_enum_values` | Значения перечисления | `name` |
| `get_predefined_values` | Предопределённые элементы | `metaType`, `name` |

### Код и модули

| Инструмент | Описание | Ключевые параметры |
|-----------|----------|-------------------|
| `get_object_module` | Путь к BSL-модулю (для read_file) | `metaType`, `name`, `moduleType`, `formName` |
| `execute_code` | Выполнить BSL-код на сервере | `code` (обяз.), `safeMode` |
| `analyze_module` | Анализ BSL-кода (процедуры, области) | `code` (обяз.) |

### Запросы и данные

| Инструмент | Описание | Ключевые параметры |
|-----------|----------|-------------------|
| `execute_query` | Выполнить запрос 1С | `queryText` (обяз.), `maxRows` |
| `get_register_data` | Остатки/обороты/срез регистра | `registerType`, `name`, `mode` (Balance/Turnovers/SliceLast/All) |
| `get_document_movements` | Все движения документа | `documentType`, `documentNumber` |
| `search_data` | Поиск по справочникам/документам | `metaType` (обяз.), `searchString`, `maxRows` |
| `export_data` | Экспорт данных в JSON/CSV | `metaType` (обяз.), `format`, `maxRows` |

### Диагностика

| Инструмент | Описание | Ключевые параметры |
|-----------|----------|-------------------|
| `validate_metadata_integrity` | Проверка целостности | `metaType` (опц.) |
| `check_document_posting` | Диагностика проведения документа | `documentType`, `number` (опц.) |
| `get_tech_journal` | Технологический журнал (ТЖ) | `action` (Check/Setup/Stop/Status), `lastMinutes`, `maxRows`, `eventFilter` |
| `find_references` | Поиск ссылок на элемент в БД | `metaType`, `name`, `searchValue` |
| `run_smoke_test` | Smoke-тест открытия форм | `metaType` (обяз.), `name` (опц.) |
| `get_data_summary` | Сводка записей по таблицам | `metaType` (опц.) |
| `compare_periods` | Сравнение остатков между периодами | `registerName` (обяз.), `period1`, `period2` |
| `get_rights_info` | Права и роли по объекту | `metaType`, `name` |
| `get_locks_info` | Блокировки (сеансы, транзакции) | — |
| `get_data_history` | История изменений из ЖР | `metaType` (обяз.), `name` (обяз.), `searchValue`, `lastMinutes`, `maxRows` |

### Администрирование

| Инструмент | Описание | Ключевые параметры |
|-----------|----------|-------------------|
| `get_users_list` | Пользователи ИБ с ролями | — |
| `get_event_log` | Журнал регистрации 1С | `level`, `lastMinutes`, `maxRows` |
| `post_document` | Провести/отменить документ | `documentType`, `documentNumber`, `action` |
| `get_constant_value` | Значение константы | `constantName` (обяз.) |
| `set_constant_value` | Установить константу | `constantName` (обяз.), `value` (обяз.) |
| `get_scheduled_jobs` | Регламентные задания | — |
| `get_session_info` | Текущий сеанс | — |
| `clear_deleted` | Удаление помеченных | `metaType` (опц.), `dryRun` (default: true) |

### Управление данными

| Инструмент | Описание | Ключевые параметры |
|-----------|----------|-------------------|
| `create_catalog_item` | Создать элемент справочника | `catalogName`, `description`, `attributes` (JSON) |
| `create_document` | Создать и провести документ | `documentType`, `date`, `attributes` (JSON), `post` |
| `update_register_record` | Запись в регистр сведений | `registerName`, `dimensions` (JSON), `resources` (JSON) |
| `delete_object` | Пометить/удалить элемент | `metaType` (обяз.), `name` (обяз.), `searchValue`, `force` |
| `update_catalog_item` | Обновить справочник | `catalogName`, `searchValue`, `attributes` (JSON) |
| `update_document` | Обновить документ | `documentType`, `documentNumber`, `attributes` (JSON) |
| `bulk_create` | Пакетное создание | `metaType` (обяз.), `name` (обяз.), `data` (JSON массив) |
| `import_data` | Импорт данных из JSON | `metaType` (обяз.), `name` (обяз.), `data` (JSON), `updateExisting` |
| `run_report` | Формирование отчёта | `reportName` (обяз.), `params` (JSON, опц.) |

### MCP Resources

| URI | Описание |
|-----|----------|
| `ptm://datamodel` | Полная модель данных конфигурации |
| `ptm://registers` | Карта регистров: измерения, ресурсы, реквизиты |
| `ptm://business-logic` | Карта документооборота: документы → движения → отчёты |
| `file://resource/syntax_1c.txt` | Синтаксис встроенного языка 1С |

### MCP Prompts

| Промпт | Описание | Аргументы |
|--------|----------|-----------|
| `generate_posting_module` | Шаблон модуля проведения | `documentName` |
| `create-metadata-object` | Чеклист создания объекта | `objectType`, `objectName`, `description` |
| `diagnose-posting-error` | Диагностика ошибки проведения | `documentType`, `errorText` |
| `generate_report_module` | Шаблон модуля отчёта | `reportName`, `mode` |
| `generate_form_handlers` | Шаблон обработчиков формы | `metaType`, `objectName` |
| `diagnose_data_integrity` | Диагностика целостности данных | `registerName`, `symptom` |

## Важные правила

- НИКОГДА не угадывать имена полей/объектов/форм — всегда проверять через MCP
- MCP-сервер возвращает объекты расширения с префиксом `mcp_` — их ИГНОРИРОВАТЬ
- Различия между файлом и ИБ — всегда доверять МСР (ИБ)
- После Dump файлы гарантированно = ИБ, но MCP-проверка всё равно полезна для валидации
