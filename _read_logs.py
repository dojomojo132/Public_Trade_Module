# -*- coding: utf-8 -*-
import pathlib

log_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs")
logs = sorted(log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)

for log_file in logs[:3]:
    print(f"\n=== {log_file.name} ({log_file.stat().st_size} bytes) ===")
    content = log_file.read_text(encoding='utf-8-sig')
    print(content[:2000])
    print("---")
