#!/usr/bin/env python3
"""Удаление осиротевших файлов отчётов из основной конфигурации."""
import shutil
from pathlib import Path

main = Path(__file__).resolve().parent.parent / "Конфигурация" / "Reports"
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
    if x.exists():
        x.unlink()
        print(f"  rm {r}.xml")

remaining = sorted(p.name for p in main.iterdir()) if main.exists() else []
print(f"\nОставшиеся отчёты в основной конфигурации: {remaining}")
