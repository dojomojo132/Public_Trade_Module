---
name: 1c-debug
description: "HTTP-отладка 1С:Предприятие через RDBG-протокол. Use when debugging runtime errors, setting breakpoints, stepping through BSL code, inspecting variables, or evaluating expressions in running 1C session."
---

# Отладка 1С:Предприятие через RDBG-протокол

## Когда использовать

- Отладка runtime-ошибок в 1С:Предприятие
- Установка breakpoints в BSL-модулях
- Пошаговое выполнение BSL-кода
- Инспекция переменных и вычисление выражений
- Анализ стека вызовов

## Архитектура

```
VS Code Agent (MCP tools/call)
    ↓ JSON-RPC stdio
scripts/debug/debug_mcp_server.py (MCP Server)
    ↓ Python API
scripts/debug/session.py (Session Manager + Polling Thread)
    ├── scripts/debug/rdbg_client.py → HTTP/XML → dbgs.exe (RDBG)
    ├── scripts/debug/launcher.py → dbgs.exe + 1cv8c.exe processes
    └── scripts/debug/metadata_mapper.py → BSL path → UUID mapping
```

## Конфигурация

Файл: `scripts/debug/debug_config.json`

| Параметр | Описание | Пример |
|----------|----------|--------|
| `platform.root` | Путь к установке 1С | `C:\Program Files\1cv8\8.3.27.1234` |
| `infoBase.path` | Путь к файловой ИБ | `D:\Bases\PTM` |
| `debug.host` | Хост dbgs.exe | `localhost` |
| `debug.portRange` | Диапазон портов | `[1550, 1560]` |
| `workspace.configRoot` | Путь к выгруженной конфигурации | `D:\Git\Public_Trade_Module\Конфигурация` |

**ВАЖНО:** Обновлять `platform.root` при смене версии 1С!

## Инструменты отладки (MCP Server: ptm-debug)

| Инструмент | Описание | Параметры |
|-----------|----------|-----------|
| `debug_connect` | Запуск dbgs.exe → attach → polling | — (ВЫЗЫВАТЬ ПЕРВЫМ!) |
| `debug_disconnect` | Остановка сессии (detach → kill) | — |
| `debug_launch` | Запуск 1С:Предприятие с отладкой | — |
| `debug_set_breakpoints` | Установить breakpoints | `file_path`, `lines[]` |
| `debug_clear_breakpoints` | Очистить breakpoints | `file_path` (опц., все если пусто) |
| `debug_continue` | Продолжить выполнение (F5) | — |
| `debug_step_over` | Шаг через (F10) | — |
| `debug_step_into` | Шаг в (F11) | — |
| `debug_step_out` | Шаг из (Shift+F11) | — |
| `debug_get_stack` | Стек вызовов (с путями к BSL) | — |
| `debug_get_variables` | Локальные переменные текущего фрейма | — |
| `debug_evaluate` | Вычислить BSL-выражение | `expression` |
| `debug_status` | Полный статус сессии | — |

## Типичный workflow отладки

```
1. debug_connect       → запуск dbgs.exe + attach
2. debug_launch        → запуск 1С:Предприятие
3. debug_set_breakpoints → { file_path: "...Module.bsl", lines: [42] }
4. [пользователь работает в 1С, срабатывает breakpoint]
5. debug_get_stack     → стек вызовов
6. debug_get_variables → локальные переменные
7. debug_evaluate      → { expression: "Объект.Наименование" }
8. debug_step_over     → шаг
9. debug_continue      → продолжить
10. debug_disconnect   → остановка
```

## Сценарий: диагностика ошибки проведения

```
1. debug_connect
2. debug_launch
3. debug_set_breakpoints → ObjectModule.bsl документа, строка ОбработкаПроведения
4. В 1С: открыть документ → провести
5. Breakpoint срабатывает:
   - debug_get_stack → увидеть цепочку вызовов
   - debug_get_variables → проверить значения реквизитов
   - debug_evaluate → "Движения.ОстаткиТоваров.Количество()" — проверить записи
   - debug_step_over → пройти по логике проведения
6. Найти строку с ошибкой → исправить BSL → деплой
7. debug_disconnect
```

## Сценарий: Runtime-исключение из ТЖ

```
1. monitor-errors.ps1 → обнаружена EXCP с текстом и стеком
2. По стеку определить модуль и примерную строку
3. debug_connect → debug_launch
4. debug_set_breakpoints → на проблемную строку
5. Воспроизвести действие в 1С
6. debug_get_variables → найти некорректные данные
7. Исправить → деплой → повторить → убедиться что исключения нет
8. debug_disconnect
```

## Правила

- ВСЕГДА начинать с `debug_connect` — без него остальные инструменты не работают
- ВСЕГДА завершать `debug_disconnect` — иначе dbgs.exe останется запущенным
- Путь к BSL-файлу в `debug_set_breakpoints` — абсолютный путь к Module.bsl в `Конфигурация/`
- `debug_evaluate` работает только при остановке на breakpoint
- При зависании dbgs.exe → убить процесс вручную через `taskkill /f /im dbgs.exe`
