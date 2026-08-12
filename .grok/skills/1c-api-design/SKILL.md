---
name: 1c-api-design
description: "Design and implement external REST API for 1C:Enterprise PTM. Use when building HTTP services, OpenAPI contracts, universal API, versioning, auth, external integration endpoints, or reviewing ТоварыАПИ. Slash: /1c-api-design"
metadata:
  short-description: "1C REST API design (OpenAPI-first)"
---

# 1C API Design (PTM)

## Когда

Проектирование или правка **внешнего** API конфигурации: HTTP-сервисы, OpenAPI, auth, ошибки, версия, интеграция с кассой/сайтом/партнёром.

Авторитетные артефакты:

| Что | Путь |
|-----|------|
| ADR | `Документация/API/ADR-001-REST-OpenAPI.md` |
| Методы/фильтры | `Документация/API/METHODS-v1.md` |
| Контракт | `Документация/API/openapi-v1.yaml` |
| Реализация | **расширение** `Конфигурация_PTM_API/` (`PTM_API`), не основная конф |
| Ревью legacy | `Документация/API/review-ТоварыАПИ.md` |

**Имена в расширении (префикс `Апи_`):** HTTP `Апи_Внешний`, ОМ `Апи_Транспорт` / `Апи_Регистры` / `Апи_Справочники`, константа `Апи_Ключ`.  
Deploy: `python scripts/deploy_ext.py --ext PTM_API --action Full` (или dev-mcp `dev_ext`).

**List-паттерн:** один `GET /{resource}`; ширина — query-фильтры. Пагинация `limit`/`offset`.

**Обязательный период** (`dateFrom`+`dateTo`) для `/sales` и document-list; без периода → 400. **Max 31 день** на запрос; длиннее → 400, клиент делает несколько запросов. Срезы остатков/цен — `onDate`.

**id path** = UUID only. Документы: `detail=header|full`. **Регистры primary**, документы secondary. См. `METHODS-v1.md`.

## Порядок работы (обязательный)

1. **Контракт first** — правка `openapi-v1.yaml` (или новый `openapi-vN.yaml`).
2. **ADR** — если меняется стиль, auth, версия, envelope ошибок.
3. **Слои BSL** (ниже) — код только после контракта.
4. **`1c-bsl-coding`** → **`1c-verify`**.

Не начинать с URL-шаблонов в XML «как получится».

## Стиль по умолчанию (PTM)

| Решение | Значение |
|---------|----------|
| Протокол | REST + JSON (`application/json; charset=utf-8`) |
| Транспорт 1С | HTTP-сервис (`/hs/...`), не OData как продуктовый API |
| Версия | URI: `/hs/ptm/v1/...` |
| Design | OpenAPI 3.x — source of truth |
| Auth (v1) | API Key в заголовке `X-Api-Key` (server-to-server); позже JWT |
| Ошибки | Единый envelope (см. OpenAPI `ErrorResponse`) |
| Корреляция | `X-Request-Id` (принять или сгенерировать; вернуть в ответе) |

Не выбирать GraphQL/gRPC/SOAP для базового внешнего API без отдельного ADR.

## Ресурсы vs RPC

- **Ресурс (CRUD):** существительные plural — `/products`, `/receipts/{id}`
- **Действие (не CRUD):** subordinate action — `POST /receipts` (create), `POST /receipts/{id}/fiscalize`
- Запрещены глаголы в корне: `/search`, `/sync`, `/check` — legacy only

## Слои в 1С

```
HTTP-сервис (Module.bsl)
  → только: метод, path/query, headers, тело → HTTPСервисОтвет
ОбщийМодуль.ПтмАпи (транспорт/адаптер)
  → auth, request-id, parse JSON, map status, serialize
ОбщийМодуль.ПтмАпи* (application)
  → use-case: поиск товара, приём чека, sync slice
Существующие модули / документы / запросы
  → домен (не знать HTTP)
```

Правила:

- В модуле HTTP-сервиса **нет** запросов к БД, проведения документов, бизнес-правил.
- Сериализация DTO — в адаптере; домен отдаёт структуры/ссылки, не «сырой» JSON string ad-hoc.
- Один формат ошибки для всех endpoint’ов.
- Транзакция — только в application/domain на запись.

## HTTP-конвенции

| Метод | Смысл | Успех |
|-------|--------|--------|
| GET | Чтение, идемпотентно | 200 / 404 |
| POST | Создание / действие | 201 (+ Location) или 200 (action) / 202 (async) |
| PUT | Полная замена | 200 / 204 |
| PATCH | Частичное | 200 |
| DELETE | Удаление | 204 / 404 |

Query: `limit` (cap), `offset` или cursor, фильтры явно именованные.  
Не отдавать «все товары» без пагинации на публичном API.

## Безопасность (минимум v1)

- HTTPS на публикации
- `X-Api-Key` обязателен на всех путях кроме health (если будет)
- Не логировать ключи и полные тела с ПДн
- Права: отдельная роль «ВнешнийAPI» / scopes в контракте
- Валидация схемы тела до use-case

## Версионирование

- Breaking change → `v2` (новый RootURL или префикс)
- Additive (новое поле JSON, новый optional query) — в той же major, если клиенты игнорируют unknown fields
- Legacy `ТоварыАПИ` (`RootURL=api`) — не расширять; миграция в `ptm/v1`

## Чеклист перед merge endpoint’а

- [ ] Path/method/схемы есть в OpenAPI
- [ ] Auth и error envelope совпадают с ADR
- [ ] HTTP-модуль тонкий; логика в общих модулях
- [ ] Нет query-in-loop / mirror таблиц 1С наружу
- [ ] Пагинация на list; лимит max
- [ ] `X-Request-Id` в ответе
- [ ] `1c-verify` / `get_errors` чисто

## Анти-паттерны (блок)

| Антипаттерн | Делать так |
|-------------|------------|
| Вся логика в HTTP Module.bsl | Слои adapter + application |
| Глаголы URL `/search`, `/check` | `/products?code=`, `POST /receipts` |
| `success: true/false` + 200 на бизнес-ошибке | HTTP status + `ErrorResponse` |
| Отдать весь каталог без limit | Пагинация / delta sync |
| `ОписаниеОшибки()` клиенту as-is | Код ошибки + безопасное message |
| Auth только Basic публикации | + API Key / JWT на уровне API |
| OData = публичный контракт | Отдельный HTTP-сервис + OpenAPI |

## Связанные skills

- Код BSL: `1c-bsl-coding`
- Ревью: `1c-bsl-review`, `1c-anti-patterns`
- Проверка: `1c-verify`
- Сессия/MCP: `1c-workflow`
