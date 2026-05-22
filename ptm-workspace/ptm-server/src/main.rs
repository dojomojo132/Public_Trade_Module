use axum::{
    extract::{Extension, Path, Json as AxumJson, Query},
    routing::{get, post, put},
    Router,
};
use tower_http::cors::{Any, CorsLayer};
use ptm_core::models::ServerConfig;
use ptm_core::plugin::{Plugin, PluginRegistry};
use ptm_core::events::EventBus;
use ptm_core::posting::PostingService;
use ptm_core::services::{PriceService, ProductService, DiscountService};
use std::sync::Arc;
use ptm_plugin_analytics::AnalyticsPlugin;
use ptm_plugin_fiscal::{FiscalPlugin, StubFiscalProvider, FiscalEventHandler};
use ptm_plugin_drivers::DriversPlugin;
use ptm_plugin_mcp::McpPlugin;
use serde::{Deserialize, Serialize};
use sqlx::postgres::PgPoolOptions;
use sqlx::PgPool;
use uuid::Uuid;
use tracing_subscriber;
use rust_decimal::Decimal;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt::init();

    let config_path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent().unwrap().join("config.toml");
    let config_str = std::fs::read_to_string(&config_path)?;
    let server_config: ServerConfig = toml::from_str(&config_str)?;

    let pool = PgPoolOptions::new().max_connections(10).connect(&server_config.database_url).await?;
    sqlx::migrate!("../migrations").run(&pool).await?;

    let event_bus = EventBus::new();
    let mut registry = PluginRegistry::new(pool.clone(), event_bus.clone());
    registry.register(Box::new(AnalyticsPlugin));
    let fiscal_provider = Arc::new(StubFiscalProvider);
    registry.register(Box::new(FiscalPlugin::new(fiscal_provider.clone())));
    registry.register(Box::new(DriversPlugin));
    registry.register(Box::new(McpPlugin));
    registry.init_all(&server_config).await?;

    let fiscal_handler = Arc::new(FiscalEventHandler::new(pool.clone(), fiscal_provider));
    event_bus.register(fiscal_handler).await;

    let posting_service = Arc::new(PostingService::new(pool.clone(), event_bus.clone()));
    let price_service = Arc::new(PriceService::new(pool.clone()));
    let product_service = Arc::new(ProductService::new(pool.clone()));
    let discount_service = Arc::new(DiscountService::new(pool.clone()));
    

    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let app = Router::new()
        .route("/health", get(|| async { "OK" }))
        .route("/api/auth/login", post(login_handler))
        .route("/api/documents", post(create_document))
        .route("/api/documents/list", get(list_documents))
        .route("/api/documents/:id", get(get_document))
        .route("/api/documents/:id", put(update_document))
        .route("/api/documents/:id/post", post(post_document))
        .route("/api/documents/:id/unpost", post(unpost_document))
        .route("/api/shifts/open", post(open_shift))
        .route("/api/shifts/current", get(current_shift))
        .route("/api/shifts/:id/close", post(close_shift))
        .route("/api/products", get(list_products))
        .route("/api/products/search", get(search_products))
        .route("/api/products/barcode/:barcode", get(product_by_barcode))
        .route("/api/prices/:product_id", get(get_price))
        .route("/api/discount/:card_number", get(lookup_card))
        .route("/api/warehouses", get(list_warehouses))
        .route("/api/counterparties", get(list_counterparties))
        .route("/api/stock-balances", get(stock_balances))
        .route("/api/stock-balances-at", get(stock_balances_at))
        .merge(registry.build_router())
        .layer(Extension(pool.clone()))
        .layer(Extension(posting_service.clone()))
        .layer(Extension(price_service.clone()))
        .layer(Extension(product_service.clone()))
        .layer(Extension(discount_service.clone()))
        .layer(cors);

    let addr = format!("127.0.0.1:{}", server_config.port);
    let listener = tokio::net::TcpListener::bind(&addr).await?;
    tracing::info!("PTM Server listening on http://{}", addr);
    axum::serve(listener, app).await?;
    Ok(())
}

// ── CREATE DOCUMENT ────────────────────────────
#[derive(Deserialize)]
struct CreateDocumentRequest {
    doc_type: String,
    warehouse_id: Option<Uuid>,
    counterparty_id: Option<Uuid>,
    cash_register_id: Option<Uuid>,
    shift_id: Option<Uuid>,
    user_id: Option<Uuid>,
    lines: Vec<LineRequest>,
    payments: Vec<PaymentRequest>,
}
#[derive(Deserialize)]
struct LineRequest {
    product_id: Uuid,
    quantity: f64,
    price: f64,
    cost_price: Option<f64>,
}
#[derive(Deserialize)]
struct PaymentRequest {
    payment_type: String,
    amount: f64,
    cash_register_id: Option<Uuid>,
}

