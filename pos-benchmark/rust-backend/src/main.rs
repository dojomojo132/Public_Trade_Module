use axum::{
    extract::{Query, State},
    http::StatusCode,
    response::Json,
    routing::{get, post},
    Router,
};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use tower_http::cors::{Any, CorsLayer};

#[derive(Clone, Serialize, Debug)]
struct Product {
    id: u32,
    name: String,
    price: u32,
}

#[derive(Deserialize, Debug)]
struct ProductsQuery {
    page: Option<u32>,
}

#[derive(Serialize, Debug)]
struct ProductsResponse {
    products: Vec<Product>,
    total: u32,
    page: u32,
    total_pages: u32,
}

#[derive(Deserialize, Debug)]
struct CartItem {
    product_id: u32,
    quantity: u32,
}

#[derive(Deserialize, Debug)]
struct CheckoutRequest {
    items: Vec<CartItem>,
}

#[derive(Serialize, Debug)]
struct CheckoutResponse {
    items: Vec<CheckoutItem>,
    total: u32,
}

#[derive(Serialize, Debug)]
struct CheckoutItem {
    product_id: u32,
    name: String,
    price: u32,
    quantity: u32,
    subtotal: u32,
}

type AppState = Arc<RwLock<HashMap<u32, Product>>>;

fn generate_products() -> HashMap<u32, Product> {
    let names = [
        "Хлеб", "Молоко", "Масло", "Сыр", "Колбаса",
        "Чай", "Кофе", "Сахар", "Соль", "Мука",
        "Яйца", "Рис", "Гречка", "Макароны", "Кетчуп",
        "Майонез", "Йогурт", "Вода", "Сок", "Печенье",
        "Шоколад", "Конфеты", "Чипсы", "Орехи", "Изюм",
        "Батон", "Сметана", "Творог", "Кефир", "Сливки",
        "Мясо", "Курица", "Рыба", "Креветки", "Лимон",
        "Яблоки", "Бананы", "Апельсины", "Виноград", "Картофель",
        "Морковь", "Лук", "Капуста", "Огурцы", "Помидоры",
        "Перец", "Чеснок", "Зелень", "Имбирь", "Хрен",
    ];
    let mut map = HashMap::new();
    for (i, name) in names.iter().enumerate() {
        let price = 20 + (i as u32 * 13) % 481;
        let id = (i + 1) as u32;
        map.insert(id, Product {
            id,
            name: name.to_string(),
            price,
        });
    }
    map
}

async fn get_products(
    Query(query): Query<ProductsQuery>,
    State(state): State<AppState>,
) -> Json<ProductsResponse> {
    let page = query.page.unwrap_or(1).max(1);
    let per_page: u32 = 12;
    let products = state.read().await;
    let total = products.len() as u32;
    let total_pages = (total + per_page - 1) / per_page;
    let page = page.min(total_pages);

    let start = ((page - 1) * per_page) as usize;
    let end = (start + per_page as usize).min(products.len());

    let items: Vec<Product> = products
        .values()
        .skip(start)
        .take(end - start)
        .cloned()
        .collect();

    Json(ProductsResponse {
        products: items,
        total,
        page,
        total_pages,
    })
}

async fn checkout(
    State(state): State<AppState>,
    Json(req): Json<CheckoutRequest>,
) -> Result<Json<CheckoutResponse>, (StatusCode, String)> {
    let products = state.read().await;
    let mut items = Vec::new();
    let mut total: u32 = 0;

    for cart_item in &req.items {
        if let Some(product) = products.get(&cart_item.product_id) {
            let subtotal = product.price * cart_item.quantity;
            items.push(CheckoutItem {
                product_id: product.id,
                name: product.name.clone(),
                price: product.price,
                quantity: cart_item.quantity,
                subtotal,
            });
            total += subtotal;
        } else {
            return Err((
                StatusCode::NOT_FOUND,
                format!("Товар с id {} не найден", cart_item.product_id),
            ));
        }
    }

    Ok(Json(CheckoutResponse { items, total }))
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    let products = Arc::new(RwLock::new(generate_products()));
    tracing::info!("Сгенерировано {} товаров", products.read().await.len());

    let cors = CorsLayer::new().allow_origin(Any).allow_methods(Any).allow_headers(Any);
    let app = Router::new()
        .route("/api/products", get(get_products))
        .route("/api/checkout", post(checkout))
        .layer(cors)
        .with_state(products);

    let addr = "0.0.0.0:3001";
    tracing::info!("Rust POS backend running on http://{}", addr);
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
