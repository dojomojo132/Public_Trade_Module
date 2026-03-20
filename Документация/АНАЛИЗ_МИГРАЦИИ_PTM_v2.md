# Уточнённый анализ миграции PTM: без БПО, с AI-агентом, Rust-бэкенд

**Дата:** 19 марта 2026 г.  
**Конфигурация:** ТорговляРозница (PTM)  
**Уточнения:** БПО не используется (кроме сканера/принтера). ПРРО пишется отдельно. Разработка через AI-агента.

---

## 1. Реальный объём кода к миграции (без БПО и фискала)

| Категория | Файлов | Строк BSL | % от всего | Мигрировать? |
|-----------|--------|-----------|-----------|-------------|
| **БПО (оборудование)** | 224 | 106 718 | **87%** | ❌ Не нужно |
| **Фискал (ККТ/ОФД)** | 20 | 2 099 | **2%** | ❌ Пишется отдельно |
| **ЯДРО (бизнес-логика)** | 85 | **13 567** | **11%** | ✅ Мигрируется |

**87% кода — БПО, который выбрасывается.**

### Детализация ядра

| Блок | Файлов | Строк | Что внутри |
|------|--------|-------|-----------|
| Документы | 17 | 2 890 | ПриходТовара, СписаниеТовара, Переоценка, Инвентаризация, ПКО/РКО, КассоваяСмена, ВозвратТовара + формы |
| Обработки | 15 | 4 726 | Импорт/экспорт, загрузка цен, тестовое заполнение, панель администрирования |
| Справочники | 16 | 2 137 | Номенклатура, Контрагенты, РабочиеМеста, ШаблоныМагнитныхКарт |
| Общие модули | 10 | 1 913 | ОбщегоНазначения, НастройкиПоУмолчанию, КассовыеСмены, ГенерацияШтрихкода |
| HTTP API | 1 | 692 | ТоварыАПИ (поиск, синхронизация, приём чеков) |
| Регистры сведений | 6 | 406 | ПлатежныеОперации, ЗначенияЕМРЦ |
| Прочее | 20 | 803 | Перечисления, WebService, модули приложения, команды |

---

## 2. Анализ бизнес-логики (Hot Path vs Cold Path)

### 🔥 Hot Path (критичная производительность)

| Функция | Откуда | Что делает | Регистры |
|---------|--------|-----------|----------|
| **ВыполнитьКонтрольОстатков()** | СписаниеТовара | Свёртка ТЧ по номенклатуре → запрос остатков → блокировка при дефиците | ОстаткиТоваров |
| **НайтиТовар(query)** | ОбщегоНазначения | 3-уровневый fallback: штрихкод → код → артикул | Штрихкоды, Номенклатура |
| **ОбработкаПроведения()** | 7 документов | Движения по 5 регистрам накопления | Все |
| **ПолучитьРозничнуюЦену()** | ОбщегоНазначения | Временной запрос цены | ЦеныНоменклатуры |

### ❄️ Cold Path (нечастые операции)

| Функция | Откуда | Что делает |
|---------|--------|-----------|
| НастройкиПоУмолчанию (геттеры) | CommonModule | Key-value хранилище настроек, кешируется |
| КассовыеСмены (state machine) | CommonModule | Открытие/закрытие, проверка 24ч лимита |
| Импорт/экспорт CSV | Обработки | Пакетная загрузка номенклатуры |
| Загрузка закупочных цен | Обработка | Пакетная загрузка цен |

### Документы → движения по регистрам

| Документ | ОстаткиТоваров | ДенежныеСредства | Взаиморасчеты | Продажи | ЦеныНоменклатуры |
|----------|:-:|:-:|:-:|:-:|:-:|
| ПриходТовара | +ПРИХОД | | +РАСХОД (долг) | | +Запись (если новая цена) |
| СписаниеТовара | +РАСХОД | | | | |
| ВозвратТовара | +ПРИХОД | +РАСХОД | | -СТОРНО | |
| Переоценка | | | | | +Запись |
| ПКО | | +ПРИХОД | | | |
| РКО | | +РАСХОД | +ПРИХОД (долг↓) | | |
| КассоваяСмена | (нет движений — оркестрация) | | | | |

---

## 3. Выбор языка с учётом AI-агента

### Почему AI-агент меняет расклад

| Фактор | Ручная разработка | С AI-агентом |
|--------|-------------------|-------------|
| Бойлерплейт Rust | Минус ×2 времени | **Нивелирован** — агент генерирует мгновенно |
| Борьба с borrow checker | -30% продуктивности | **-5%** — агент знает паттерны |
| ORM-маппинг | 1-2 недели | **2-3 дня** |
| Перевод BSL → новый язык | Ручная семантическая работа | **Прямой перевод** |
| Тесты | 1.5-2 недели | **3-4 дня** |

### Сравнение сроков

