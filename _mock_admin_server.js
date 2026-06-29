const express = require('express');
const app = express();
app.use(express.json());

// ── CORS (must be before all routes) ──
app.use((_, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (_.method === 'OPTIONS') return res.sendStatus(204);
  next();
});

const PORT = 3001;

// ── Mock data ──────────────────────────────────────────────
const products = [];
const names = [
  "Молоко 3.2% 1л", "Кефир 2.5% 0.5л", "Сыр Голландский", "Хлеб белый",
  "Батон нарезной", "Вода минеральная 1.5л", "Сок яблочный 1л",
  "Стиральный порошок 3кг", "Масло сливочное 200г", "Сметана 20% 400г",
  "Творог 9% 300г", "Йогурт питьевой 0.5л", "Чай чёрный 100г",
  "Кофе растворимый 100г", "Сахар 1кг", "Мука пшеничная 2кг",
  "Яйца куриные 10шт", "Рис круглозёрный 1кг", "Гречка 1кг",
  "Макароны 500г", "Кетчуп 300г", "Майонез 400г", "Шоколад молочный",
  "Печенье овсяное 300г", "Чипсы 150г"
];
const units = ["шт", "кг", "л", "мл", "г"];

for (let i = 1; i <= 200; i++) {
  const base = names[i % names.length];
  products.push({
    id: `a${String(i).padStart(8, '0')}-0000-4000-8000-${String(i).padStart(12, '0')}`,
    code: String(i).padStart(5, '0'),
    name: i > names.length ? `${base} (арт.${i})` : base,
    article: `АРТ-${String(i).padStart(4, '0')}`,
    unit: units[i % units.length],
    price: 15 + (i * 7) % 500,
  });
}

const counterparties = [
  { id: 'c1-uuid', name: 'ООО "Молокозавод"', is_supplier: true },
  { id: 'c2-uuid', name: 'ИП Иванов А.А.', is_supplier: true },
  { id: 'c3-uuid', name: 'ООО "Супермаркет"', is_supplier: false },
  { id: 'c4-uuid', name: 'ИП Петрова И.С.', is_supplier: false },
];

const warehouses = [
  { id: 'w1-uuid', name: 'Основной склад' },
  { id: 'w2-uuid', name: 'Торговый зал' },
  { id: 'w3-uuid', name: 'Склад №2 (юг)' },
];

const discountCards = [
  { id: 'd1-uuid', name: 'Стандарт', card_number: 'DC-0001', discount_pct: 5, is_active: true },
  { id: 'd2-uuid', name: 'Серебро', card_number: 'DC-0002', discount_pct: 10, is_active: true },
  { id: 'd3-uuid', name: 'Золото', card_number: 'DC-0003', discount_pct: 15, is_active: true },
];

// ── Health ──
app.get('/health', (_, r) => r.send('OK'));

// ── Auth ──
app.post('/api/auth/login', (req, res) => {
  const { username, password } = req.body;
  if (username === 'admin' && password === 'admin')
    return res.json({ success: true, token: 'mock-jwt-token', user: { id: 'u1-uuid', name: 'Администратор', role: 'admin' } });
  res.status(401).json({ success: false, error: 'Неверный логин или пароль' });
});

// ── Products ──
app.get('/api/products', (req, res) => {
  const page = parseInt(req.query.page) || 1;
  const pp = parseInt(req.query.per_page) || 12;
  const total = products.length;
  const start = (page - 1) * pp;
  const items = products.slice(start, start + pp).map(p => ({ id: p.id, code: p.code, name: p.name, article: p.article, unit: p.unit }));
  res.json({ products: items, total, page, total_pages: Math.ceil(total / pp) });
});

app.get('/api/products/search', (req, res) => {
  const q = (req.query.q || '').toLowerCase();
  const filtered = products.filter(p => p.name.toLowerCase().includes(q) || p.code.includes(q) || (p.article || '').toLowerCase().includes(q)).slice(0, 20);
  res.json({ success: true, products: filtered.map(p => ({ id: p.id, code: p.code, name: p.name, article: p.article, unit: p.unit })) });
});

app.get('/api/products/barcode/:barcode', (req, res) => res.json({ success: false, error: 'Not found' }));
app.get('/api/prices/:pid', (req, res) => { const p = products.find(x => x.id === req.params.pid); res.json({ success: true, price: p ? p.price : 0 }); });

