# PTM External API

| Артефакт | Назначение |
|----------|------------|
| [ADR-001-REST-OpenAPI.md](./ADR-001-REST-OpenAPI.md) | Решение: REST + OpenAPI + слои |
| [METHODS-v1.md](./METHODS-v1.md) | **Каталог методов и фильтров (согласование)** |
| [openapi-v1.yaml](./openapi-v1.yaml) | Контракт v1 (source of truth после freeze) |
| [review-ТоварыАПИ.md](./review-ТоварыАПИ.md) | Разбор legacy `/hs/api` |

Skill агента: `.grok/skills/1c-api-design` (`/1c-api-design`).

**Статус:** OpenAPI v1 **frozen** (`openapi-v1.yaml`).

Порядок реализации: каркас → регистры → документы. Skills: `1c-api-design` → `1c-bsl-coding` → `1c-verify`.