| Вариант | Ручная разработка | С AI-агентом | Выигрыш |
|---------|-------------------|-------------|---------|
| Python (FastAPI) | 3 мес. | **3-4 недели** | ×3-4 |
| Гибрид Python+Rust (PyO3) | 3.5 мес. | **4-5 недель** | ×3 |
| **Чистый Rust (Axum)** | 5-6 мес. | **5-7 недель** | ×4 |

### Рекомендация: ЧИСТЫЙ RUST (Axum + SQLx + PostgreSQL)

С AI-агентом главный минус Rust (многословность) исчезает, а плюсы остаются:

| Плюс | Значение для POS |
|------|-----------------|
| Один бинарник ~10MB | Деплой = скопировать файл |
| 10-30MB RAM | Работает на мини-ПК кассы |
| Типобезопасность | Компилятор ловит ошибки агента до рантайма |
| Нет GC-пауз | Стабильность на 24ч+ кассовых сменах |
| Конкурентность (tokio) | 50+ касс одновременно без проблем |

---

## 4. Архитектура Rust-бэкенда

### Структура проекта

```
ptm-server/
├── Cargo.toml
├── src/
│   ├── main.rs              # Axum app + tower middleware
│   ├── config.rs            # Настройки (env / toml)
│   ├── error.rs             # Error types
│   ├── db/
│   │   ├── mod.rs
│   │   ├── pool.rs          # SQLx PostgreSQL async pool
│   │   └── migrations/      # SQL миграции
│   ├── models/
│   │   ├── catalog.rs       # Номенклатура, Контрагенты, Кассы, Склады
│   │   ├── document.rs      # 7 типов документов + табличные части
│   │   └── register.rs      # 5 регистров накопления + регистры сведений
│   ├── services/
│   │   ├── barcode.rs       # Поиск по штрихкоду (HashMap, O(1))
│   │   ├── posting.rs       # Проведение 7 типов документов → движения
│   │   ├── stock.rs         # Контроль остатков при списании
│   │   ├── shifts.rs        # Кассовые смены (state machine)
│   │   ├── settings.rs      # НастройкиПоУмолчанию (in-memory cache)
│   │   ├── prices.rs        # Ценообразование + история цен
│   │   └── import.rs        # CSV/JSON импорт номенклатуры
│   └── api/
│       ├── goods.rs         # GET /api/goods, /api/search
│       ├── documents.rs     # POST /api/documents/{type}
│       ├── shifts.rs        # /api/shifts (open/close/status)
│       ├── reports.rs       # /api/reports/sales, /stock
│       └── auth.rs          # JWT login
├── tests/
│   ├── posting_tests.rs
│   ├── stock_tests.rs
│   └── api_tests.rs
└── Dockerfile               # multi-stage → scratch ~15MB
```

### Ключевые технические решения

| Компонент | Решение | Почему |
|-----------|--------|--------|
| HTTP-фреймворк | **Axum** | Самый эргономичный, tower middleware, активная разработка |
| БД | **SQLx** (compile-time checked queries) | Ошибки SQL на компиляции, async, без ORM overhead |
| Auth | **JWT (jsonwebtoken crate)** | Stateless, подходит для POS |
| Миграции | **sqlx-cli** | Встроено в SQLx |
| Сериализация | **Serde** | Стандарт де-факто |
| Штрихкоды | **In-memory HashMap** | O(1) поиск, загрузка при старте |
| Контроль остатков | **SELECT FOR UPDATE + HashMap** | Транзакционная блокировка |
| Деплой | **Docker multi-stage** | 15MB образ на scratch |

### Поиск товара по штрихкоду (O(1))

```rust
pub struct BarcodeIndex {
    // barcode → [(product_uuid, name, price)]
    index: HashMap<String, Vec<ProductInfo>>,
}

impl BarcodeIndex {
    /// 3-уровневый fallback: штрихкод → код → артикул (как в 1С)
    pub fn find(&self, query: &str) -> Vec<ProductInfo> {
        // 1. Точное совпадение по штрихкоду
        if let Some(products) = self.index.get(query) {
            return products.clone();
        }
        // 2-3. Fallback по коду/артикулу
        let upper = query.to_uppercase();
        self.index.values().flatten()
            .filter(|p| p.code == upper || p.article == upper)
            .cloned().collect()
    }
}
```

### Проведение документа (движения по регистрам)

```rust
pub async fn post_document(
    db: &PgPool, doc: &Document
) -> Result<Vec<RegisterMovement>, PostingError> {
    let mut tx = db.begin().await?;
    
    let movements = match doc.doc_type {
        DocType::ПриходТовара => calc_prihod_movements(doc),
        DocType::СписаниеТовара => {
            // Контроль остатков ПЕРЕД проведением
            check_stock(&mut tx, doc).await?;
            calc_spisanie_movements(doc)
        }
        DocType::Возврат => calc_vozvrat_movements(doc),
        DocType::Переоценка => calc_revaluation_movements(doc),
        DocType::ПКО => calc_pko_movements(doc),
        DocType::РКО => calc_rko_movements(doc),
        _ => return Err(PostingError::UnknownDocType),
    };
    
    // Записать все движения одной транзакцией
    for mv in &movements {
        write_register_movement(&mut tx, mv).await?;
    }
    mark_posted(&mut tx, doc.id).await?;
    tx.commit().await?;
    
    Ok(movements)
}
```

