package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math"
	"net/http"
	"strconv"
	"sync"
)

type Product struct {
	ID    uint32 `json:"id"`
	Name  string `json:"name"`
	Price uint32 `json:"price"`
}

type ProductsResponse struct {
	Products   []Product `json:"products"`
	Total      uint32    `json:"total"`
	Page       uint32    `json:"page"`
	TotalPages uint32    `json:"total_pages"`
}

type CartItem struct {
	ProductID uint32 `json:"product_id"`
	Quantity  uint32 `json:"quantity"`
}

type CheckoutRequest struct {
	Items []CartItem `json:"items"`
}

type CheckoutItem struct {
	ProductID uint32 `json:"product_id"`
	Name      string `json:"name"`
	Price     uint32 `json:"price"`
	Quantity  uint32 `json:"quantity"`
	Subtotal  uint32 `json:"subtotal"`
}

type CheckoutResponse struct {
	Items []CheckoutItem `json:"items"`
	Total uint32         `json:"total"`
}

var (
	products     = make(map[uint32]Product)
	productsMu   sync.RWMutex
)

func generateProducts() {
	names := []string{
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
	}
	for i, name := range names {
		price := 20 + (uint32(i)*13)%481
		id := uint32(i + 1)
		products[id] = Product{ID: id, Name: name, Price: price}
	}
	log.Printf("Сгенерировано %d товаров", len(products))
}

func getProducts(w http.ResponseWriter, r *http.Request) {
	productsMu.RLock()
	defer productsMu.RUnlock()

	pageStr := r.URL.Query().Get("page")
	page := uint32(1)
	if pageStr != "" {
		if p, err := strconv.ParseUint(pageStr, 10, 32); err == nil {
			page = uint32(p)
		}
	}
	if page == 0 {
		page = 1
	}

	perPage := uint32(12)
	total := uint32(len(products))
	totalPages := uint32(math.Ceil(float64(total) / float64(perPage)))
	if page > totalPages {
		page = totalPages
	}
	if totalPages == 0 {
		page = 0
	}

	start := (page - 1) * perPage
	end := start + perPage
	if end > total {
		end = total
	}
	allProducts := make([]Product, 0, len(products))
	for _, p := range products {
		allProducts = append(allProducts, p)
	}
	var items []Product
	if int(start) < len(allProducts) {
		items = allProducts[start:end]
	} else {
		items = []Product{}
	}

	resp := ProductsResponse{
		Products:   items,
		Total:      total,
		Page:       page,
		TotalPages: totalPages,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func checkout(w http.ResponseWriter, r *http.Request) {
	productsMu.RLock()
	defer productsMu.RUnlock()

	var req CheckoutRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Неверный формат запроса", http.StatusBadRequest)
		return
	}

	var items []CheckoutItem
	var total uint32

	for _, cartItem := range req.Items {
		product, ok := products[cartItem.ProductID]
		if !ok {
			http.Error(w, fmt.Sprintf("Товар с id %d не найден", cartItem.ProductID), http.StatusNotFound)
			return
		}
		subtotal := product.Price * cartItem.Quantity
		items = append(items, CheckoutItem{
			ProductID: product.ID,
			Name:      product.Name,
			Price:     product.Price,
			Quantity:  cartItem.Quantity,
			Subtotal:  subtotal,
		})
		total += subtotal
	}

	resp := CheckoutResponse{Items: items, Total: total}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}
		next.ServeHTTP(w, r)
	})
}

func main() {
	generateProducts()

	mux := http.NewServeMux()
	mux.HandleFunc("/api/products", getProducts)
	mux.HandleFunc("/api/checkout", checkout)

	addr := ":3002"
	log.Printf("Go POS backend running on http://0.0.0.0%s", addr)
	log.Fatal(http.ListenAndServe(addr, corsMiddleware(mux)))
}
