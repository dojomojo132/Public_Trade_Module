# PTM v2 — План миграции (УТВЕРЖДЁН)

**Дата утверждения:** 18 мая 2026 г.
**Статус:** утверждён, готов к реализации

---

## Итоговый стек

### Бэкенд
Rust 1.86 + Axum 0.7 + SQLx 0.8 + Tokio + PostgreSQL 16 + JWT + rust_decimal + tracing

### Фронтенд
SvelteKit 2 + Svelte 5 + Tailwind CSS 4 + Vite + PWA + IndexedDB + BarcodeDetector API + TypeScript

### Инфраструктура
Docker + Prometheus/Grafana + plugins.toml

---

## Архитектура: 3 сервиса

| Сервис | Объём (Rust) | Ответственность |
|---|---|---|
| **ptm-core** | ~18 000 строк | POS-ядро: товары, продажи, остатки, смены, цены, проведение 7 документов через EventBus |
| **ptm-fiscal-service** | ~3 000 строк | Фискализация: разбиение по ФОП, отправка в ПРРО, хранение чеков, очередь повторов |
| **MCP Extension** | ~2 000 строк | Copilot-интеграция |

**Фронтенд:** ~3 500 строк Svelte/TS (один PWA на три роли: кассир, админ, бухгалтер)

---

## Оценки

| Параметр | Значение |
|---|---|
| Строк Rust | ~23 000 |
| Строк Svelte/TS | ~3 500 |
| Срок (1 агент) | 10-14 недель |
| Срок (4 агента) | 5-7 недель |
| RAM (все сервисы) | 20-50 MB |
| Размер бинарников | ~30 MB суммарно |
| Лицензии | $0 |

---

## План реализации (8 шагов)

1. **Схема БД** — готово (`migrations/001_core_schema.sql`)
2. **Cargo workspace + ptm-core** — модели, Plugin trait, EventBus
3. **ptm-server** — сборка, конфигурация, запуск
4. **MCP Extension** — первый плагин, инструмент для агента
5. **Бизнес-логика ptm-core** — 7 документов, смены, цены, поиск
6. **PTM-Fiscal-Service** — отдельный сервис фискализации
7. **Оборудование** — сканер, принтер, эмулятор
8. **Миграция данных** — Strangler Fig: 1С → PostgreSQL

---

## Файлы проекта

- `Документация/ПЛАН_МИГРАЦИИ_PTM_Rust_v3.md` — полный план
- `ptm-workspace/` — Cargo workspace
- `ptm-workspace/crates/ptm-core/` — ядро (модели, plugin, events, error)
- `ptm-workspace/migrations/001_core_schema.sql` — схема БД
- `pos-benchmark/` — бенчмарк Rust vs Go