---

## 5. План реализации (AI-агент, чистый Rust)

| Неделя | Задача | ~Строк Rust |
|--------|--------|------------|
| 1 | DB-модели (справочники + документы + регистры) + миграции SQL | ~2 000 |
| 2 | Проведение 7 типов документов + контроль остатков | ~2 500 |
| 3 | REST API (CRUD + поиск + JWT auth + Swagger) | ~1 500 |
| 4 | Кассовые смены + настройки + импорт/экспорт + штрихкоды | ~2 000 |
| 5 | Тесты + миграция данных из 1С + интеграция сканер/принтер | ~2 000 |
| 6-7 | Edge cases, нагрузочное тестирование, Docker | ~500 |

**Итого: ~10 500 строк Rust, 5-7 недель, один AI-агент.**

---

## 6. Интеграция сканера и принтера (без БПО)

| Устройство | Протокол | Решение | Crate |
|------------|----------|---------|-------|
| Сканер штрихкодов | Serial/USB HID | WebSocket → клиент → API | `serialport` или JS BarcodeDetector |
| Принтер чеков | ESC/POS | `escposify` или прямая отправка байтов | `escpospp` / raw TCP |
| Принтер этикеток | ZPL/EPL | Шаблоны → raw TCP | Строковые шаблоны |

Потребуется ~200 строк кода. Тривиальная задача.

---

## 7. Миграция данных из 1С

Однократный ETL-скрипт (Python, не Rust — для удобства):

```
1С HTTP API (ТоварыАПИ/sync) → JSON → Python скрипт → PostgreSQL

Таблицы:
- Номенклатура (справочник) → products
- Штрихкоды (регистр) → barcodes  
- ЦеныНоменклатуры (регистр) → prices
- Контрагенты → counterparties
- Кассы, Склады → cash_registers, warehouses
- ОстаткиТоваров (остатки) → stock_balances
- КассовыеСмены → cash_shifts (архив)
```

---

## 8. Итоговое сравнение вариантов

| Критерий | Остаться на 1С | Python (FastAPI) | Rust (Axum) |
|----------|:-:|:-:|:-:|
| Объём миграции | 0 | 13 500 → ~6 800 | 13 500 → ~10 500 |
| Сроки (AI-агент) | 0 | 3-4 недели | **5-7 недель** |
| RAM сервера | ~500MB | ~200MB | **10-30MB** |
| Деплой | Конфигуратор | virtualenv + systemd | **Один бинарник** |
| Типобезопасность | Слабая (BSL) | Слабая (Python) | **Строгая (компилятор)** |
| Производительность | Хорошая | Хорошая | **Отличная** |
| Фискал | Встроен | ❌ Отдельно | ❌ Отдельно |
| Стоимость лицензии | $10-50K/год | $0 | **$0** |
| Долгосрочная поддержка | Зависимость от 1С | Хорошая | **Отличная (компилятор)** |

---

## 9. Стратегия параллельной разработки (Multi-Agent)

### 9.1 Cargo workspace: 4 crate = 4 агента

```
ptm-workspace/
├── Cargo.toml              ← workspace root
├── crates/
│   ├── ptm-models/         ← Agent A: DB-модели, миграции, типы, трейты
│   ├── ptm-engine/         ← Agent B: проведение, остатки, бизнес-логика
│   ├── ptm-services/       ← Agent C: штрихкоды, смены, настройки, импорт
│   └── ptm-api/            ← Agent D: HTTP-роуты, auth, middleware, DevOps
├── ptm-server/             ← Orchestrator crate (main.rs)
└── tests/                  ← Общие интеграционные тесты
```

Граф зависимостей:

```
ptm-models ──────┬──→ ptm-engine  ──→ ptm-server
                 ├──→ ptm-services ──→ ptm-server
                 └──→ ptm-api ──────→ ptm-server
```

`ptm-models` — фундамент. Остальные три crate зависят от него, но **НЕ зависят друг от друга** → полный параллелизм.

### 9.2 Трёхфазный план (4 агента)

