# План миграции PTM на Rust + Web

**Дата:** 18 мая 2026 г.
**Конфигурация:** ТорговляРозница (Public Trade Module)
**Целевой стек:** Rust (Axum + SQLx + Tokio) + PostgreSQL + Svelte (PWA)

## Шаг 0: Границы

### Мигрируем: ~50 000 строк BSL -> ~30 000 строк Rust

Основная конфигурация (35 228 строк): 12 документов, 5 регистров накопления, 7 регистров сведений, ~22 справочника, HTTP API, обработки.
Расширения (14 500 строк): MCP_Extension, PTM_Analytics, PTM_Fiscal, PTM_Driver_Emulator.

### НЕ мигрируем: БПО (76 078 строк), демо, орфан-файлы.

Оборудование подключается напрямую: сканер serial/HID, принтер ESC/POS, фискализация HTTP API ПРРО.

### Стек: Rust (Axum + SQLx + Tokio) + PostgreSQL 16 + Svelte PWA + JWT

### Принципы: Strangler Fig, Read-first, Plugin = Cargo crate, EventBus, материализованные остатки (O(1)), ценность после каждой фазы.

## Шаг 1: Схема БД (18 таблиц)

Справочники, документы (documents + document_lines + document_payments), движения по регистрам, материализованные остатки (stock_balances), кассовые смены.
Файл: ptm-workspace/migrations/001_core_schema.sql

## Шаг 2: Cargo workspace + ptm-core

500 строк Rust, 1-2 дня. Модели, Plugin trait, EventBus, ошибки.

## Шаг 3: ptm-server

300 строк Rust, 1 день. main.rs, конфигурация, health check.

## Шаг 4: MCP Extension

3 000 строк Rust, 3-5 дней. MCP-сервер для Copilot.

## Шаг 5: Бизнес-логика

20 000 строк Rust, 4-6 недель. Проведение 9 типов документов, контроль остатков, поиск товаров, смены, цены.

## Шаг 6: Оборудование

800 строк Rust, 3-5 дней. Сканер, принтер, эмулятор.

## Шаг 7: Фискализация

1 000 строк Rust, 1-2 недели. FiscalProvider + ПРРО через EventBus.

## Шаг 8: Миграция данных

Фаза 1: Svelte -> 1С API (1 неделя)
Фаза 2: Rust read-only + ETL (3 недели)
Фаза 3: переключение write -> Rust (1 неделя)

## Итог: 10-14 недель (1 агент), 5-8 недель (4-5 агентов)

Строк Rust: ~30 000. RAM: 10-30 MB. Бинарник: ~15 MB. Лицензии: $0.
