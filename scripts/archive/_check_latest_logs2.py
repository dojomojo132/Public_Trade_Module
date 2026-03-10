# -*- coding: utf-8 -*-
import pathlib
log_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs")
logs = sorted(log_dir.glob("1c-designer-*"), key=lambda p: p.stat().st_mtime, reverse=True)
for log_file in logs[:5]:
    print(f"--- {log_file.name} ({log_file.stat().st_size}B) [{log_file.stat().st_mtime}] ---")
    content = log_file.read_text(encoding='utf-8-sig').strip()
    print(content[:300] if content else "[EMPTY - OK!]")
    print()
