# -*- coding: utf-8 -*-
"""Извлечение названий блюд и цен из PDF-меню → Excel."""

import sys
import os

# Путь к PDF (кириллица — через явный литерал)
PDF_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Меню.pdf")
OUTPUT_PATH = os.path.join(os.path.dirname(PDF_PATH), "Меню_результат.xlsx")


def analyze_pdf():
    """Анализ структуры PDF — вывести текст первых 3 страниц."""
    import pdfplumber

    pdf = pdfplumber.open(PDF_PATH)
    print(f"Страниц: {len(pdf.pages)}")

    for i, page in enumerate(pdf.pages[:3]):
        print(f"\n=== Страница {i+1} ===")
        text = page.extract_text()
        if text:
            print(text[:3000])
        tables = page.extract_tables()
        if tables:
            print(f"\nТаблицы на странице: {len(tables)}")
            for t_idx, table in enumerate(tables):
                print(f"  Таблица {t_idx+1}, строк: {len(table)}")
                for row in table[:5]:
                    print(f"    {row}")
    pdf.close()


def extract_and_save():
    """Извлечь блюда + цены из всех страниц → Excel."""
    import pdfplumber
    import re
    from openpyxl import Workbook

    pdf = pdfplumber.open(PDF_PATH)
    results = []

    # Паттерны для пропуска
    skip_patterns = re.compile(
        r"^[\d\s]*[гшт./, ]+$"       # "300 г", "1 шт", "1/2 шт ."
        r"|^[а-яА-ЯіїєґІЇЄҐёЁ\s,«»\(\)\-'']+$"  # чисто текстовая строка без цифр (описание/ингредиенты)
    )

    # Декоративные строки с удвоенными буквами (ссььооммггаа)
    double_letters = re.compile(r"(.)\1{2,}")

    for page in pdf.pages:
        text = page.extract_text()
        if not text:
            continue

        for line in text.split("\n"):
            line = line.strip()
            if not line or len(line) < 5:
                continue

            # Пропустить описания ингредиентов (удвоенные буквы)
            if double_letters.search(line) and not any(c.isdigit() for c in line[-5:]):
                continue

            # Пропустить строки с весом/штуками
            if skip_patterns.match(line):
                continue

            # Паттерн 1: название ... цена (точки + опциональный пробел + число)
            match = re.match(r"^(.+?)\s*[.\s]{3,}(\d+[\.,]?\d*)\s*$", line)

            # Паттерн 2: с весом в середине — "Тар-тар ... 200 г .............340"
            if not match:
                match = re.match(
                    r"^(.+?)\s*[.\s]{3,}\d+\s*г?\s*[.\s]{3,}(\d+[\.,]?\d*)\s*$",
                    line,
                )

            if match:
                name = match.group(1).strip().rstrip(". ")
                # Очистить название от точек в конце
                name = re.sub(r"[.\s]+$", "", name).strip()
                if not name or len(name) < 2:
                    continue
                price_str = match.group(2).replace(",", ".")
                try:
                    price = float(price_str)
                    if price > 0:
                        results.append((name, price))
                except ValueError:
                    pass

    pdf.close()

    # Сохранить в Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Меню"
    ws.append(["Название", "Цена"])

    for name, price in results:
        ws.append([name, price])

    # Автоширина колонок
    ws.column_dimensions["A"].width = 60
    ws.column_dimensions["B"].width = 12

    wb.save(OUTPUT_PATH)
    print(f"Извлечено позиций: {len(results)}")
    print(f"Сохранено: {OUTPUT_PATH}")

    # Показать первые 20
    for i, (name, price) in enumerate(results[:20]):
        print(f"  {i+1}. {name} — {price}")
    if len(results) > 20:
        print(f"  ... ещё {len(results) - 20}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--analyze":
        analyze_pdf()
    else:
        extract_and_save()