async fn create_document(
    Extension(pool): Extension<PgPool>,
    AxumJson(req): AxumJson<CreateDocumentRequest>,
) -> Result<AxumJson<serde_json::Value>, (axum::http::StatusCode, String)> {
    let doc_id = Uuid::new_v4();
    let mut tx = pool.begin().await.map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, format!("{}", e)))?;

    let total: Decimal = req.lines.iter()
        .map(|l| Decimal::from_f64_retain(l.quantity * l.price).unwrap_or_default())
        .sum();

    sqlx::query(
        "INSERT INTO documents (id, doc_type, doc_date, posted, warehouse_id, counterparty_id, cash_register_id, shift_id, user_id, total_amount) \
         VALUES ($1, $2, now(), false, $3, $4, $5, $6, $7, $8)"
    )
    .bind(doc_id).bind(&req.doc_type).bind(req.warehouse_id).bind(req.counterparty_id)
    .bind(req.cash_register_id).bind(req.shift_id).bind(req.user_id).bind(total)
    .execute(&mut *tx).await.map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, format!("{}", e)))?;

    let mut line_num = 1i32;
    for line in &req.lines {
        sqlx::query(
            "INSERT INTO document_lines (document_id, line_number, product_id, quantity, price, cost_price) \
             VALUES ($1, $2, $3, $4, $5, $6)"
        )
        .bind(doc_id).bind(line_num).bind(line.product_id)
        .bind(Decimal::from_f64_retain(line.quantity).unwrap_or_default())
        .bind(Decimal::from_f64_retain(line.price).unwrap_or_default())
        .bind(line.cost_price.map(|v| Decimal::from_f64_retain(v).unwrap_or_default()))
        .execute(&mut *tx).await.map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, format!("{}", e)))?;
        line_num += 1;
    }

    for p in &req.payments {
        sqlx::query(
            "INSERT INTO document_payments (document_id, payment_type, amount, cash_register_id) VALUES ($1, $2, $3, $4)"
        )
        .bind(doc_id).bind(&p.payment_type)
        .bind(Decimal::from_f64_retain(p.amount).unwrap_or_default())
        .bind(p.cash_register_id)
        .execute(&mut *tx).await.map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, format!("{}", e)))?;
    }

    tx.commit().await.map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, format!("{}", e)))?;

    // Создать снэпшот на начало текущего дня, если ещё не создавался
    let _ = ensure_daily_snapshot(&pool).await;

    Ok(AxumJson(serde_json::json!({
        "success": true,
        "document_id": doc_id.to_string(),
        "total": total.to_string()
    })))
}

// ── UPDATE DOCUMENT ───────────────────────────
async fn update_document(
    Extension(pool): Extension<PgPool>,
    Path(doc_id): Path<Uuid>,
    AxumJson(req): AxumJson<CreateDocumentRequest>,
) -> Result<AxumJson<serde_json::Value>, (axum::http::StatusCode, String)> {
    let row: Option<(bool,)> = sqlx::query_as("SELECT posted FROM documents WHERE id = $1")
        .bind(doc_id).fetch_optional(&pool).await
        .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, format!("{}", e)))?;
    let (posted,) = row.ok_or_else(|| (axum::http::StatusCode::NOT_FOUND, "Document not found".to_string()))?;
    if posted {
        return Err((axum::http::StatusCode::BAD_REQUEST, "Cannot edit posted document".to_string()));
    }

    let total: Decimal = req.lines.iter()
        .map(|l| Decimal::from_f64_retain(l.quantity * l.price).unwrap_or_default())
        .sum();

    let mut tx = pool.begin().await.map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, format!("{}", e)))?;

    sqlx::query("UPDATE documents SET warehouse_id=$2, counterparty_id=$3, total_amount=$4 WHERE id=$1")
        .bind(doc_id).bind(req.warehouse_id).bind(req.counterparty_id).bind(total)
        .execute(&mut *tx).await.map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, format!("{}", e)))?;

    sqlx::query("DELETE FROM document_lines WHERE document_id = $1")
        .bind(doc_id).execute(&mut *tx).await
        .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, format!("{}", e)))?;

    let mut line_num = 1i32;
    for line in &req.lines {
        sqlx::query(
            "INSERT INTO document_lines (document_id, line_number, product_id, quantity, price, cost_price) \
             VALUES ($1, $2, $3, $4, $5, $6)"
        )
        .bind(doc_id).bind(line_num).bind(line.product_id)
        .bind(Decimal::from_f64_retain(line.quantity).unwrap_or_default())
        .bind(Decimal::from_f64_retain(line.price).unwrap_or_default())
        .bind(line.cost_price.map(|v| Decimal::from_f64_retain(v).unwrap_or_default()))
        .execute(&mut *tx).await.map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, format!("{}", e)))?;
        line_num += 1;
    }

    tx.commit().await.map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, format!("{}", e)))?;

    Ok(AxumJson(serde_json::json!({
        "success": true,
        "document_id": doc_id.to_string(),
        "total": total.to_string()
    })))
}