// ── Warehouses ──
app.get('/api/warehouses', (_, res) => res.json({ success: true, warehouses }));

// ── Counterparties ──
app.get('/api/counterparties', (_, res) => res.json({ success: true, counterparties }));

// ── Discount ──
app.get('/api/discount-cards', (req, res) => {
  res.json({ success: true, cards: discountCards.map(c => ({ id: c.id, name: c.name, card_number: c.card_number, discount_pct: c.discount_pct, is_active: c.is_active })) });
});

app.get('/api/discount/:card', (req, res) => {
  const card = discountCards.find(c => c.card_number === req.params.card);
  if (card) return res.json({ success: true, card: { id: card.id, card_number: card.card_number, discount_pct: card.discount_pct } });
  res.json({ success: false, error: 'Card not found' });
});

// ── Documents ──
const mockDocuments = {
  receipt: [
    { id:'r1', number:'ПН-00001', date:'2026-05-15', counterparty:'ООО "Молокозавод"', warehouse:'Основной склад', total:2250.00, posted:true,
      rows:[{ goods:'Молоко 3.2% 1л', qty:20, price:45.00, sum:900.00 },{ goods:'Кефир 2.5% 0.5л', qty:15, price:38.00, sum:570.00 }] },
    { id:'r2', number:'ПН-00002', date:'2026-05-16', counterparty:'ИП Иванов А.А.', warehouse:'Основной склад', total:660.00, posted:false,
      rows:[{ goods:'Хлеб белый', qty:30, price:22.00, sum:660.00 }] }
  ],
  expense: [
    { id:'e1', number:'РН-00001', date:'2026-05-16', counterparty:'ООО "Супермаркет"', warehouse:'Основной склад', total:1080.00, posted:true,
      rows:[{ goods:'Сыр Голландский', qty:2, price:320.00, sum:640.00 }] }
  ],
  transfer: [
    { id:'t1', number:'ПЕР-00001', date:'2026-05-14', warehouseFrom:'Основной склад', warehouseTo:'Торговый зал', total:900.00, posted:true,
      rows:[{ goods:'Молоко 3.2% 1л', qty:10, price:45.00, sum:450.00 }] }
  ],
  writeoff: [
    { id:'w1', number:'СП-00001', date:'2026-05-15', warehouse:'Торговый зал', reason:'Истек срок годности', total:190.00, posted:true,
      rows:[{ goods:'Молоко 3.2% 1л', qty:2, price:45.00, sum:90.00 }] }
  ],
  return_doc: [],
  kkk: [
    { id:'k1', number:'ЧЕК-00001', date:'2026-05-19', shift:'Смена 1', cashier:'Петрова А.С.', total:520.00, posted:true,
      rows:[{ goods:'Хлеб белый', qty:2, price:25.00, sum:50.00 }] }
  ]
};

app.get('/api/documents', (req, res) => {
  res.json({ success: true, documents: mockDocuments });
});

app.post('/api/documents', (req, res) => res.json({ success: true, document_id: 'doc-' + Date.now(), total: '123.45' }));

app.post('/api/documents/:id/post', (req, res) => res.json({ success: true, movements_count: 3 }));
app.post('/api/documents/:id/unpost', (req, res) => res.json({ success: true }));

// ── Shifts ──
app.post('/api/shifts/open', (req, res) => res.json({ success: true, shift_id: 'shift-' + Date.now() }));
app.post('/api/shifts/:id/close', (req, res) => res.json({ success: true, report: { shift_id: req.params.id, total_receipts: 5, total_revenue: '1234.56', closed_at: new Date().toISOString() } }));

// ── Stock balances ──
app.get('/api/stock-balances', (req, res) => {
  const items = products.slice(0, 30).map((p, i) => ({
    product_id: p.id, product_code: p.code, product_name: p.name,
    unit: p.unit, warehouse_id: 'w1-uuid', warehouse_name: 'Основной склад',
    quantity: String((i * 7) % 100)
  }));
  res.json({ success: true, items });
});

app.listen(PORT, '0.0.0.0', () => console.log(`\n  🧪 Mock API Server on http://localhost:${PORT}\n  Products: ${products.length}\n  Endpoints: products, warehouses, counterparties, discounts, auth, documents, stock\n`));
