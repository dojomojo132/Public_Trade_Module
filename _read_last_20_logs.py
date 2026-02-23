# -*- coding: utf-8 -*-
"""Найти последний успешный LoadConfigFromFiles лог."""
import pathlib

logs_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs")
log_files = sorted(logs_dir.glob("1c-designer-*.log"))
print(f"Всего логов: {len(log_files)}")

# Посмотреть последние 20
for log in log_files[-20:]:
    try:
        text = log.read_text(encoding="utf-8-sig", errors="replace").strip()
        # Определяем тип операции
        if "Выгрузка информационной базы" in text:
            op = "DumpIB"
        elif "Обработка структуры" in text or "Обновление" in text:
            op = "UpdateDB"
        elif "Загрузка" in text or "Ошибка формата" in text:
            op = "LoadConfig"
        else:
            op = "?"
        status = "УСПЕШНО" if not text or "Ошибка" not in text else "ОШИБКА"
        print(f"  [{log.stem[-15:]}] [{op}] [{status}] {text[:80]!r}")
    except Exception as e:
        print(f"  {log.name}: ошибка: {e}")
