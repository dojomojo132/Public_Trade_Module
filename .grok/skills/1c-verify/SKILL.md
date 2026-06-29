---
name: 1c-verify
description: "Verification gate after 1C BSL or config changes. Use after editing .bsl or configuration XML, before claiming task complete or deploying. Runs get_errors, optional dev_validate, reconciliation loop."
metadata:
  short-description: "Post-edit verification gate for 1C"
---

# Верификация изменений 1С

## Когда использовать

**После любого** изменения `.bsl` или XML метаданных — до сообщения «готово» или деплоя.

## Reconciliation loop

```
изменил файл → проверил → есть ошибки → исправил → проверил снова
```

Не выходи из цикла, пока критические проверки не пройдены (или пользователь явно принял риск).

## Шаг 1: BSL syntax

**onec-mcp** → `get_errors` на каждый изменённый `.bsl`.

- Есть ошибки → исправить → повторить `get_errors`
- MCP недоступен → сообщить пользователю (нужна публикация ИБ или Конфигуратор), не притворяться что проверено

## Шаг 2: XML метаданных (если менялся)

**dev-mcp** → `dev_validate`

Также проверь согласованность `Configuration.xml` / `ConfigDumpInfo.xml` при добавлении объектов.

## Шаг 3: Семантическое ревью

Прочитай diff глазами или через skill `1c-bsl-review` / `1c-anti-patterns`:

- Конструктор `Новый`
- Директивы и области
- Клиент-сервер
- Запросы и транзакции

## Шаг 4: Контекст (если менялся объект метаданных)

После правок в `Конфигурация/` hook обновит граф; при необходимости:

```
dev-mcp → dev_sync_obsidian
```

## Шаг 5: Отчёт

```markdown
## Верификация

| Проверка | Результат |
|----------|-----------|
| get_errors | 0 ошибок / N ошибок (список) |
| dev_validate | OK / FAIL |
| anti-patterns | OK / замечания |

Готово к деплою: да / нет
```

## Запрещено

- Завершать задачу с BSL без `get_errors`
- Деплоить при критических замечаниях ревью без согласия пользователя