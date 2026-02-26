# -*- coding: utf-8 -*-
import pathlib

logs_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs")
if logs_dir.exists():
    logs = sorted(logs_dir.glob("1c-designer*.log"), key=lambda f: f.stat().st_mtime, reverse=True)
    for f in logs[:3]:
        print(f"=== {f.name} ===")
        content = f.read_text(encoding="utf-8-sig")
        print(content[:1000] if content else "[ПУСТОЙ ФАЙЛ]")
        print()
else:
    for f in sorted(pathlib.Path(r"D:\Git\Public_Trade_Module").rglob("1c-designer*.log"), key=lambda f: f.stat().st_mtime, reverse=True)[:3]:
        print(f"=== {f} ===")
        content = f.read_text(encoding="utf-8-sig")
        print(content[:1000] if content else "[ПУСТОЙ ФАЙЛ]")
        print()
