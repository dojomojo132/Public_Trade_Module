# -*- coding: utf-8 -*-
"""Читать лог 165252 (предположительно LoadConfig)."""
import pathlib

logs_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs")

# Прочитать логи нужных временных меток
targets = ["1c-designer-20260223-165252.log", "1c-designer-20260223-160920.log", "1c-designer-20260223-232639.log"]
for t in targets:
    lf = logs_dir / t
    if lf.exists():
        text = lf.read_text(encoding="utf-8-sig", errors="replace").strip()
        print(f"=== {t} ({lf.stat().st_size} bytes) ===")
        print(text[:500])
        print()
    else:
        print(f"НЕТ: {t}")
