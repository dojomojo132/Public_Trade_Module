# -*- coding: utf-8 -*-
import pathlib
import glob

log_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs")
if log_dir.exists():
    logs = sorted(log_dir.glob("*.log"), key=lambda f: f.stat().st_mtime, reverse=True)
    for log in logs[:3]:
        print(f"=== {log.name} ===")
        content = log.read_text(encoding="utf-8-sig")
        lines = content.strip().split("\n")
        for line in lines[-40:]:
            print(line)
        print()
else:
    print(f"Log dir not found: {log_dir}")
