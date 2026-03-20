# -*- coding: utf-8 -*-
"""Restore pre-refactoring state and check DT backup logic."""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')

base = r'd:\Git\Public_Trade_Module'
ps_script = os.path.join(base, 'Документация', 'Валидация', 'deploy-config.ps1')

with open(ps_script, encoding='utf-8-sig') as f:
    lines = f.readlines()

print("=== DT/Backup related lines in deploy-config.ps1 ===")
for i, line in enumerate(lines, 1):
    l = line.strip()
    if any(k in l for k in ['DtBak', 'DtBackup', 'SkipDt', '.dt', 'Backup', 'backup',
                              'CreateDt', 'DT', 'BACKUP']):
        print(f"  {i}: {l[:160]}")

print("\n=== Parameters section ===")
for i, line in enumerate(lines, 1):
    l = line.strip()
    if 'param' in l.lower() or 'Skip' in l:
        print(f"  {i}: {l[:160]}")
    if i > 60:
        break

# Check where DT file is stored
print("\n=== DT file path references ===")
for i, line in enumerate(lines, 1):
    l = line.strip()
    if '.dt' in l.lower() or 'export' in l.lower():
        print(f"  {i}: {l[:160]}")
