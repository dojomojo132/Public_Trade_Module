# PTM API v1 — каталог методов (read)

| Поле | Значение |
|------|----------|
| Статус | **Frozen** (согласовано) |
| Base | `/hs/ptm/v1` |
| Контракт | `openapi-v1.yaml` (**source of truth**) |
| Принцип | **Один list-метод на ресурс**; ширина выборки — **query-фильтры**, не разные URL |

## 0. Зафиксированные решения

| # | Решение |
|---|---------|
| 1 | **Период обязателен** для оборотов/журналов (продажи, закупки/приходы, чеки и прочие document-list). Запрос «за всё время» → **`400`**, без выполнения. |
| 2 | Период = `dateFrom` + `dateTo` (один день или несколько). |
| 3 | **`{id}` в path = только UUID** (не code/number). |
| 4 | Документы: **один list-метод**; полнота — параметр **`detail=header\|full`**. |
| 5 | **Основной источник картины учёта — регистры.** Документы — **запасной** канал за деталями, которых нет в регистрах. |
| 6 | Справочники / срезы остатков / штрихкоды / актуальные цены — без обязательного периода (см. §2). |

---

## 1. Общий принцип

### 1.1. Один endpoint на коллекцию

```
GET /{resource}?filter…&limit=&offset=
```

| Запрос | Смысл |
|--------|--------|
| `GET /products` | широкая выборка (с пагинацией) |
| `GET /products?groupId=…` | та же операция + отбор |

**Запрещено:** `/products/all`, `/products/by-group`, `/products/search`.

### 1.2. Фильтры

- Query, опциональные **кроме** обязательного периода там, где он требуется (§2).
- Несколько параметров = **AND**.
- Неизвестный параметр → `400`.

### 1.3. Пагинация (все list)

| Параметр | Default | Max |
|----------|---------|-----|
| `limit` | 100 | 1000 |
| `offset` | 0 | — |

### 1.4. Идентификатор

- Path: `GET /{resource}/{id}` — **только UUID**.
- В фильтрах: `*Id` = UUID; дополнительно `*Code` где удобно (склад, товар, касса).

### 1.5. Оболочка list

```json
{
  "items": [],
  "count": 50,
  "limit": 100,
  "offset": 0,
  "total": 1234
}
```

### 1.6. Период: лимит 31 день

| Правило | Значение |
|---------|----------|
| Max длина одного запроса | **31 календарный день** включительно (`dateTo - dateFrom + 1 ≤ 31` для date-only; для date-time — не более 31×24h) |
| Длиннее 31 дня | **не обслуживаем одним запросом** → `400` `period_too_long` |
| Как получить больше | **клиент режет** на несколько запросов по ≤31 дню (сервер сам не склеивает и не разбивает) |

Примеры:

```http
# OK: 12 дней
GET /sales?dateFrom=2026-08-01&dateTo=2026-08-12

# OK: ровно 31 день
GET /sales?dateFrom=2026-08-01&dateTo=2026-08-31

# 400 period_too_long — клиент делает 2+ запроса
GET /sales?dateFrom=2026-07-01&dateTo=2026-08-31
→ GET … dateFrom=2026-07-01&dateTo=2026-07-31
→ GET … dateFrom=2026-08-01&dateTo=2026-08-31
```

### 1.7. Ошибки периода

| Ситуация | HTTP | code |
|----------|------|------|
| Нет `dateFrom` или `dateTo` (где период обязателен) | 400 | `period_required` |
| `dateFrom` > `dateTo` | 400 | `period_invalid` |
| Длина периода > 31 день | 400 | `period_too_long` |

---

## 2. Обязательный период (anti «за всё время»)

### 2.1. Где период **обязателен** (`dateFrom` + `dateTo`)

| Path | Почему |
|------|--------|
| `GET /sales` | обороты продаж — объём |
| `GET /goods-receipts` | журнал приходов / закупок |
| `GET /write-offs` | журнал списаний |
| `GET /inventories` | журнал инвентаризаций |
| `GET /repricings` | журнал переоценок |
| `GET /cash-in` | журнал ПКО |
| `GET /cash-out` | журнал РКО |
| `GET /receipts` | журнал чеков |
| `GET /prices` в режиме **history** | если переданы оба `dateFrom`/`dateTo` — ок; см. §4.2 |

