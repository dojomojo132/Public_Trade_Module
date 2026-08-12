# PTM External API

| Артефакт | Назначение |
|----------|------------|
| [ADR-001-REST-OpenAPI.md](./ADR-001-REST-OpenAPI.md) | Решение: REST + OpenAPI + слои |
| [METHODS-v1.md](./METHODS-v1.md) | **Каталог методов и фильтров (согласование)** |
| [openapi-v1.yaml](./openapi-v1.yaml) | Контракт v1 (source of truth после freeze) |
| [review-ТоварыАПИ.md](./review-ТоварыАПИ.md) | Разбор legacy `/hs/api` |

Skill агента: `.grok/skills/1c-api-design` (`/1c-api-design`).

**Статус:** OpenAPI v1 **frozen**. Реализация — **расширение `PTM_API`** (`Конфигурация_PTM_API/`).

| | |
|--|--|
| Base URL | `http://localhost/PTM_Clean/hs/ptm/v1` |
| HTTP-сервис | `Апи_Внешний` (RootURL `ptm`) |
| Auth | `X-Api-Key` = константа `Апи_Ключ` (пусто = DEV, auth off) |
| Модули | `Апи_Транспорт`, `Апи_Регистры`, `Апи_Справочники` |
| Deploy | `python scripts/deploy_ext.py --ext PTM_API --action Full` |

Реализовано: health, products, warehouses, cash-registers, counterparties, price-types, barcodes, prices, stocks, sales, cash-balances, settlements.  
Документы: URL есть, `501 not_implemented`.

**Не в основной конф** — только расширение.
