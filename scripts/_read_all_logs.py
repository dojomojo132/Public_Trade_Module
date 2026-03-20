# -*- coding: utf-8 -*-
"""Read all latest 1C designer logs"""
import os

log_dir = r'D:\Git\Public_Trade_Module\Документация\Валидация\logs'

# Read designer logs for both load and update
target_logs = [
    '1c-designer-20260320-231207.log',  # LoadConfig
    '1c-designer-20260320-231216.log',  # UpdateDB
    '1c-designer-20260320-225934.log',  # Previous attempt
    '1c-designer-20260320-225932.log',  # Previous attempt
]

for logname in target_logs:
    fp = os.path.join(log_dir, logname)
    if os.path.exists(fp):
        sz = os.path.getsize(fp)
        print(f'\n=== {logname} (size={sz}) ===')
        try:
            with open(fp, 'r', encoding='utf-8-sig') as f:
                content = f.read()
        except:
            try:
                with open(fp, 'r', encoding='utf-16') as f:
                    content = f.read()
            except:
                with open(fp, 'rb') as f:
                    raw = f.read()
                print(f'Raw bytes (first 200): {raw[:200]}')
                content = None
        if content:
            print(content[:5000])
    else:
        print(f'\n=== {logname}: NOT FOUND ===')