| Фаза | Длит. | Agent A (Models) | Agent B (Engine) | Agent C (Services) | Agent D (API + DevOps) |
|:---:|:---:|---|---|---|---|
| **Ф1** | 2-3 дня | DB-модели, миграции, типы, трейты, interfaces.rs | **Ожидает** interfaces.rs | **Ожидает** interfaces.rs | API-контракты (OpenAPI spec), JWT scaffolding |
| **Ф2** | 5-7 дней | Unit-тесты, Data migration ETL | 7 документов → движения, контроль остатков | Штрихкоды, смены, настройки, цены, импорт | HTTP-роуты, middleware, Swagger |
| **Ф3** | 3-4 дня | Интеграц. тесты | Edge cases, нагрузка | Сканер/принтер интеграция | Docker, CI/CD, деплой |

### 9.3 Хронология по дням

```
День  1-3:  ████████ Agent A: models + migrations + interfaces.rs
            ░░░░░░░░ Agents B,C ждут интерфейсы (Agent D делает OpenAPI)
          
День  4-10: ████████ Agent A: тесты моделей + ETL миграция данных
            ████████ Agent B: posting engine (7 типов документов)
            ████████ Agent C: barcode, shifts, settings, prices
            ████████ Agent D: API routes, auth, middleware
            
День 11-14: ████████ Agent A: интеграционные тесты
            ████████ Agent B: edge cases + нагрузочные тесты
            ████████ Agent C: scanner/printer integration
            ████████ Agent D: Docker + deploy scripts
```

### 9.4 interfaces.rs — контракт для параллельной работы

Главный файл, который Agent A создаёт в Фазе 1 и который разблокирует остальных:

```rust
// crates/ptm-models/src/interfaces.rs

/// Движение по регистру (output проведения)
pub struct RegisterMovement {
    pub register: RegisterType,
    pub direction: MovementDirection, // Income | Expense
    pub product_id: Option<Uuid>,
    pub amount: Decimal,
    pub quantity: Option<Decimal>,
    pub period: NaiveDateTime,
    pub document_id: Uuid,
}

/// Трейт проведения — Agent B реализует для каждого типа документа
pub trait Postable {
    async fn post(&self, tx: &mut PgTransaction) -> Result<Vec<RegisterMovement>, PostingError>;
    async fn unpost(&self, tx: &mut PgTransaction) -> Result<(), PostingError>;
}

/// Трейт сервиса — Agent C реализует для каждого модуля
pub trait ProductSearch: Send + Sync {
    async fn find(&self, query: &str) -> Result<Vec<ProductInfo>, SearchError>;
}
pub trait ShiftManager: Send + Sync {
    async fn open(&self, params: OpenShiftParams) -> Result<Shift, ShiftError>;
    async fn close(&self, shift_id: Uuid) -> Result<ShiftReport, ShiftError>;
}

/// API-контракты — Agent D строит роуты вокруг этих типов
pub struct ApiResponse<T> { pub data: T, pub error: Option<String> }
pub struct PaginatedResponse<T> { pub items: Vec<T>, pub total: i64, pub page: i32 }
```

### 9.5 Распределение объёма по агентам

| Agent | Crate | ~Строк | Ответственность |
|:---:|---|:---:|---|
| A | **ptm-models** | 2 500 | Структуры, SQL-миграции, CRUD, ETL, интеграц. тесты |
| B | **ptm-engine** | 3 000 | Проведение 7 типов, контроль остатков, бизнес-правила |
| C | **ptm-services** | 2 500 | Штрихкоды, смены, настройки, цены, импорт, принтер |
| D | **ptm-api** | 2 500 | Роуты, JWT, middleware, Swagger, Docker |

### 9.6 Протокол координации

1. Agent A выдаёт `interfaces.rs` (трейты + типы) → День 2
2. Каждый агент работает в СВОЁМ crate → 0 merge-конфликтов
3. Общий `Cargo.toml` workspace → компиляция проверяет стыки
4. Git: каждый агент = ветка (`feat/models`, `feat/engine`, `feat/services`, `feat/api`)
5. Merge в main после каждой фазы (точки синхронизации)

### 9.7 Почему 4 агента — оптимум

| Агентов | Параллелизм | Координация | Итого |
|:---:|---|---|---|
| 1 | 0% | 0 overhead | 5-7 недель |
| 2 | ~40% | Минимальная | 3-4 недели |
| **4** | **~75%** | **Управляемая** | **~2 недели** |
| 6+ | ~80% | Merge-хаос, дублирование | ~2 нед. + конфликты |

Проект в 10 500 строк не делится тоньше 4 crate без создания искусственных зависимостей.

### 9.8 Риски и митигация

| Риск | Вероятность | Митигация |
|------|:-:|---|
| Рассинхрон интерфейсов | Средняя | `interfaces.rs` фиксируется в Фазе 1, изменения через PR |
| Merge-конфликты | Низкая | Cargo workspace: каждый crate = изолированная директория |
| Дублирование логики | Средняя | `ptm-models` — единственный источник типов и трейтов |
| Один агент блокирует остальных | Низкая | Фаза 1 короткая (~3 дня), критический путь = Agent A |

### 9.9 Итоговое сравнение сроков