// ── LIST PRODUCTS ──────────────────────────────
#[derive(Deserialize)]
struct ProductsQuery { page: Option<u32>, per_page: Option<u32> }

#[derive(Debug, Serialize, sqlx::FromRow)]
struct ProductListRow { id: Uuid, code: String, name: String, article: Option<String>, unit: String }

async fn list_products(
    Extension(pool): Extension<PgPool>,
    Query(q): Query<ProductsQuery>,
) -> AxumJson<serde_json::Value> {
    let page = q.page.unwrap_or(1).max(1);
    let per_page = q.per_page.unwrap_or(12);
    let offset = ((page - 1) * per_page) as i64;

    let total: (i64,) = sqlx::query_as("SELECT COUNT(*)::int8 FROM products WHERE is_deleted = false")
        .fetch_one(&pool).await.unwrap_or((0,));
    let total_pages = ((total.0 as u32) + per_page - 1) / per_page;

    let rows = sqlx::query_as::<_, ProductListRow>(
        "SELECT id, code, name, article, unit FROM products WHERE is_deleted = false ORDER BY name LIMIT $1 OFFSET $2"
    )
    .bind(per_page as i32).bind(offset)
    .fetch_all(&pool).await.unwrap_or_default();

    let products: Vec<serde_json::Value> = rows.into_iter().map(|r| serde_json::json!({
        "id": r.id.to_string(), "code": r.code, "name": r.name, "article": r.article, "unit": r.unit
    })).collect();

    AxumJson(serde_json::json!({
        "products": products, "total": total.0, "page": page, "total_pages": total_pages
    }))
}

// ── Compact handlers ────────────────────────────
async fn post_document(Extension(svc): Extension<Arc<PostingService>>, Path(doc_id): Path<Uuid>) -> Result<AxumJson<serde_json::Value>, (axum::http::StatusCode, String)> {
    match svc.post_document(doc_id).await {
        Ok(m) => Ok(AxumJson(serde_json::json!({"success": true, "movements_count": m.len()}))),
        Err(e) => { tracing::error!("Post error: {}", e); Err((axum::http::StatusCode::BAD_REQUEST, format!("{}", e))) }
    }
}
async fn unpost_document(Extension(svc): Extension<Arc<PostingService>>, Path(doc_id): Path<Uuid>) -> Result<AxumJson<serde_json::Value>, (axum::http::StatusCode, String)> {
    match svc.unpost_document(doc_id).await {
        Ok(()) => Ok(AxumJson(serde_json::json!({"success": true}))),
        Err(e) => { tracing::error!("Unpost error: {}", e); Err((axum::http::StatusCode::BAD_REQUEST, format!("{}", e))) }
    }
}

