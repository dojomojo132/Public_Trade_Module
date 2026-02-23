# -*- coding: utf-8 -*-
"""
Диагностика "Ошибка формата потока".
1. Сравниваем Configuration.xml (Проверка) в текущем git HEAD vs 09e34c3
2. Проверяем первые 10 байт (BOM) и последние 20 байт (конец файла)
3. Проверяем уникальность uuid в ConfigDumpInfo.xml
"""

import subprocess
import pathlib
import sys

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
PROVERKA = ROOT / "Конфигурация" / "Проверка"

def git_show(commit, path_relative):
    """Получить содержимое файла из git."""
    result = subprocess.run(
        ["git", "show", f"{commit}:{path_relative}"],
        capture_output=True,
        cwd=str(ROOT)
    )
    if result.returncode != 0:
        return None
    return result.stdout

# ==============================================================================
print("=== 1. Проверяем Configuration.xml текущий vs 09e34c3 ===")

cfg_path = PROVERKA / "Configuration.xml"
current_bytes = cfg_path.read_bytes()

# Получаем из git (используем forward slashes)
old_bytes_cfg = git_show("09e34c3", "Конфигурация/Проверка/Configuration.xml")

if old_bytes_cfg is None:
    print("  [!] Не удалось получить из git (кириллица?)")
    # Попробуем через файловый путь
    result2 = subprocess.run(
        ["git", "cat-file", "-p", "09e34c3:Конфигурация/Проверка/Configuration.xml"],
        capture_output=True, cwd=str(ROOT)
    )
    if result2.returncode == 0:
        old_bytes_cfg = result2.stdout
        print("  [OK] cat-file сработал")
    else:
        print(f"  [ERR] cat-file тоже не работает: {result2.stderr[:200]}")
else:
    print("  [OK] git show сработал")

if old_bytes_cfg is not None:
    print(f"  Старый размер: {len(old_bytes_cfg)} байт")
    print(f"  Текущий размер: {len(current_bytes)} байт")
    print(f"  Старый BOM: {old_bytes_cfg[:3].hex()}")
    print(f"  Текущий BOM: {current_bytes[:3].hex()}")
    print(f"  Старые первые 30 байт: {old_bytes_cfg[:30].hex()}")
    print(f"  Текущие первые 30 байт: {current_bytes[:30].hex()}")
    
    # Ищем отличия
    if old_bytes_cfg == current_bytes:
        print("  [==] Файлы идентичны")
    else:
        print(f"  [!=] Файлы ОТЛИЧАЮТСЯ!")
        # Найти первое отличие
        for i, (a, b) in enumerate(zip(old_bytes_cfg, current_bytes)):
            if a != b:
                ctx_start = max(0, i-20)
                print(f"  Первое отличие на байте {i}:")
                print(f"    Старый context: {old_bytes_cfg[ctx_start:i+20].hex()}")
                print(f"    Новый context:  {current_bytes[ctx_start:i+20].hex()}")
                break

# ==============================================================================
print()
print("=== 2. Проверяем наличие \r\n в Configuration.xml ===")
crlf_count = current_bytes.count(b'\r\n')
lf_count = current_bytes.count(b'\n')
cr_only = current_bytes.count(b'\r') - crlf_count
print(f"  CRLF: {crlf_count}, LF-only: {lf_count - crlf_count}, CR-only: {cr_only}")
if old_bytes_cfg:
    old_crlf = old_bytes_cfg.count(b'\r\n')
    old_lf = old_bytes_cfg.count(b'\n')
    print(f"  [git] CRLF: {old_crlf}, LF-only: {old_lf - old_crlf}")

# ==============================================================================
print()
print("=== 3. Проверяем ConfigDumpInfo.xml ===")

cdi_path = PROVERKA / "ConfigDumpInfo.xml"
cdi_bytes = cdi_path.read_bytes()
print(f"  Текущий размер: {len(cdi_bytes)} байт")
print(f"  BOM: {cdi_bytes[:3].hex()}")
cdi_crlf = cdi_bytes.count(b'\r\n')
cdi_lf = cdi_bytes.count(b'\n')
print(f"  CRLF: {cdi_crlf}, LF-only: {cdi_lf - cdi_crlf}")

old_bytes_cdi = git_show("09e34c3", "Конфигурация/Проверка/ConfigDumpInfo.xml")
if old_bytes_cdi:
    print(f"  [git 09e34c3] размер: {len(old_bytes_cdi)} байт")
    print(f"  BOM git: {old_bytes_cdi[:3].hex()}")
    old_cdi_crlf = old_bytes_cdi.count(b'\r\n')
    old_cdi_lf = old_bytes_cdi.count(b'\n')
    print(f"  [git] CRLF: {old_cdi_crlf}, LF-only: {old_cdi_lf - old_cdi_crlf}")
    if old_bytes_cdi == cdi_bytes:
        print("  [==] CDI файлы идентичны")
    else:
        print(f"  [!=] CDI файлы ОТЛИЧАЮТСЯ!")
        for i, (a, b) in enumerate(zip(old_bytes_cdi, cdi_bytes)):
            if a != b:
                ctx_start = max(0, i-20)
                print(f"  Первое CDI отличие на байте {i}:")
                print(f"    Старый: {old_bytes_cdi[ctx_start:i+20].hex()}")
                print(f"    Новый:  {cdi_bytes[ctx_start:i+20].hex()}")
                break
        # Разница в размере
        if len(cdi_bytes) > len(old_bytes_cdi):
            added = len(cdi_bytes) - len(old_bytes_cdi)
            print(f"  Добавлено {added} байт")
else:
    print("  [!] Не удалось получить CDI из git")

print()
print("=== 4. Проверяем все XML файлы в Проверка/ на BOM ===")
ok_count = 0
no_bom = []
for xml_file in PROVERKA.rglob("*.xml"):
    b = xml_file.read_bytes()
    if len(b) < 3 or b[:3] != b'\xef\xbb\xbf':
        no_bom.append(xml_file.relative_to(PROVERKA))

if no_bom:
    print(f"  Файлы БЕЗ BOM ({len(no_bom)}):")
    for f in no_bom[:20]:
        print(f"    {f}")
    if len(no_bom) > 20:
        print(f"    ... и ещё {len(no_bom) - 20}")
else:
    # Считаем
    for xml_file in PROVERKA.rglob("*.xml"):
        ok_count += 1
    print(f"  Все {ok_count} XML файлов имеют BOM ✓")

print()
print("=== 5. Проверяем BSL файлы в Проверка/ на BOM ===")
bsl_no_bom = []
for bsl_file in PROVERKA.rglob("*.bsl"):
    b = bsl_file.read_bytes()
    if len(b) < 3 or b[:3] != b'\xef\xbb\xbf':
        bsl_no_bom.append(bsl_file.relative_to(PROVERKA))

if bsl_no_bom:
    print(f"  BSL файлы БЕЗ BOM ({len(bsl_no_bom)}):")
    for f in bsl_no_bom[:30]:
        print(f"    {f}")
    if len(bsl_no_bom) > 30:
        print(f"    ... и ещё {len(bsl_no_bom) - 30}")
else:
    bsl_count = sum(1 for _ in PROVERKA.rglob("*.bsl"))
    print(f"  Все {bsl_count} BSL файлов имеют BOM ✓")

print()
print("Диагностика завершена.")
