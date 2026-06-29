"""
Вставляет тестовые данные в sales_movements для проверки отчёта.
Использует существующие товары из таблицы products.
"""
import psycopg2
import uuid
from datetime import datetime, timezone, timedelta

DSN = "host=localhost dbname=ptm user=postgres password=postgres"

conn = psycopg2.connect(DSN)
cur = conn.cursor()

# Получаем первые 3 товара
cur.execute("SELECT id, name FROM products WHERE is_deleted = false LIMIT 3")
products = cur.fetchall()
if not products:
    print("Товаров нет в БД. Сначала заполните справочник товаров.")
    conn.close()
    exit(1)

print(f"Найдено товаров: {len(products)}")
for p in products:
    print(f"  {p[1]} ({p[0]})")

# Вставляем тестовые движения за последние 3 дня
now = datetime.now(timezone.utc)
rows_inserted = 0

for i, (product_id, product_name) in enumerate(products):
    for day_offset in range(3):
        period = now - timedelta(days=day_offset)
        quantity = round(2.5 + i * 1.0 + day_offset * 0.5, 3)
        amount = round(quantity * (100.0 + i * 50.0), 2)

        doc_id = str(uuid.uuid4())
        # Создаём фиктивный документ-продажу
        cur.execute(
            """
            INSERT INTO documents (id, doc_type, doc_number, doc_date, posted, total_amount)
            VALUES (%s, 'receipt', %s, %s, true, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (doc_id, f"TEST-{day_offset}-{i}", period, amount)
        )

        cur.execute(
            """
            INSERT INTO sales_movements (id, document_id, period, product_id, quantity, amount)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (str(uuid.uuid4()), doc_id, period, str(product_id), quantity, amount)
        )
        rows_inserted += 1

conn.commit()
print(f"\nВставлено {rows_inserted} записей в sales_movements.")
cur.close()
conn.close()
