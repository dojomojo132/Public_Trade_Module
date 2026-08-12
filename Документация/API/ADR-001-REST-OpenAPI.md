# ADR-001: Универсальный внешний API PTM (REST + OpenAPI)

| Поле | Значение |
|------|----------|
| Статус | Accepted |
| Дата | 2026-08-12 |
| Контекст | Public Trade Module (1С 8.3.27) |
| Контракт | `Документация/API/openapi-v1.yaml` |
| Skill | `.grok/skills/1c-api-design` |

## Решение

Внешнее взаимодействие с конфигурацией PTM строится как **REST API + JSON**, контракт **OpenAPI 3** (design-first), транспорт — **HTTP-сервис** платформы.

| Выбор | Значение |
|-------|----------|
| Base path | `/hs/ptm/v1` |
| Media type | `application/json; charset=utf-8` |
| Версия | major в URI (`v1`, `v2`, …) |
| Auth v1 | заголовок `X-Api-Key` |
| Корреляция | `X-Request-Id` |
| OData (авто REST) | **не** продуктовый внешний контракт |
| GraphQL / gRPC / SOAP | только отдельным ADR |

## Мотивация

- Единая точка интеграции (касса, сайт, партнёры, сервисы) без ad-hoc URL.
- Независимость клиентов от структуры метаданных 1С.
- Эволюция через версию и OpenAPI, а не через ломку существующих клиентов.
- Существующий `ТоварыАПИ` (`/hs/api/...`) — прототип, не целевой каркас (см. review).

## Архитектура слоёв

```
Клиент
  → HTTP-сервис ПтмАпи (тонкий Module.bsl)
    → ПтмАпи (auth, JSON, ошибки, request-id)
      → ПтмАпиТовары / ПтмАпиЧеки / … (use-cases)
        → ОбщегоНазначения, документы, запросы
```

- HTTP-модуль: только маршрутный handler → вызов application → `HTTPСервисОтвет`.
- Не смешивать проведение документов и разбор URL в одном уровне.

## Ресурсы v1 (scope)

Полный каталог: `Документация/API/METHODS-v1.md`.

| Слой | Ресурсы | Роль |
|------|---------|------|
| Master | products, warehouses, cash-registers, counterparties, price-types, barcodes | справочники |
| Snapshot / core | stocks, prices, sales, cash-balances, settlements | **основная** картина учёта |
| Documents (secondary) | goods-receipts, write-offs, inventories, repricings, cash-in, cash-out, receipts | детали вне регистров |
| Service | health | probe |

### Правила выборки (зафиксировано)

1. Один list-метод на ресурс; фильтры — query (не разные URL).
2. **Период `dateFrom`+`dateTo` обязателен** для `/sales` и всех document-list; «за всё время» → 400.
3. **Max период одного запроса = 31 день**; длиннее → `400 period_too_long`, клиент бьёт на несколько запросов (сервер не авто-split).
4. Path `/{id}` — **только UUID**.
5. Документы: `detail=header|full` (list default `header`; get-by-id default `full`).
6. Регистры — primary; документы — secondary.

## Ошибки

- HTTP status отражает класс ошибки (4xx/5xx).
- Тело — единый `ErrorResponse` (`code`, `message`, `requestId`, опционально `details`).
- Не использовать «всегда 200 + success:false» в новом API.
- Клиенту не отдавать сырой `ОписаниеОшибки()` / stack.

## Безопасность

1. Публикация только по HTTPS (или доверенная внутренняя сеть + TLS на edge).
2. `X-Api-Key` обязателен на бизнес-методах.
3. Роль/права 1С для пользователя публикации + проверка ключа в коде API.
4. Лимиты: max `limit` на list; запрет full dump без пагинации/delta.
5. Аудит: request-id, метод, path, код ответа, identity (без секретов).

## Версии и legacy

| API | RootURL | Судьба |
|-----|---------|--------|
| Legacy | `api` (`ТоварыАПИ`) | freeze: не добавлять endpoints; багфиксы only |
| Target | `ptm` + templates `/v1/...` | развитие |

Миграция клиентов: dual-run → deprecation header/docs → отключение legacy.

## Последствия

**Плюсы:** предсказуемый контракт, тестируемость, SDK/docs из OpenAPI, чистые слои.

**Минусы:** нужен каркас модулей и дисциплина design-first; краткий dual-run с `ТоварыАПИ`.

## Не в scope этого ADR

- Реализация BSL-каркаса (отдельная задача).
- OAuth2 / JWT (следующий ADR при появлении user-delegated clients).
- Event/webhooks (отдельный ADR + AsyncAPI при необходимости).

## Ссылки

- Skill: `.grok/skills/1c-api-design/SKILL.md`
- OpenAPI: `Документация/API/openapi-v1.yaml`
- Review legacy: `Документация/API/review-ТоварыАПИ.md`
- Azure REST guidance: https://learn.microsoft.com/azure/architecture/best-practices/api-design
