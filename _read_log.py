# -*- coding: utf-8 -*-
import pathlib, glob

log_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs")
if not log_dir.exists():
    print(f"Папка не найдена: {log_dir}")
else:
    logs = sorted(log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not logs:
        print("Нет логов")
    else:
        for log in logs[:3]:
            print(f"\n=== {log.name} ({log.stat().st_size} bytes) ===")
            content = log.read_text(encoding='utf-8-sig', errors='replace')
            print(content[:3000] if content else "(пусто)")