#[derive(Deserialize)] struct OpenShiftRequest { cash_register_id: Uuid, user_id: Uuid }
async fn open_shift(Extension(svc): Extension<Arc<PostingService>>, AxumJson(req): AxumJson<OpenShiftRequest>) -> Result<AxumJson<serde_json::Value>, (axum::http::StatusCode, String)> {
    match svc.open_shift(req.cash_register_id, req.user_id).await {
        Ok(id) => Ok(AxumJson(serde_json::json!({"success": true, "shift_id": id.to_string()}))),
        Err(e) => { tracing::error!("Open shift error: {}", e); Err((axum::http::StatusCode::BAD_REQUEST, format!("{}", e))) }
    }
}
#[derive(Deserialize)] struct CashRegisterQuery { cash_register_id: Option<Uuid> }
async fn current_shift(Extension(pool): Extension<sqlx::PgPool>, Query(q): Query<CashRegisterQuery>) -> AxumJson<serde_json::Value> {
    let row: Option<(Uuid, Uuid, Uuid, String, String)> = if let Some(cr_id) = q.cash_register_id {
        sqlx::query_as(
            "SELECT id, cash_register_id, user_id, status, opened_at::text FROM cash_shifts WHERE cash_register_id = $1 AND status = 'open' LIMIT 1"
        ).bind(cr_id).fetch_optional(&pool).await.unwrap_or(None)
    } else {
        sqlx::query_as(
            "SELECT id, cash_register_id, user_id, status, opened_at::text FROM cash_shifts WHERE status = 'open' ORDER BY opened_at DESC LIMIT 1"
        ).fetch_optional(&pool).await.unwrap_or(None)
    };
    match row {
        Some((id, cr_id, u_id, status, opened_at)) => AxumJson(serde_json::json!({
            "success": true,
            "shift": { "id": id.to_string(), "cash_register_id": cr_id.to_string(), "user_id": u_id.to_string(), "status": status, "opened_at": opened_at }
        })),
        None => AxumJson(serde_json::json!({ "success": true, "shift": null }))
    }
}
async fn close_shift(Extension(svc): Extension<Arc<PostingService>>, Path(shift_id): Path<Uuid>) -> Result<AxumJson<serde_json::Value>, (axum::http::StatusCode, String)> {
    match svc.close_shift(shift_id).await {
        Ok(r) => Ok(AxumJson(serde_json::json!({"success": true, "report": {"shift_id": r.shift_id.to_string(), "total_receipts": r.total_receipts, "total_revenue": r.total_revenue.to_string(), "closed_at": r.closed_at.to_string()}}))),
        Err(e) => { tracing::error!("Close shift error: {}", e); Err((axum::http::StatusCode::BAD_REQUEST, format!("{}", e))) }
    }
}

#[derive(Deserialize)] struct SQ { q: String }
async fn search_products(Extension(svc): Extension<Arc<ProductService>>, Query(p): Query<SQ>) -> AxumJson<serde_json::Value> {
    match svc.search(&p.q).await { Ok(r) => AxumJson(serde_json::json!({"success": true, "products": r})), Err(e) => AxumJson(serde_json::json!({"success": false, "error": format!("{}", e)})) }
}
async fn product_by_barcode(Extension(svc): Extension<Arc<ProductService>>, Path(b): Path<String>) -> AxumJson<serde_json::Value> {
    match svc.find_by_barcode(&b).await { Ok(Some(p)) => AxumJson(serde_json::json!({"success": true, "product": p})), Ok(None) => AxumJson(serde_json::json!({"success": false, "error": "Not found"})), Err(e) => AxumJson(serde_json::json!({"success": false, "error": format!("{}", e)})) }
}
async fn get_price(Extension(svc): Extension<Arc<PriceService>>, Path(pid): Path<Uuid>) -> AxumJson<serde_json::Value> {
    match svc.get_retail_price(pid).await { Ok(Some(pr)) => AxumJson(serde_json::json!({"success": true, "price": pr})), Ok(None) => AxumJson(serde_json::json!({"success": false, "error": "No price found"})), Err(e) => AxumJson(serde_json::json!({"success": false, "error": format!("{}", e)})) }
}
async fn lookup_card(Extension(svc): Extension<Arc<DiscountService>>, Path(cn): Path<String>) -> AxumJson<serde_json::Value> {
    match svc.find_card(&cn).await { Ok(Some(c)) => AxumJson(serde_json::json!({"success": true, "card": c})), Ok(None) => AxumJson(serde_json::json!({"success": false, "error": "Card not found"})), Err(e) => AxumJson(serde_json::json!({"success": false, "error": format!("{}", e)})) }
}

// ── AUTH / LOGIN ────────────────────────────────
#[derive(Deserialize)]
struct LoginRequest {
    username: String,
    password: String,
}

#[derive(Serialize, sqlx::FromRow)]
struct AuthUserRow {
    id: Uuid,
    login: String,
    password_hash: String,
    full_name: Option<String>,
    role: String,
}

