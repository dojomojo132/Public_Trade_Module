# -*- coding: utf-8 -*-
import pathlib
log_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs")
logs = sorted(log_dir.glob("1c-designer-20260226-1814*"), key=lambda p: p.stat().st_mtime, reverse=True)
for log_file in logs[:3]:
    print(f"--- {log_file.name} ({log_file.stat().st_size}B) ---")
    content = log_file.read_text(encoding='utf-8-sig').strip()
    print(content[:500] if content else "[EMPTY - OK!]")
