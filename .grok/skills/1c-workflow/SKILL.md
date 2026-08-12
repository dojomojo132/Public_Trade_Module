---
name: 1c-workflow
description: "PTM 1C development workflow: bootstrap, MCP matrix, paths, context search, deploy routing. Use at session start, when choosing tools, or when unsure which MCP or skill to use for a 1C task."
metadata:
  short-description: "PTM 1C session workflow"
---

# Workflow PTM (1С)

## Старт

```powershell
Set-Location D:\Git\Public_Trade_Module
.\.venv\Scripts\python.exe scripts\project_bootstrap.py
```

## MCP по задаче

| Задача | MCP |
|--------|-----|
| Понять объект, зависимости | context-mcp |
| Dump / backup / deploy | dev-mcp |
| Запрос к ИБ, get_errors | onec-mcp |
| Отладка | ptm-debug |
| Окно Конфигуратора | onec-configurator |
| Obsidian REST | obsidian-vault |

Полный регламент: `D:\Git\DevHub\docs\1c-reglament.md`

## Поиск кода (MCP-first)

1. context-mcp `resolve` / `get` / `moc`
2. onec-mcp code-metadata / grep (если доступен)
3. Только потом `Grep` по `Конфигурация/`

## Маршрутизация агентов (Copilot)

| Этап | Агент |
|------|-------|
| План | `planner` |
| BSL | `1c-coder` |
| XML | `1c-xml-editor` |
| Формы BSL | `1c-form-builder` |
| Закрытие | `closer` |

Карта vault: `.github/VAULT_STRUCTURE.md`. Регламент: `.github/copilot-instructions.md` §7.1.

## Маршрутизация скиллов

| Тип работы | Скилл |
|------------|-------|
| BSL код | `1c-bsl-coding` → `1c-verify` |
| Внешний REST API / OpenAPI / HTTP-сервис | `1c-api-design` → `1c-bsl-coding` → `1c-verify` |
| Ревью | `1c-bsl-review` |
| Деплой | `dev-mcp` + агент `closer` |
| XML объекта | `1c-xml-editor` |
| Форма | `1c-form-generator` |
| СКД отчёт | `1c-report` |
| Отладка | `1c-debug` |
| Метаданные целостность | `1c-metadata-check` |

## Пути

- ИБ: `D:\Confiq\Public Trade Module`
- Apache: `D:\Apache\Module_Torgovly_DEV` (base `/PTM_Clean` в default.vrd)
- HTTP onec-mcp: `http://localhost/PTM_Clean/hs/mcp/mcp`
- Конфиг: `.github/project-config.yml`
- Расширения: `MCP_Extension/`, `Конфигурация_PTM_Analytics/`

## Troubleshooting MCP

```powershell
python scripts\_generate_mcp.py
grok mcp doctor onec-mcp
```

Имена: `onec-mcp`, `onec-configurator` (не `1c-mcp`). Config: `.grok/config.toml`. После правок — перезапуск сессии.