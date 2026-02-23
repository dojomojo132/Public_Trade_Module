# -*- coding: utf-8 -*-
"""
Исправляет CRLF -> LF в Configuration.xml и ConfigDumpInfo.xml.
1C LoadConfigFromFiles ожидает LF-окончания строк (как в родных dump-файлах 1С).
"""

import pathlib
import sys

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")

TARGET_FILES = [
    ROOT / "Конфигурация" / "Проверка" / "Configuration.xml",
    ROOT / "Конфигурация" / "Проверка" / "ConfigDumpInfo.xml",
    ROOT / "Конфигурация" / "Configuration.xml",
    ROOT / "Конфигурация" / "ConfigDumpInfo.xml",
]

# Дополнительно - новые файлы ТестыРМК тоже могут быть с CRLF
TESTS_DIRS = [
    ROOT / "Конфигурация" / "Проверка" / "DataProcessors" / "ТестыРМК",
    ROOT / "Конфигурация" / "DataProcessors" / "ТестыРМК",
]

def fix_file(path: pathlib.Path):
    """CRLF -> LF, сохраняю BOM."""
    data = path.read_bytes()
    if b'\r\n' not in data:
        print(f"  [SKIP] {path.name} — уже LF")
        return False
    fixed = data.replace(b'\r\n', b'\n')
    path.write_bytes(fixed)
    changed = (len(data) - len(fixed))
    print(f"  [FIX]  {path.name} | убрано {changed} CR-байт ({len(data)} -> {len(fixed)} байт)")
    return True

print("=== Исправление Configuration.xml и ConfigDumpInfo.xml ===")
for f in TARGET_FILES:
    if f.exists():
        fix_file(f)
    else:
        print(f"  [?] {f.name} не найден: {f}")

print()
print("=== Исправление ТестыРМК файлов ===")
fixes = 0
for base_dir in TESTS_DIRS:
    if not base_dir.exists():
        print(f"  [?] {base_dir} не найдена")
        continue
    for f in base_dir.rglob("*"):
        if f.is_file() and f.suffix in ('.xml', '.bsl'):
            if fix_file(f):
                fixes += 1

# Также основной xml описатель
for variant in [ROOT / "Конфигурация" / "Проверка" / "DataProcessors" / "ТестыРМК.xml",
                ROOT / "Конфигурация" / "DataProcessors" / "ТестыРМК.xml"]:
    if variant.exists():
        if fix_file(variant):
            fixes += 1

# Исправляем Форма.xml описатели
for variant in [
    ROOT / "Конфигурация" / "Проверка" / "DataProcessors" / "ТестыРМК" / "Forms" / "Форма.xml",
    ROOT / "Конфигурация" / "DataProcessors" / "ТестыРМК" / "Forms" / "Форма.xml",
]:
    if variant.exists():
        if fix_file(variant):
            fixes += 1

print(f"\nИтого ТестыРМК: {fixes} файлов исправлено")

print()
print("=== Проверка результата ===")
for f in TARGET_FILES:
    if f.exists():
        data = f.read_bytes()
        crlf = data.count(b'\r\n')
        lf_only = data.count(b'\n')
        bom = "✓" if data[:3] == b'\xef\xbb\xbf' else "✗ BOM MISSING!"
        status = "✓ LF" if crlf == 0 else f"✗ CRLF остались: {crlf}"
        print(f"  {f.name}: {status} | BOM: {bom} | {len(data)} байт")

print("\nГотово!")