Без периода → **не выбирать данные**, сразу `400`.

### 2.2. Где период **не** обязателен

| Path | Вместо периода |
|------|----------------|
| Справочники | фильтры + пагинация |
| `GET /barcodes` | фильтры + пагинация |
| `GET /prices` (режим **slice**) | `onDate` (default = сейчас) |
| `GET /stocks` | `onDate` (default = сейчас) — срез остатков |
| `GET /cash-balances` | `onDate` |
| `GET /settlements` | `onDate` |
| `GET /…/{id}` | один объект по UUID |

---

## 3. Приоритет данных

```
Регистры (stocks, sales, prices, cash-balances, settlements, barcodes)
  = основной способ получить актуальную / оборотную картину

Документы (goods-receipts, receipts, …)
  = запасной канал: доп. реквизиты, ТЧ, то, чего нет в регистрах
```

Реализацию и нагрузку оптимизировать **сначала под регистры**.  
Документные endpoint’ы — полноценные, но вторичны по сценариям.

---

## 4. Справочники

Полный item в list и в `GET /{id}`.

### 4.1. `products` ← Номенклатура

| Method | Path |
|--------|------|
| GET | `/products` |
| GET | `/products/{id}` |

**Фильтры list:** `id`, `code`, `article`, `barcode`, `name`, `groupId`, `isFolder`, `deletionMark` (default false), `requiresExciseStamp`.

### 4.2. `warehouses` ← Склады

GET `/warehouses` · GET `/warehouses/{id}`  
**Фильтры:** `id`, `code`, `name`, `deletionMark`.

### 4.3. `cash-registers` ← Кассы

GET `/cash-registers` · GET `/cash-registers/{id}`  
**Фильтры:** `id`, `code`, `name`, `deletionMark`.

### 4.4. `counterparties` ← Контрагенты

GET `/counterparties` · GET `/counterparties/{id}`  
**Фильтры:** `id`, `code`, `name`, `groupId`, `isFolder`, `deletionMark`.

### 4.5. `price-types` ← ТипыЦен

GET `/price-types` · GET `/price-types/{id}`  
**Фильтры:** `id`, `code`, `name`, `deletionMark`.

---

## 5. Регистры сведений

### 5.1. `barcodes` ← Штрихкоды

GET `/barcodes`  
**Фильтры:** `barcode`, `productId`, `productCode`.  
**Item:** barcode, productId, productCode, productName.

### 5.2. `prices` ← ЦеныНоменклатуры

GET `/prices` — **один метод, два режима**:

| Режим | Как включить | Период |
|-------|----------------|--------|
| **slice** (актуальные) | нет `dateFrom`/`dateTo`; опц. `onDate` | не обязателен |
| **history** | заданы **оба** `dateFrom` и `dateTo` | обязателен (оба) |

**Фильтры:** `productId`/`productCode`, `priceTypeId`/`priceTypeCode`, `onDate`, `dateFrom`/`dateTo`, `recorderId`.

**Item:** product*, priceType*, price, period, recorderId.

---

## 6. Регистры накопления (основа картины)

### 6.1. `stocks` ← ОстаткиТоваров

GET `/stocks`  
**Фильтры:** `warehouseId`/`warehouseCode`, `productId`/`productCode`, `onDate`, `onlyNonZero` (default true).  
**Item:** warehouse*, product*, quantity, onDate.

### 6.2. `sales` ← Продажи

GET `/sales`  
**Обязательно:** `dateFrom`, `dateTo`.  
**Фильтры:** `productId`/`productCode`, `cashRegisterId`/`cashRegisterCode`, `shiftId`, `employeeId`.  
**Item:** product*, cashRegister*, shiftId, employeeId, quantity, amount, cost (+ период/день агрегации).

### 6.3. `cash-balances` ← ДенежныеСредства

GET `/cash-balances`  
**Фильтры:** `cashRegisterId`/`cashRegisterCode`, `onDate`, `onlyNonZero`.  
**Item:** cashRegister*, amount, onDate.