async fn login_handler(
    Extension(pool): Extension<PgPool>,
    AxumJson(req): AxumJson<LoginRequest>,
) -> Result<AxumJson<serde_json::Value>, (axum::http::StatusCode, String)> {
    let user: AuthUserRow = sqlx::query_as("SELECT id, login, password_hash, full_name, role FROM users WHERE login = $1")
        .bind(&req.username)
        .fetch_optional(&pool)
        .await
        .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, format!("{}", e)))?
        .ok_or((axum::http::StatusCode::UNAUTHORIZED, "Неверный логин или пароль".into()))?;

    let valid = bcrypt::verify(&req.password, &user.password_hash)
        .unwrap_or(false);

    if !valid {
        return Err((axum::http::StatusCode::UNAUTHORIZED, "Неверный логин или пароль".into()));
    }

    let claims = serde_json::json!({
        "sub": user.id.to_string(),
        "login": user.login,
        "role": user.role,
        "iat": chrono::Utc::now().timestamp()
    });

    let token = jsonwebtoken::encode(
        &jsonwebtoken::Header::default(),
        &claims,
        &jsonwebtoken::EncodingKey::from_secret(b"ptm-dev-secret-key-change-in-production")
    ).map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, format!("{}", e)))?;

    Ok(AxumJson(serde_json::json!({
        "success": true,
        "token": token,
        "user": {
            "id": user.id.to_string(),
            "name": user.full_name.unwrap_or_else(|| user.login.clone()),
            "role": user.role
        }
    })))
}

// ── WAREHOUSES ──────────────────────────────────
#[derive(Debug, Serialize, sqlx::FromRow)]
struct WarehouseRow { id: Uuid, name: String }

async fn list_warehouses(
    Extension(pool): Extension<PgPool>,
) -> AxumJson<serde_json::Value> {
    let rows = sqlx::query_as::<_, WarehouseRow>(
        "SELECT id, name FROM warehouses WHERE is_deleted = false ORDER BY name"
    )
    .fetch_all(&pool).await.unwrap_or_default();
    let warehouses: Vec<serde_json::Value> = rows.into_iter().map(|r| serde_json::json!({
        "id": r.id.to_string(), "name": r.name
    })).collect();
    AxumJson(serde_json::json!({ "success": true, "warehouses": warehouses }))
}

// ── COUNTERPARTIES ──────────────────────────────
#[derive(Debug, Serialize, sqlx::FromRow)]
struct CounterpartyRow { id: Uuid, name: String, is_supplier: bool }

async fn list_counterparties(
    Extension(pool): Extension<PgPool>,
) -> AxumJson<serde_json::Value> {
    let rows = sqlx::query_as::<_, CounterpartyRow>(
        "SELECT id, name, is_supplier FROM counterparties WHERE is_deleted = false ORDER BY name"
    )
    .fetch_all(&pool).await.unwrap_or_default();
    let counterparties: Vec<serde_json::Value> = rows.into_iter().map(|r| serde_json::json!({
        "id": r.id.to_string(), "name": r.name, "is_supplier": r.is_supplier
    })).collect();
    AxumJson(serde_json::json!({ "success": true, "counterparties": counterparties }))
}

// ── STOCK BALANCES ──────────────────────────────
#[derive(Deserialize)]
struct StockBalanceQuery {
    warehouse_id: Option<String>,
}

#[derive(Debug, Serialize, sqlx::FromRow)]
struct StockBalanceRow {
    product_id: Uuid,
    product_code: String,
    product_name: String,
    unit: String,
    warehouse_id: Uuid,
    warehouse_name: String,
    quantity: rust_decimal::Decimal,
}

async fn stock_balances(
    Extension(pool): Extension<PgPool>,
    Query(q): Query<StockBalanceQuery>,
) -> AxumJson<serde_json::Value> {
    let rows = if let Some(ref wh_id) = q.warehouse_id {
        let wh_uuid = Uuid::parse_str(wh_id).unwrap_or_default();
        sqlx::query_as::<_, StockBalanceRow>(
            r#"SELECT sb.product_id, p.code AS product_code, p.name AS product_name, p.unit,
                      sb.warehouse_id, w.name AS warehouse_name, sb.quantity
               FROM stock_balances sb
               JOIN products p ON p.id = sb.product_id
               JOIN warehouses w ON w.id = sb.warehouse_id
               WHERE sb.warehouse_id = $1 AND sb.quantity != 0 AND p.is_deleted = false
               ORDER BY p.name"#
        )
        .bind(wh_uuid)
        .fetch_all(&pool).await.unwrap_or_default()
    } else {
        sqlx::query_as::<_, StockBalanceRow>(
            r#"SELECT sb.product_id, p.code AS product_code, p.name AS product_name, p.unit,
                      sb.warehouse_id, w.name AS warehouse_name, sb.quantity
               FROM stock_balances sb
               JOIN products p ON p.id = sb.product_id
               JOIN warehouses w ON w.id = sb.warehouse_id
               WHERE sb.quantity != 0 AND p.is_deleted = false
               ORDER BY w.name, p.name"#
        )
        .fetch_all(&pool).await.unwrap_or_default()
    };

    let items: Vec<serde_json::Value> = rows.into_iter().map(|r| serde_json::json!({
        "product_id": r.product_id.to_string(),
        "product_code": r.product_code,
        "product_name": r.product_name,
        "unit": r.unit,
        "warehouse_id": r.warehouse_id.to_string(),
        "warehouse_name": r.warehouse_name,
        "quantity": r.quantity.to_string()
    })).collect();
    AxumJson(serde_json::json!({ "success": true, "items": items }))
}

