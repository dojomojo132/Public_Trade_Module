# -*- coding: utf-8 -*-
import pathlib

logs_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs")
logs = sorted(logs_dir.glob("1c-designer-*.log"), key=lambda x: x.stat().st_mtime, reverse=True)

for log in logs[:3]:
    size = log.stat().st_size
    print(f"--- {log.name} ({size} B) ---")
    if size == 0:
        print("[EMPTY]")
    else:
        for enc in ["utf-16", "utf-8", "cp1251"]:
            try:
                text = log.read_text(encoding=enc, errors="replace")
                print(text[:3000])
                break
            except Exception as e:
                continue
    print()
