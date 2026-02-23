# -*- coding: utf-8 -*-
"""List changed files in Конфигурация (not Проверка) from git"""
import subprocess
import os

os.chdir(r"D:\Git\Public_Trade_Module")

# Use -z for NUL-separated output (avoids octal encoding)
r = subprocess.run(['git', 'diff', '--name-only', '-z', 'HEAD'], capture_output=True)
files = r.stdout.decode('utf-8').split('\0')
files = [f for f in files if f.strip()]

print(f"Total changed files: {len(files)}")
print("\n--- Конфигурация (source, NOT Проверка) ---")
config_files = [f for f in files if f.startswith('Конфигурация/') and '/Проверка/' not in f]
for f in config_files:
    print(f"  {f}")

print(f"\n--- Проверка ---")
proverka_files = [f for f in files if '/Проверка/' in f]
print(f"  Count: {len(proverka_files)}")

print(f"\n--- Other ---")
other = [f for f in files if not f.startswith('Конфигурация/')]
for f in other:
    print(f"  {f}")