// ── ENSURE DAILY SNAPSHOT ───────────────────────
// Вызывается при каждом создании документа.
// Если снэпшот на начало сегодняшнего дня ещё не создан — создаём его
// (берём текущие stock_balances как "остаток на начало дня").
async fn ensure_daily_snapshot(pool: &PgPool) -> anyhow::Result<bool> {
    let today_start: (chrono::DateTime<chrono::Utc>,) = sqlx::query_as(
        "SELECT date_trunc('day', now() AT TIME ZONE 'UTC') AT TIME ZONE 'UTC'"
    ).fetch_one(pool).await?;
    let snap_at = today_start.0;

    // Проверяем, есть ли уже хоть одна запись снэпшота на этот день
    let exists: (bool,) = sqlx::query_as(
        "SELECT EXISTS(SELECT 1 FROM stock_snapshots WHERE snapshot_at = $1)"
    ).bind(snap_at).fetch_one(pool).await?;

    if exists.0 {
        return Ok(false); // снэпшот уже есть
    }

    // Создаём снэпшот из stock_balances
    let affected = sqlx::query(
        r#"INSERT INTO stock_snapshots (snapshot_at, warehouse_id, product_id, qty)
           SELECT $1, warehouse_id, product_id, quantity
           FROM stock_balances
           WHERE quantity != 0
           ON CONFLICT (snapshot_at, warehouse_id, product_id) DO NOTHING"#
    ).bind(snap_at).execute(pool).await?.rows_affected();

    tracing::info!("Daily snapshot created for {}: {} rows", snap_at.date_naive(), affected);
    Ok(true)
}

// ── STOCK BALANCES AT DATE ──────────────────────
// GET /api/stock-balances-at?at=2026-05-22T00:00:00Z&warehouse_id=<uuid>
// Возвращает остатки на момент времени T:
//   = ближайший снэпшот до T + движения от снэпшота до T
#[derive(Deserialize)]
struct StockAtQuery {
    at: Option<String>,
    warehouse_id: Option<String>,
}

async fn stock_balances_at(
    Extension(pool): Extension<PgPool>,
    Query(q): Query<StockAtQuery>,
) -> AxumJson<serde_json::Value> {
    use chrono::{DateTime, Utc};

    // Если дата не указана — текущий момент (эквивалентно stock_balances)
    let target_dt: DateTime<Utc> = q.at
        .as_deref()
        .and_then(|s| DateTime::parse_from_rfc3339(s).ok().map(|d| d.with_timezone(&Utc)))
        .unwrap_or_else(Utc::now);

    let wh_filter = q.warehouse_id
        .as_deref()
        .and_then(|s| Uuid::parse_str(s).ok());

    // Основной запрос: снэпшот + дельта движений
    let sql = r#"
        WITH last_snap AS (
            SELECT DISTINCT ON (warehouse_id, product_id)
                snapshot_at, warehouse_id, product_id, qty
            FROM stock_snapshots
            WHERE snapshot_at <= $1
              AND ($2::uuid IS NULL OR warehouse_id = $2)
            ORDER BY warehouse_id, product_id, snapshot_at DESC
        ),
        snap_base AS (
            SELECT snapshot_at AS base_at, MAX(snapshot_at) AS max_snap FROM last_snap GROUP BY snapshot_at LIMIT 1
        ),
        delta AS (
            SELECT
                sm.product_id,
                sm.warehouse_id,
                SUM(CASE WHEN sm.direction = 'in' THEN sm.quantity ELSE -sm.quantity END) AS qty_delta
            FROM stock_movements sm
            CROSS JOIN (SELECT MAX(snapshot_at) AS max_snap FROM last_snap) s
            WHERE sm.period > COALESCE(s.max_snap, '1970-01-01'::timestamptz)
              AND sm.period <= $1
              AND ($2::uuid IS NULL OR sm.warehouse_id = $2)
            GROUP BY sm.product_id, sm.warehouse_id
        )
        SELECT
            p.id           AS product_id,
            p.code         AS product_code,
            p.name         AS product_name,
            p.unit         AS unit,
            w.id           AS warehouse_id,
            w.name         AS warehouse_name,
            COALESCE(ls.qty, 0) + COALESCE(d.qty_delta, 0) AS quantity
        FROM (
            SELECT product_id, warehouse_id FROM last_snap
            UNION
            SELECT product_id, warehouse_id FROM delta
        ) combined
        JOIN products p ON p.id = combined.product_id
        JOIN warehouses w ON w.id = combined.warehouse_id
        LEFT JOIN last_snap ls ON ls.product_id = combined.product_id AND ls.warehouse_id = combined.warehouse_id
        LEFT JOIN delta d ON d.product_id = combined.product_id AND d.warehouse_id = combined.warehouse_id
        WHERE COALESCE(ls.qty, 0) + COALESCE(d.qty_delta, 0) != 0
          AND p.is_deleted = false
        ORDER BY w.name, p.name
    "#;

    #[derive(Debug, sqlx::FromRow)]
    struct Row {
        product_id: Uuid,
        product_code: String,
        product_name: String,
        unit: String,
        warehouse_id: Uuid,
        warehouse_name: String,
        quantity: rust_decimal::Decimal,
    }

    let rows = sqlx::query_as::<_, Row>(sql)
        .bind(target_dt)
        .bind(wh_filter)
        .fetch_all(&pool).await.unwrap_or_default();

    let items: Vec<serde_json::Value> = rows.into_iter().map(|r| serde_json::json!({
        "product_id": r.product_id.to_string(),
        "product_code": r.product_code,
        "product_name": r.product_name,
        "unit": r.unit,
        "warehouse_id": r.warehouse_id.to_string(),
        "warehouse_name": r.warehouse_name,
        "quantity": r.quantity.to_string()
    })).collect();

    AxumJson(serde_json::json!({
        "success": true,
        "at": target_dt.to_rfc3339(),
        "items": items
    }))
}

