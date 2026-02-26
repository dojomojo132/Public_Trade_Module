---
description: 'Полный каталог 40+ MCP-инструментов 1С: запросы, метаданные, диагностика, администрирование, данные'
mode: agent
tools:
  - mcp_mcp_1c_torgov/*
---

# Каталог MCP-инструментов 1С

> Также доступно через `tool_search_tool_regex` с паттерном `mcp_mcp_1c_torgov`.

## Запросы и данные

| Инструмент | Описание | Параметры |
|-----------|----------|-----------|
| `execute_query` | Запрос 1С → таблица | `queryText`, `maxRows` |
| `get_register_data` | Остатки/обороты/срез регистра | `registerType`, `name`, `mode` (Balance/Turnovers/SliceLast/All) |
| `get_document_movements` | Движения документа по регистрам | `documentType`, `documentNumber` |
| `search_data` | Поиск по справочникам/документам | `metaType`, `searchString`, `maxRows` |
| `export_data` | Экспорт в JSON/CSV | `metaType`, `format`, `maxRows` |

## Метаданные и структура

| Инструмент | Описание | Параметры |
|-----------|----------|-----------|
| `list_metadata_objects` | Список объектов | `metaType`, `nameMask`, `maxItems` |
| `get_metadata_structure` | Реквизиты, ТЧ, типы | `metaType`, `name` |
| `get_configuration_overview` | Обзор конфигурации | — |
| `get_connected_objects` | Граф зависимостей | `metaType`, `name` |
| `get_form_structure` | Структура формы + пути | `metaType`, `name`, `formName` |
| `get_subsystem_content` | Состав подсистемы | `name` |
| `list_enum_values` | Значения перечисления | `name` |
| `get_predefined_values` | Предопределённые элементы | `metaType`, `name` |

## Код и модули

| Инструмент | Описание | Параметры |
|-----------|----------|-----------|
| `get_object_module` | Путь к BSL-модулю | `metaType`, `name`, `moduleType`, `formName` |
| `execute_code` | Выполнить BSL на сервере | `code`, `safeMode` |
| `analyze_module` | Анализ BSL (процедуры, области) | `code` |

## Диагностика

| Инструмент | Описание | Параметры |
|-----------|----------|-----------|
| `validate_metadata_integrity` | Целостность метаданных | `metaType` |
| `check_document_posting` | Диагностика проведения | `documentType`, `number` |
| `find_references` | Поиск ссылок в БД | `metaType`, `name`, `searchValue` |
| `run_smoke_test` | Smoke-тест форм | `metaType`, `name` |
| `get_data_summary` | Сводка записей | `metaType` |
| `compare_periods` | Сравнение периодов регистра | `registerName`, `period1`, `period2` |
| `get_rights_info` | Права и роли | `metaType`, `name` |
| `get_locks_info` | Блокировки | — |
| `get_data_history` | История изменений из ЖР | `metaType`, `name`, `searchValue`, `lastMinutes` |

## Администрирование

| Инструмент | Описание | Параметры |
|-----------|----------|-----------|
| `get_users_list` | Пользователи с ролями | — |
| `get_event_log` | Журнал регистрации | `level`, `lastMinutes`, `maxRows` |
| `post_document` | Провести/отменить документ | `documentType`, `documentNumber`, `action` |
| `get_constant_value` | Значение константы | `constantName` |
| `set_constant_value` | Установить константу | `constantName`, `value` |
| `get_scheduled_jobs` | Регламентные задания | — |
| `get_session_info` | Текущий сеанс | — |
| `clear_deleted` | Удаление помеченных | `metaType`, `dryRun` |

## Управление данными

| Инструмент | Описание | Параметры |
|-----------|----------|-----------|
| `create_catalog_item` | Создать элемент справочника | `catalogName`, `description`, `attributes` |
| `create_document` | Создать документ | `documentType`, `date`, `attributes`, `post` |
| `update_register_record` | Запись в регистр сведений | `registerName`, `dimensions`, `resources` |
| `delete_object` | Пометить/удалить | `metaType`, `name`, `searchValue`, `force` |
| `update_catalog_item` | Обновить элемент | `catalogName`, `searchValue`, `attributes` |
| `update_document` | Обновить документ | `documentType`, `documentNumber`, `attributes` |
| `bulk_create` | Пакетное создание | `metaType`, `name`, `data` (JSON массив) |
| `import_data` | Импорт JSON | `metaType`, `name`, `data`, `updateExisting` |
| `run_report` | Формирование отчёта | `reportName`, `params` |

## MCP Resources

- `ptm://datamodel` — модель данных конфигурации
- `ptm://registers` — карта регистров: измерения, ресурсы, регистраторы
- `ptm://business-logic` — документооборот: документы → движения → отчёты
- `file://resource/syntax_1c.txt` — синтаксис 1С

## MCP Prompts

- `generate_posting_module` — шаблон модуля проведения
- `create-metadata-object` — чеклист создания объекта
- `diagnose-posting-error` — диагностика ошибки проведения
- `generate_report_module` — шаблон модуля отчёта
- `generate_form_handlers` — шаблон обработчиков формы
- `diagnose_data_integrity` — расследование нарушения целостности
