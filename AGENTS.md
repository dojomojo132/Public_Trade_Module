# Public Trade Module — правила для AI-агентов (1С:Предприятие 8.3.27)

> **Проект:** PTM | **Платформа:** 8.3.27 | **Git root:** `D:\Git\Public_Trade_Module`

## Роль

Senior 1C Developer. Пиши BSL по стандартам платформы и проекта. Не выдумывай API — проверяй через MCP и исходники.

## Пути (не путать)

| Что | Путь |
|-----|------|
| Корень проекта | `D:\Git\Public_Trade_Module` |
| Файловая ИБ | `D:\Confiq\Public Trade Module` |
| Публикация Apache | `D:\Apache\Module_Torgovly_DEV` → URL `/PTM_Clean` |
| HTTP MCP | `http://localhost/PTM_Clean/hs/mcp/mcp` |
| Выгрузка конфигурации | `Конфигурация/` |
| Расширение MCP | `MCP_Extension/` |
| Obsidian vault | `D:\Git\ObsidianVaults\Public_Trade_Module` |
| Регламент DevHub | `D:\Git\DevHub\docs\1c-reglament.md` |

## Старт сессии

```powershell
Set-Location D:\Git\Public_Trade_Module
.\.venv\Scripts\python.exe scripts\project_bootstrap.py
```

Перед работой с объектами 1С — свежий `graph_index.json` (bootstrap делает сам при необходимости).

## MCP — отдельная настройка на каждый проект 1С

MCP **не переиспользуются** между проектами. Для каждого репозитория:

1. Скрипты MCP лежат в `scripts/` **этого** проекта (`dev_mcp_server.py`, `context_mcp_server.py`, …).
2. Параметры — в `.github/project-config.yml` (секция `mcp.*`) и `config.json` (vault, пути конфигураций).
3. Генерация конфигов IDE: `python scripts/_generate_mcp.py` → `.mcp.json`, `.cursor/mcp.json`, `.grok/config.toml`.
4. Для PTM: HTTP onec-mcp → `http://localhost/PTM_Clean/hs/mcp/mcp`, ИБ → `D:\Confiq\Public Trade Module`.

Не подключать MCP-серверы из AdminReport или других проектов — только копировать фреймворк и заполнить `project-config.yml`.

## MCP — что уже есть (использовать, не дублировать терминалом)

| MCP | Когда |
|-----|-------|
| **context-mcp** | Контекст по объектам: `resolve`, `get`, `moc` |
| **dev-mcp** | backup, dump, validate, deploy, sync_obsidian |
| **onec-mcp** | Живая ИБ: запросы, метаданные, `get_errors` |
| **ptm-debug** | Пошаговая отладка BSL |
| **onec-configurator** | UI Конфигуратора (окно должно быть открыто) |
| **tg-dashboard** | Задачи vault / Telegram |
| ~~obsidian-vault~~ | **Не используется** — vault через `dev_sync_obsidian` + файлы |

**Поиск по коду:** context-mcp → grep в MCP → только потом `Grep` по файлам.

**Деплой/бэкап:** только через dev-mcp. Терминал для рутинных операций — запрещён.

## Агенты (Copilot)

| Этап | Агент |
|------|-------|
| План задачи | `planner` |
| BSL-код | `1c-coder` |
| XML метаданных | `1c-xml-editor` |
| Формы (BSL) | `1c-form-builder` |
| Закрытие, деплой | `closer` |
| Анализ сессий | `session-analyst` |

Архив: `orchestrator`, `1c-architect`, `1c-deployer` → `.github/agents/archive/`.  
Карта vault: `.github/VAULT_STRUCTURE.md`. Регламент: `.github/copilot-instructions.md` §7.1.

## Скиллы — обязательная маршрутизация

Grok: `.grok/skills/`. Copilot/Cursor: `.github/skills/`.

| Задача | Скилл |
|--------|-------|
| Любая правка `.bsl` | `1c-bsl-coding` → затем `1c-verify` |
| Внешний REST API / OpenAPI / HTTP-сервис | `1c-api-design` → `1c-bsl-coding` → `1c-verify` |
| Ревью / pre-deploy | `1c-bsl-review` |
| Антипаттерны | `1c-anti-patterns` |
| Деплой, мониторинг | `dev-mcp` + агент `closer` |
| XML метаданных | `1c-xml-editor` |
| Формы | `1c-form-generator` |
| Отладка | `1c-debug` |
| Отчёты СКД | `1c-report` |
| Старт, MCP, bootstrap | `1c-workflow` |

## Конфиги агента

| Файл | Назначение |
|------|------------|
| `.grok/config.toml` | Grok MCP + skills paths |
| `.github/project-config.yml` | ИБ, пути, флаги MCP |
| `config.json` | Vault, graph_index (context-mcp) |

После правок MCP: `python scripts\_generate_mcp.py` и перезапуск сессии.