// ── LIST DOCUMENTS ─────────────────────────────
// GET /api/documents/list?doc_type=invoice_in&page=1&per_page=20
#[derive(Deserialize)]
struct ListDocsQuery {
    doc_type: Option<String>,
    page: Option<u32>,
    per_page: Option<u32>,
}

async fn list_documents(
    Extension(pool): Extension<PgPool>,
    Query(q): Query<ListDocsQuery>,
) -> AxumJson<serde_json::Value> {
    let page = q.page.unwrap_or(1).max(1);
    let per_page = q.per_page.unwrap_or(20).min(100);
    let offset = ((page - 1) * per_page) as i64;

    let (total_count,): (i64,) = if let Some(ref dt) = q.doc_type {
        sqlx::query_as("SELECT COUNT(*)::int8 FROM documents WHERE doc_type = $1 AND is_deleted = false")
            .bind(dt).fetch_one(&pool).await.unwrap_or((0,))
    } else {
        sqlx::query_as("SELECT COUNT(*)::int8 FROM documents WHERE is_deleted = false")
            .fetch_one(&pool).await.unwrap_or((0,))
    };

    #[derive(sqlx::FromRow)]
    struct DocRow {
        id: Uuid,
        doc_number: Option<String>,
        doc_type: String,
        doc_date: chrono::DateTime<chrono::Utc>,
        posted: bool,
        total_amount: rust_decimal::Decimal,
        warehouse_name: Option<String>,
        counterparty_name: Option<String>,
    }

    let sql_filter = if q.doc_type.is_some() {
        "WHERE d.doc_type = $1 AND d.is_deleted = false ORDER BY d.doc_date DESC LIMIT $2 OFFSET $3"
    } else {
        "WHERE d.is_deleted = false ORDER BY d.doc_date DESC LIMIT $2 OFFSET $3"
    };

    let rows: Vec<DocRow> = if let Some(ref dt) = q.doc_type {
        sqlx::query_as(&format!(
            r#"SELECT d.id, d.doc_number, d.doc_type, d.doc_date, d.posted, d.total_amount,
                      w.name AS warehouse_name, c.name AS counterparty_name
               FROM documents d
               LEFT JOIN warehouses w ON w.id = d.warehouse_id
               LEFT JOIN counterparties c ON c.id = d.counterparty_id
               {sql_filter}"#
        ))
        .bind(dt).bind(per_page as i32).bind(offset)
        .fetch_all(&pool).await.unwrap_or_default()
    } else {
        sqlx::query_as(&format!(
            r#"SELECT d.id, d.doc_number, d.doc_type, d.doc_date, d.posted, d.total_amount,
                      w.name AS warehouse_name, c.name AS counterparty_name
               FROM documents d
               LEFT JOIN warehouses w ON w.id = d.warehouse_id
               LEFT JOIN counterparties c ON c.id = d.counterparty_id
               {sql_filter}"#
        ))
        .bind(per_page as i32).bind(offset)
        .fetch_all(&pool).await.unwrap_or_default()
    };

    let docs: Vec<serde_json::Value> = rows.into_iter().map(|r| serde_json::json!({
        "id": r.id.to_string(),
        "doc_number": r.doc_number,
        "doc_type": r.doc_type,
        "doc_date": r.doc_date.to_rfc3339(),
        "posted": r.posted,
        "total_amount": r.total_amount.to_string(),
        "warehouse_name": r.warehouse_name,
        "counterparty_name": r.counterparty_name,
    })).collect();

    let total_pages = (total_count as u32 + per_page - 1) / per_page;
    AxumJson(serde_json::json!({
        "success": true,
        "documents": docs,
        "total": total_count,
        "page": page,
        "total_pages": total_pages
    }))
}

