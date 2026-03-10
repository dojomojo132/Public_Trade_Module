# -*- coding: utf-8 -*-
import pathlib

log_dir = pathlib.Path(r'D:\Git\Public_Trade_Module\Документация\Валидация\logs')
logs = sorted(log_dir.glob('*.log'), key=lambda f: f.stat().st_mtime, reverse=True)[:5]
for f in logs:
    print(f.name, f.stat().st_size, 'bytes')
    try:
        content = f.read_bytes()
        text = content.lstrip(b'\xef\xbb\xbf').decode('utf-8', errors='replace')
        if text.strip():
            print(text[:800])
    except Exception as e:
        print(f'Error: {e}')
    print('---')
