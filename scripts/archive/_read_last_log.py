# -*- coding: utf-8 -*-
"""Чтение последнего лога деплоя."""
import pathlib

logs_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs")
log_files = sorted(logs_dir.glob("1c-designer-*.log"))
if log_files:
    last = log_files[-1]
    print(f"Последний лог: {last.name}")
    try:
        text = last.read_text(encoding="utf-8-sig", errors="replace")
        print(text[:3000])
    except Exception as e:
        print(f"Ошибка чтения: {e}")
else:
    print("Логи не найдены")
