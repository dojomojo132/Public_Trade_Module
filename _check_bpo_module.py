# -*- coding: utf-8 -*-
import subprocess, pathlib

r = subprocess.run(
    ['git', 'show', 'f8d6d1a:Конфигурация/Проверка/Ext/ManagedApplicationModule.bsl'],
    capture_output=True, encoding='utf-8', errors='replace',
    cwd=r'D:\Git\Public_Trade_Module'
)

print(f"Exit: {r.returncode}")
print(f"Lines: {len(r.stdout.splitlines())}")
print("Content:")
print(r.stdout)