| Сценарий | Срок | Выигрыш vs 1 агент |
|----------|:---:|:---:|
| 1 агент (последовательно) | 5-7 недель | — |
| 2 агента | 3-4 недели | ×1.7 |
| **4 агента (рекомендация)** | **~2 недели** | **×3** |
| 6 агентов | ~2 недели | ×3 (потолок) |

---

## 10. Плагинная архитектура (сохранение модели расширений 1С)

### 10.1 Текущие расширения 1С → Rust плагины

```
PTM (Base) ─────────────────────────────────────────────
  ├── MCP_Extension      (AddOn, prefix: mcp_)  → ptm-plugin-mcp
  ├── PTM_Analytics      (Custom, prefix: Анл_) → ptm-plugin-analytics
  ├── PTM_Fiscal         (Custom, prefix: Фскл_) → ptm-plugin-fiscal
  └── PTM_Driver_Emulator (Custom, prefix: Эмл_) → ptm-plugin-drivers
```

| 1С Extension | Rust Plugin Crate | Содержимое |
|---|---|---|
| PTM (Base) | `ptm-core` | Документы, регистры, справочники, проведение |
| MCP_Extension | `ptm-plugin-mcp` | MCP-сервер для Copilot (dev only) |
| PTM_Analytics | `ptm-plugin-analytics` | 9 отчётов, РМК, мобильная касса |
| PTM_Fiscal | `ptm-plugin-fiscal` | Фискализация через EventBus → ПРРО |
| PTM_Driver_Emulator | `ptm-plugin-drivers` | Сканер, принтер (real + emulator) |

### 10.2 Подход: Cargo features + trait registry + EventBus

Для POS не нужен hot-reload (перезапуск ~2 сек). Зато критична типобезопасность (деньги).

- Каждый плагин = **отдельный crate** в Cargo workspace
- Активация через **Cargo features** (compile-time) + **plugins.toml** (runtime config)
- **EventBus** заменяет 1С EventSubscriptions (подписки на события)
- Плагины **не трогают** core — только реализуют трейты

### 10.3 Структура проекта

```
ptm-workspace/
├── Cargo.toml                         ← workspace + features
├── crates/
│   ├── ptm-core/                      ← ЯДРО (всегда включено)
│   │   └── src/
│   │       ├── plugin.rs              ← Plugin trait + PluginRegistry
│   │       ├── events.rs              ← EventBus (pub/sub)
│   │       ├── models/                ← базовые модели (документы, справочники)
│   │       ├── services/              ← проведение, остатки, цены
│   │       └── api/                   ← core API routes
│   ├── ptm-plugin-analytics/          ← ≡ PTM_Analytics
│   │   └── src/
│   │       ├── lib.rs                 ← impl Plugin for AnalyticsPlugin
│   │       ├── reports/               ← 9 отчётов (SQL-запросы к регистрам)
│   │       ├── routes.rs              ← /api/reports/*
│   │       └── mobile.rs              ← мобильная касса API
│   ├── ptm-plugin-fiscal/             ← ≡ PTM_Fiscal
│   │   └── src/
│   │       ├── lib.rs                 ← impl Plugin for FiscalPlugin
│   │       ├── provider.rs            ← trait FiscalProvider (абстракция ПРРО)
│   │       └── handlers.rs            ← event handlers (после проведения → чек)
│   ├── ptm-plugin-drivers/            ← ≡ PTM_Driver_Emulator
│   │   └── src/
│   │       ├── lib.rs                 ← impl Plugin for DriversPlugin
│   │       ├── scanner.rs             ← trait Scanner + USB/Serial
│   │       ├── printer.rs             ← trait ReceiptPrinter + ESC/POS
│   │       └── emulator.rs            ← mock-реализации для разработки
│   └── ptm-plugin-mcp/               ← ≡ MCP_Extension (dev only)
│       └── src/
│           ├── lib.rs                 ← impl Plugin for McpPlugin
│           └── tools/                 ← MCP tools для Copilot
├── ptm-server/                        ← main.rs — собирает ядро + плагины
└── config/
    └── plugins.toml                   ← активные плагины + настройки
```

### 10.4 Plugin trait (контракт ядра)

```rust
// crates/ptm-core/src/plugin.rs

#[async_trait]
pub trait Plugin: Send + Sync + 'static {
    /// Уникальное имя ("analytics", "fiscal", "drivers", "mcp")
    fn name(&self) -> &'static str;
    fn version(&self) -> &'static str;
    
    /// Зависимости от других плагинов
    fn dependencies(&self) -> Vec<&'static str> { vec![] }
    
    /// Инициализация (БД, кэши, подключения)
    async fn init(&self, ctx: &PluginContext) -> Result<(), PluginError>;
    
    /// HTTP-роуты плагина (монтируются в общий Router)
    fn routes(&self) -> Router { Router::new() }
    
    /// Подписки на события (≡ EventSubscriptions в 1С)
    fn event_subscriptions(&self) -> Vec<EventSubscription> { vec![] }
    
    /// SQL-миграции плагина (свои таблицы)
    fn migrations(&self) -> Vec<Migration> { vec![] }
    
    /// Graceful shutdown
    async fn shutdown(&self) -> Result<(), PluginError> { Ok(()) }
}

/// Контекст: read-only доступ к ядру
pub struct PluginContext {
    pub db: PgPool,
    pub event_bus: EventBus,
    pub settings: Settings,
    pub config: PluginConfig,      // секция [plugin.xxx] из plugins.toml
}
```

