# -*- coding: utf-8 -*-
"""Читаем последний УСПЕШНЫЙ лог деплоя."""
import pathlib

logs_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs")
log_files = sorted(logs_dir.glob("1c-designer-*.log"))
print(f"Всего логов: {len(log_files)}")
for log in log_files[-5:]:
    try:
        text = log.read_text(encoding="utf-8-sig", errors="replace").strip()
        status = "УСПЕШНО" if not text or "Ошибка" not in text else "ОШИБКА"
        print(f"  {log.name}: [{status}] {text[:80]!r}")
    except Exception as e:
        print(f"  {log.name}: ошибка чтения: {e}")
