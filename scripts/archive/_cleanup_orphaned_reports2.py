#!/usr/bin/env python3
"""Удаление осиротевших файлов отчётов из основной конфигурации."""
import shutil
from pathlib import Path

# Абсолютный путь к папке Reports
main = Path(r"D:\Git\Public_Trade_Module") / "Конфигурация" / "Reports"
print(f"Путь: {main}")
print(f"Существует: {main.exists()}")

reports = [
    "Возвраты", "ВаловаяПрибыль", "ПродажиПоСчетам",
    "ДвижениеДенежныхСредств", "ПродажиЗаСмену", "ДвижениеТоваров",
]

for r in reports:
    d = main / r
    x = main / f"{r}.xml"
    if d.exists():
        shutil.rmtree(d)
        print(f"  rm {r}/")
    else:
        print(f"  skip {r}/ (не найдена)")
    if x.exists():
        x.unlink()
        print(f"  rm {r}.xml")
    else:
        print(f"  skip {r}.xml (не найден)")

remaining = sorted(p.name for p in main.iterdir()) if main.exists() else ["DIR NOT FOUND"]
print(f"\nОставшиеся: {remaining}")