### 10.5 EventBus (замена EventSubscriptions)

```rust
// crates/ptm-core/src/events.rs

#[derive(Clone, Debug)]
pub enum Event {
    DocumentPosted { doc_type: DocType, doc_id: Uuid, movements: Vec<RegisterMovement> },
    DocumentUnposted { doc_type: DocType, doc_id: Uuid },
    ShiftOpened { shift_id: Uuid, register_id: Uuid },
    ShiftClosed { shift_id: Uuid, report: ShiftReport },
    PriceChanged { product_id: Uuid, old_price: Decimal, new_price: Decimal },
    Custom { name: String, payload: serde_json::Value },
}

#[async_trait]
pub trait EventHandler: Send + Sync {
    fn handles(&self, event: &Event) -> bool;
    async fn handle(&self, event: &Event, ctx: &PluginContext) -> Result<(), PluginError>;
    fn priority(&self) -> i32 { 50 }  // меньше = раньше (Fiscal=10, Analytics=100)
}

pub struct EventBus {
    handlers: RwLock<Vec<Arc<dyn EventHandler>>>,
}

impl EventBus {
    pub async fn publish(&self, event: &Event, ctx: &PluginContext) -> Result<(), PluginError> {
        let handlers = self.handlers.read().await;
        let mut relevant: Vec<_> = handlers.iter()
            .filter(|h| h.handles(event)).collect();
        relevant.sort_by_key(|h| h.priority());
        for handler in relevant {
            handler.handle(event, ctx).await?;
        }
        Ok(())
    }
}
```

### 10.6 Пример: Fiscal Plugin (≡ PTM_Fiscal)

```rust
// crates/ptm-plugin-fiscal/src/lib.rs

pub struct FiscalPlugin { provider: Arc<dyn FiscalProvider> }

#[async_trait]
impl Plugin for FiscalPlugin {
    fn name(&self) -> &'static str { "fiscal" }
    fn version(&self) -> &'static str { "0.1.0" }
    
    async fn init(&self, ctx: &PluginContext) -> Result<(), PluginError> {
        self.provider.connect(&ctx.config).await
    }
    
    fn routes(&self) -> Router {
        Router::new()
            .route("/api/fiscal/status", get(fiscal_status))
            .route("/api/fiscal/receipt", post(send_receipt))
    }
    
    fn event_subscriptions(&self) -> Vec<EventSubscription> {
        vec![EventSubscription::new("after_post", self.fiscal_handler())]
    }
}

// После проведения продажи → автоматическая фискализация
struct FiscalPostingHandler { provider: Arc<dyn FiscalProvider> }

#[async_trait]
impl EventHandler for FiscalPostingHandler {
    fn handles(&self, event: &Event) -> bool {
        matches!(event, Event::DocumentPosted { doc_type: DocType::Продажа, .. })
    }
    fn priority(&self) -> i32 { 10 } // До аналитики!
    async fn handle(&self, event: &Event, _ctx: &PluginContext) -> Result<(), PluginError> {
        if let Event::DocumentPosted { movements, .. } = event {
            let receipt = build_fiscal_receipt(movements);
            self.provider.register_receipt(&receipt).await?;
        }
        Ok(())
    }
}
```

### 10.7 Сборка из main.rs

```rust
// ptm-server/src/main.rs

#[tokio::main]
async fn main() {
    let config = load_config("config/plugins.toml");
    let db = PgPool::connect(&config.database_url).await.unwrap();
    let event_bus = EventBus::new();
    
    let mut registry = PluginRegistry::new(db.clone(), event_bus.clone());
    registry.register(CorePlugin::new());
    
    #[cfg(feature = "analytics")]
    if config.plugin_enabled("analytics") {
        registry.register(AnalyticsPlugin::new());
    }
    #[cfg(feature = "fiscal")]
    if config.plugin_enabled("fiscal") {
        registry.register(FiscalPlugin::new(config.fiscal_provider()));
    }
    #[cfg(feature = "drivers")]
    if config.plugin_enabled("drivers") {
        registry.register(DriversPlugin::new());
    }
    
    registry.init_all().await.unwrap();
    let app = registry.build_router();
    axum::serve(TcpListener::bind("0.0.0.0:8080").await.unwrap(), app).await.unwrap();
}
```

