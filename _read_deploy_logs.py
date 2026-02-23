# -*- coding: utf-8 -*-
"""Читаем последние 3 лога деплоя."""
import pathlib

LOGS = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs")
logs = sorted(LOGS.glob("1c-designer-*.log"), key=lambda f: f.stat().st_mtime)

print(f"Всего логов: {len(logs)}")
for log in logs[-5:]:
    size = log.stat().st_size
    txt = log.read_bytes()
    try:
        content = txt.decode("utf-8-sig")
    except:
        content = txt.decode("cp1251", errors="replace")
    content = content.strip()
    print(f"\n--- {log.name} ({size} байт) ---")
    print(content[:2000] if len(content) > 2000 else content)
