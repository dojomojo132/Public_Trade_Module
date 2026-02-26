# -*- coding: utf-8 -*-
"""Read ALL recent deploy logs"""
import pathlib

log_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs")
logs = sorted(log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)

for log_file in logs[:10]:
    size = log_file.stat().st_size
    content = log_file.read_text(encoding='utf-8-sig').strip()
    print(f"\n--- {log_file.name} ({size}B) ---")
    print(content[:500] if content else "[EMPTY]")