### 10.8 plugins.toml (конфигурация)

```toml
[server]
port = 8080
database_url = "postgres://ptm:secret@localhost/ptm"

[plugins]
analytics = { enabled = true }
fiscal = { enabled = true, provider = "checkbox" }
drivers = { enabled = true, mode = "real" }    # или "emulator"
mcp = { enabled = false }                      # только для dev

[plugin.fiscal]
api_url = "https://api.checkbox.ua"
api_key = "..."

[plugin.drivers]
scanner_port = "COM3"
printer_ip = "192.168.1.100"
printer_type = "escpos"
```

### 10.9 Cargo features (compile-time toggle)

```toml
# ptm-server/Cargo.toml
[features]
default = ["analytics", "fiscal", "drivers"]
analytics = ["dep:ptm-plugin-analytics"]
fiscal = ["dep:ptm-plugin-fiscal"]
drivers = ["dep:ptm-plugin-drivers"]
mcp = ["dep:ptm-plugin-mcp"]
full = ["analytics", "fiscal", "drivers", "mcp"]

# Варианты сборки:
# cargo build                        → core + analytics + fiscal + drivers
# cargo build --no-default-features  → только ядро
# cargo build --features full        → всё включая MCP
# cargo build --features fiscal      → ядро + фискал
```

### 10.10 Преимущества vs 1С Extensions

| Аспект | 1С Extensions | Rust Plugins |
|---|---|---|
| Изоляция | Средняя (общая ИБ) | **Строгая** (trait boundaries) |
| Типобезопасность | ❌ Runtime ошибки | ✅ Compile-time |
| Тестирование | ❌ Только в ИБ | ✅ Unit tests + mock |
| Деплой | ~15 сек | **~2 сек** перезапуск |
| Dependencies | Неявные | **Явные** (Cargo.toml) |
| Event handlers | XML подписки | **Типизированный** EventBus |
| Доступ к ядру | Полный (опасно) | **Read-only** PluginContext |

### 10.11 Обновлённый Multi-Agent план (с плагинами)

| Agent | Crate(s) | ~Строк | Ответственность |
|:---:|---|:---:|---|
| A | **ptm-core** | 4 000 | Модели, проведение, Plugin trait, EventBus |
| B | **ptm-plugin-analytics** | 2 000 | 9 отчётов, РМК, мобильная касса |
| C | **ptm-plugin-fiscal** | 1 000 | FiscalProvider + Checkbox impl |
| D | **ptm-plugin-drivers** | 800 | Scanner/Printer traits + ESC/POS |
| E | **ptm-server + ptm-plugin-mcp** | 1 500 | Assembly, auth, Docker, MCP |

Срок: **~2 недели** (5 агентов, critical path = Agent A).

---

## 11. Стратегия постепенной миграции (Strangler Fig)

### 11.1 Общая схема

```
ФАЗА 1 (нед. 1):     Svelte фронт → 1С HTTP API
ФАЗА 2a (нед. 2-4):  Rust read-only → постепенно забирает GET endpoints
ФАЗА 2b (1 вечер):   Data migration 1С → PostgreSQL, переключение write → Rust
ФАЗА 3 (нед. 5):     1С отключена. Чистый Rust + Svelte.
```

### 11.2 Архитектура по фазам

```
ФАЗА 1: Новый фронт + 1С бэкенд
┌──────────┐     HTTP      ┌──────────┐
│  Svelte  │ ────────────→ │   1С     │
│  Frontend│               │ HTTP API │
└──────────┘               └──────────┘

ФАЗА 2: API Gateway + dual backend
┌──────────┐     ┌──────────────┐     ┌──────────┐
│  Svelte  │ ──→ │ API Gateway  │ ──→ │ Rust     │ (read endpoints)
│  Frontend│     │ (Rust/Nginx) │     │ Backend  │
└──────────┘     │              │ ──→ ┌──────────┐
                 └──────────────┘     │ 1С       │ (write endpoints)
                                      │ HTTP API │
                                      └──────────┘

ФАЗА 3: Полный Rust
┌──────────┐     HTTP      ┌──────────┐
│  Svelte  │ ────────────→ │  Rust    │
│  Frontend│               │ Backend  │
└──────────┘               └──────────┘
```

### 11.3 Фаза 1: Доработки 1С API

Текущие API 1С уже покрывают мобильную кассу. Нужно дописать:

| Эндпоинт | Для чего | ~Строк BSL |
|-----------|----------|:-:|
| `GET /api/documents` | Список документов | ~80 |
| `POST /api/documents/{type}` | Создание документа | ~120 |
| `GET /api/reports/{name}` | 9 отчётов | ~200 |
| `GET /api/catalogs/{name}` | CRUD справочников | ~100 |
| `GET /api/registers/{name}` | Чтение регистров | ~80 |
| `POST /api/shifts/open\|close` | Управление сменами | ~60 |
| `GET /api/settings` | Настройки | ~40 |

