# -*- coding: utf-8 -*-
"""Read latest 1C designer logs"""
import os
import glob

log_dir = r'D:\Git\Public_Trade_Module\Документация\Валидация\logs'

print(f'Log dir exists: {os.path.exists(log_dir)}')

if not os.path.exists(log_dir):
    # Try alternative
    log_dir2 = r'D:\Git\Public_Trade_Module\logs'
    print(f'Checking: {log_dir2}')
else:
    # Find latest designer logs
    files = []
    for f in os.listdir(log_dir):
        if f.startswith('1c-designer'):
            fp = os.path.join(log_dir, f)
            files.append((os.path.getmtime(fp), f, fp))
    files.sort(reverse=True)
    print(f'Latest designer logs:')
    for mtime, name, fp in files[:5]:
        from datetime import datetime
        dt = datetime.fromtimestamp(mtime)
        print(f'  {dt:%Y-%m-%d %H:%M:%S} {name}')
    if files:
        latest_fp = files[0][2]
        print(f'\n=== Reading {files[0][1]} ===')
        try:
            with open(latest_fp, 'r', encoding='utf-8-sig') as f:
                content = f.read()
        except:
            with open(latest_fp, 'r', encoding='cp1251') as f:
                content = f.read()
        print(content[:3000])
