# -*- coding: utf-8 -*-
"""Найти нестандартные файлы в Проверка/."""
import pathlib

PROVERKA = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")

# Ожидаемые расширения файлов в конфиг-директории
EXPECTED_EXTS = {'.xml', '.bsl', '.mxl', '.efd', '.bin', '.gif', '.png', '.ico', '', '.html', '.json', '.epf', '.cf', '.cfe', '.dt'}

print("=== Нестандартные файлы в Проверка/ ===")
unusual = []
for f in PROVERKA.rglob("*"):
    if f.is_file():
        # Python-скрипты или .txt файлы не должны быть здесь
        if f.suffix not in EXPECTED_EXTS or f.suffix in {'.py', '.txt', '.log'}:
            unusual.append(f)

for f in unusual:
    print(f"  {f.relative_to(PROVERKA)}")

if not unusual:
    print("  (нет нестандартных файлов)")

print()
print("=== Файлы в корне Проверка/ ===")
for f in sorted(PROVERKA.iterdir()):
    if f.is_file():
        print(f"  {f.name} ({f.stat().st_size} байт)")

print()
print("=== Количество .xml файлов в DataProcessors/ ===")
dp = PROVERKA / "DataProcessors"
xml_files = list(dp.rglob("*.xml"))
print(f"  {len(xml_files)} XML файлов")
# Показать корневые XML файлы DataProcessors
for f in sorted(dp.glob("*.xml")):
    print(f"  {f.name}")
