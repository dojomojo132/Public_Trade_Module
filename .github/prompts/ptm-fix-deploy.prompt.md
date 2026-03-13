---
description: "Цикл исправления ошибок после неудачного деплоя 1С конфигурации PTM. Разбор логов, фикс XML/BSL, повторный деплой, откат при необходимости."
agent: "1c-deployer"
tools: [read, search, edit, execute]
argument-hint: "Вставь текст ошибки деплоя или опиши проблему"
---

Исправь ошибки деплоя конфигурации PTM.

## Процедура

### 1. Найти и разобрать ошибки

В выводе деплоя найти блок `=== ОШИБКИ (для Copilot Agent) ===` и прочитать ВСЕ секции:
- `--- ОШИБКИ ---`
- `--- ПОЛНЫЙ ЛОГ 1С ---`
- `--- STDOUT ---`
- `--- STDERR ---`

### 2. Классифицировать ошибки

| Код | Причина | Действие |
|-----|---------|----------|
| `[ДИАЛОГ ЗАБЛОКИРОВАН]` | Критическая ошибка XML | `validate-config.ps1`, исправить ВСЕ |
| `EXIT_CODE: -2` | Таймаут | ОТКАТИТЬ немедленно |
| `EXIT_CODE: 1` | Общая ошибка | Читать ПОЛНЫЙ ЛОГ |
| `{Модуль(строка)}:` | Ошибка BSL | Исправить BSL |

### 3. Исправить

- Исправить XML/BSL файлы
- Вызвать `get_errors` на изменённые файлы

### 4. Повторить деплой

```powershell
$script = Get-ChildItem -Path "D:\Git\Public_Trade_Module" -Recurse -Filter "deploy-config.ps1" | Select-Object -First 1
powershell -ExecutionPolicy Bypass -File $script.FullName -Action Full -SkipDtBackup -SkipCheck
```

### 5. Правило 2 попыток

Если ошибки не решаются за 2 попытки — ОТКАТИТЬ:
```powershell
powershell -ExecutionPolicy Bypass -File $script.FullName -Action Rollback
```
Затем исправить корневую причину и попробовать заново.