### 6.4. `settlements` ← Взаиморасчеты

GET `/settlements`  
**Фильтры:** `counterpartyId`/`counterpartyCode`, `documentId`, `onDate`, `onlyNonZero`.  
**Item:** counterparty*, documentId, amount, onDate.

---

## 7. Документы (вторичный канал)

### 7.1. Шаблон

| Method | Path | Назначение |
|--------|------|------------|
| GET | `/{docs}` | журнал с **обязательным периодом** |
| GET | `/{docs}/{id}` | один документ по **UUID** |

**Обязательные query на list:** `dateFrom`, `dateTo`.

**Общие фильтры:** `id`, `number`, `posted`, `deletionMark` + поля шапки вида.

### 7.2. Полнота: параметр `detail` (не два URL)

| `detail` | Где | Содержимое item |
|----------|-----|-----------------|
| `header` | **default для list** | только шапка |
| `full` | list по запросу; **default для GET by id** | шапка + все ТЧ |

```http
GET /goods-receipts?dateFrom=…&dateTo=…&detail=header
GET /goods-receipts?dateFrom=…&dateTo=…&detail=full
GET /goods-receipts/{uuid}                 → full
GET /goods-receipts/{uuid}?detail=header  → только шапка
```

Так сохраняется правило «один list-метод»; глубина — query.

### 7.3. Ресурсы

| Path | 1С | Доп. фильтры list |
|------|-----|-------------------|
| `/goods-receipts` | ПриходТовара | warehouse*, counterparty* |
| `/write-offs` | СписаниеТовара | warehouse* |
| `/inventories` | ИнвентаризацияТоваров | warehouse* |
| `/repricings` | Переоценка | priceType* |
| `/cash-in` | ПКО | cashRegister*, counterparty* |
| `/cash-out` | РКО | cashRegister*, counterparty* |
| `/receipts` | ЧекККМ | cashRegister*, warehouse*, shiftId, status |

**Write:** `POST /receipts` — вне read-спеки; обсуждается отдельно.

---

## 8. Служебное

GET `/health` — без auth, без периода.

---

## 9. Сводка

| Приоритет | Path | Период | id path |
|-----------|------|--------|---------|
| service | `/health` | — | — |
| master | `/products`, `/warehouses`, `/cash-registers`, `/counterparties`, `/price-types` | нет | UUID |
| master/РС | `/barcodes` | нет | — |
| snapshot | `/prices` (slice), `/stocks`, `/cash-balances`, `/settlements` | `onDate` опц. | — |
| **core** | `/sales` | **обязателен** | — |
| **core** | `/prices` (history) | **обязателен** | — |
| secondary | все document list | **обязателен** | UUID + `detail` |

---

## 10. Примеры

```http
# Регистр — основа
GET /sales?dateFrom=2026-08-01T00:00:00&dateTo=2026-08-12T23:59:59
GET /sales?dateFrom=2026-08-12&dateTo=2026-08-12&cashRegisterId={uuid}
GET /stocks?warehouseId={uuid}
GET /stocks?productId={uuid}&warehouseId={uuid}

# Без периода — отказ
GET /sales
→ 400 period_required

GET /goods-receipts
→ 400 period_required

# Документ — запасной канал
GET /goods-receipts?dateFrom=2026-08-01&dateTo=2026-08-12&detail=header
GET /goods-receipts?dateFrom=2026-08-01&dateTo=2026-08-12&detail=full
GET /goods-receipts/550e8400-e29b-41d4-a716-446655440000
```

---

## 11. Зафиксировано / ещё open

| Тема | Статус |
|------|--------|
| Max период **31 день**; длиннее → несколько запросов клиента | **зафиксировано** |
| Формат дат: ISO-8601; date-only = сутки целиком | зафиксировано (дефолт) |
| `total` в list | отдавать; если дорого — later `null` |
| `POST /receipts` | после freeze read |

---

## 12. Next

1. ~~Перенести METHODS → openapi-v1.yaml~~ **done**  
2. ~~Каркас BSL (HTTP + auth/period/errors + регистры + справочники)~~ **done**  
3. Документы (secondary, `detail=header|full`)  
4. Deploy + smoke HTTP tests
