# -*- coding: utf-8 -*-
"""
Организация папки Тесты/ для 1С тестов PTM
"""
import pathlib
import shutil

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
TESTS = ROOT / "Тесты"
TEMPLATES = ROOT / "Документация" / "Тестирование" / "Шаблоны"

# Создать структуру папок
folders = [
    TESTS / "YAxUnit",
    TESTS / "Smoke",
    TESTS / "EPF",
    TESTS / "Данные",
]

print("=== Создание структуры Тесты/ ===")
for f in folders:
    f.mkdir(exist_ok=True)
    print(f"  📁 {f.relative_to(ROOT)}/")

print()

# Переместить EPF файл
epf_src = TESTS / "ТестированиеПоискаПоШтрихкоду.epf"
if epf_src.exists():
    shutil.move(str(epf_src), str(TESTS / "EPF" / epf_src.name))
    print(f"  ✓ {epf_src.name} → Тесты/EPF/")

# Переместить BSL файл тестов
bsl_src = TESTS / "ТестСериализацииНастроек.bsl"
if bsl_src.exists():
    shutil.move(str(bsl_src), str(TESTS / "YAxUnit" / bsl_src.name))
    print(f"  ✓ {bsl_src.name} → Тесты/YAxUnit/")

# Скопировать шаблоны YAxUnit в Тесты/YAxUnit/
print()
print("=== Копирование шаблонов YAxUnit ===")
for tmpl in sorted(TEMPLATES.glob("ОМ_*.bsl")):
    dst = TESTS / "YAxUnit" / tmpl.name
    if not dst.exists():
        shutil.copy2(str(tmpl), str(dst))
        print(f"  ✓ {tmpl.name} → Тесты/YAxUnit/")
    else:
        print(f"  - {tmpl.name} (уже есть)")

print()
print("=== Итог ===")
for folder in [TESTS] + folders:
    files = list(folder.glob("*.*"))
    subdirs = [d for d in folder.iterdir() if d.is_dir()]
    print(f"  {folder.relative_to(ROOT)}/: {len(files)} файлов, {len(subdirs)} папок")

print()
print("Готово!")