**Итого:** ~680 строк BSL в расширении PTM_Analytics (1-2 дня с AI-агентом).

### 11.4 Фаза 2: Порядок переноса endpoints (read → write)

| Этап | Что переносим | Сложность | Откат |
|:---:|---|:-:|:-:|
| 2.1 | `GET /api/catalogs/*` (справочники) | ✅ Простая | Мгновенный |
| 2.2 | `GET /api/search` (поиск товара) | ✅ Простая | Мгновенный |
| 2.3 | `GET /api/reports/*` (9 отчётов) | Средняя | Мгновенный |
| 2.4 | `GET /api/settings`, `/shifts/status` | ✅ Простая | Мгновенный |
| 2.5 | `POST /api/shifts/open\|close` | Средняя | ⚠️ Синхронизация |
| 2.6 | `POST /api/documents/*` (проведение) | 🔴 Критический | ⚠️ Миграция данных |
| 2.7 | Mobile API (`/cart`, `/send`) | Средняя | ⚠️ |

Принцип: этапы 2.1-2.4 (read-only) безопасны — Rust читает из PostgreSQL, 1С пишет в ИБ, данные синхронизируются однократным ETL. Этапы 2.5-2.7 (write) переключаются разом (Стратегия C — Pragmatic Strangler).

### 11.5 Синхронизация данных

Стратегия C: **read endpoints мигрируют постепенно, write endpoints переключаются за один вечер.**

- Этапы 2.1-2.4: Rust читает из PostgreSQL, данные загружены ETL однократно + периодическая синхронизация (`/api/goods/sync`)
- Этап 2.5-2.7: Даунтайм ~1 час → финальная миграция данных → переключение всех write → 1С off

Это позволяет избежать двойной записи и конфликтов.

### 11.6 Overhead постепенной vs Big Bang

| Что | Big Bang | Постепенная | Overhead |
|-----|:-:|:-:|:-:|
| Расширение 1С API | 0 | ~680 строк BSL | **+1-2 дня** |
| API Gateway | 0 | ~200 строк Rust | **+0.5 дня** |
| Двойное тестирование | 0 | ~500 строк тестов | **+1 день** |
| Поддержка двух систем | 0 | ~1 нед. overlap | **+1 неделя** |
| **ИТОГО** | **~2 нед.** | **~4-5 нед.** | **+2-3 нед.** |

### 11.7 Выигрыш Фазы 1 (до Rust)

Уже после первой недели пользователи получают:

| Метрика | До (1С клиент) | После (Svelte → 1С API) |
|---------|:-:|:-:|
| UX | 1С-интерфейс (десктоп) | Modern PWA (mobile) |
| Offline | ❌ | ✅ Service Worker |
| Загрузка | ~5-10 сек | ~1 сек (SPA) |
| Мульти-платформа | Windows only | Любой браузер |
| Install as app | ❌ | ✅ Add to Home Screen |

### 11.8 Timeline (5 агентов, постепенная миграция)

```
Неделя 1:   ██ Agent A: HTTP API расширение 1С (PTM_Analytics)
            ████████ Agent E: Svelte scaffold + PWA
            ████████ Agent B: UI компоненты (Login, POS, Cart, Scanner)

→ MILESTONE: Svelte фронт работает с 1С бэкендом ✅

Неделя 2:   ████████ Agent A: ptm-core (models, Plugin trait, EventBus)
            ████████ Agent E: Frontend → 1С API интеграция + тесты
            ░░░░░░░░ Agents C,D ждут interfaces

Неделя 3:   ████████ Agent A: ptm-core (проведение, остатки)
            ████████ Agent B: ptm-plugin-analytics (отчёты)
            ████████ Agent C: ptm-plugin-fiscal
            ████████ Agent D: ptm-plugin-drivers

Неделя 4:   ████████ Agent A: API Gateway + read-only endpoints Rust
            ████████ Agent E: Frontend → Rust (read endpoints)
            ████████ Agents B,C,D: тесты + edge cases

→ MILESTONE: Read на Rust, write на 1С ✅

Неделя 5:   ████ Data migration (1С → PostgreSQL)
            ████████ Переключение write → Rust
            ████████ Integration testing

→ MILESTONE: 1С отключена, чистый Rust + Svelte ✅
```

### 11.9 Итоговое сравнение стратегий

| Критерий | Big Bang (~2 нед.) | Постепенная (~5 нед.) |
|----------|:-:|:-:|
| Риск | 🔴 Высокий | ✅ Низкий |
| Даунтайм | ~1 день | ~1 час |
| Результат для пользователей | После 2 недель | **После 1 недели** (фронт) |
| Откат | Полный (назад на 1С) | На любом этапе |
| Overhead | 0 | +2-3 недели |
| Для production-системы | ⚠️ Рискованно | ✅ Рекомендуется |
