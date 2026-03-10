# -*- coding: utf-8 -*-
import pathlib
import os

logs_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\logs")
if logs_dir.exists():
    files = sorted(logs_dir.iterdir(), key=lambda f: f.stat().st_mtime, reverse=True)
    for f in files[:5]:
        print(f"{f.name} ({f.stat().st_size} bytes)")
    if files:
        latest = files[0]
        print(f"\n--- {latest.name} ---")
        text = latest.read_text(encoding='utf-8', errors='replace')
        print(text[-3000:] if len(text) > 3000 else text)
else:
    print("logs/ not found")