// ── GET DOCUMENT ───────────────────────────────
// GET /api/documents/:id
async fn get_document(
    Extension(pool): Extension<PgPool>,
    Path(doc_id): Path<Uuid>,
) -> Result<AxumJson<serde_json::Value>, (axum::http::StatusCode, String)> {
    #[derive(sqlx::FromRow)]
    struct DocHeader {
        id: Uuid,
        doc_number: Option<String>,
        doc_type: String,
        doc_date: chrono::DateTime<chrono::Utc>,
        posted: bool,
        total_amount: rust_decimal::Decimal,
        warehouse_id: Option<Uuid>,
        warehouse_name: Option<String>,
        counterparty_id: Option<Uuid>,
        counterparty_name: Option<String>,
    }

    let doc = sqlx::query_as::<_, DocHeader>(
        r#"SELECT d.id, d.doc_number, d.doc_type, d.doc_date, d.posted, d.total_amount,
                  d.warehouse_id, w.name AS warehouse_name,
                  d.counterparty_id, c.name AS counterparty_name
           FROM documents d
           LEFT JOIN warehouses w ON w.id = d.warehouse_id
           LEFT JOIN counterparties c ON c.id = d.counterparty_id
           WHERE d.id = $1 AND d.is_deleted = false"#
    )
    .bind(doc_id)
    .fetch_optional(&pool).await
    .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?
    .ok_or((axum::http::StatusCode::NOT_FOUND, "Document not found".into()))?;

    #[derive(sqlx::FromRow)]
    struct LineRow {
        line_number: i32,
        product_id: Uuid,
        product_code: String,
        product_name: String,
        unit: String,
        quantity: rust_decimal::Decimal,
        price: rust_decimal::Decimal,
        cost_price: Option<rust_decimal::Decimal>,
    }

    let lines = sqlx::query_as::<_, LineRow>(
        r#"SELECT dl.line_number, dl.product_id, p.code AS product_code,
                  p.name AS product_name, p.unit,
                  dl.quantity, dl.price, dl.cost_price
           FROM document_lines dl
           JOIN products p ON p.id = dl.product_id
           WHERE dl.document_id = $1
           ORDER BY dl.line_number"#
    )
    .bind(doc_id)
    .fetch_all(&pool).await
    .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let lines_json: Vec<serde_json::Value> = lines.into_iter().map(|l| serde_json::json!({
        "line_number": l.line_number,
        "product_id": l.product_id.to_string(),
        "product_code": l.product_code,
        "product_name": l.product_name,
        "unit": l.unit,
        "quantity": l.quantity.to_string(),
        "price": l.price.to_string(),
        "cost_price": l.cost_price.map(|v| v.to_string()),
        "line_total": (l.quantity * l.price).to_string(),
    })).collect();

    Ok(AxumJson(serde_json::json!({
        "success": true,
        "document": {
            "id": doc.id.to_string(),
            "doc_number": doc.doc_number,
            "doc_type": doc.doc_type,
            "doc_date": doc.doc_date.to_rfc3339(),
            "posted": doc.posted,
            "total_amount": doc.total_amount.to_string(),
            "warehouse_id": doc.warehouse_id.map(|v| v.to_string()),
            "warehouse_name": doc.warehouse_name,
            "counterparty_id": doc.counterparty_id.map(|v| v.to_string()),
            "counterparty_name": doc.counterparty_name,
            "lines": lines_json
        }
    })))
}
