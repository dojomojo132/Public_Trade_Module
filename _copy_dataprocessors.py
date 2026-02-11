# -*- coding: utf-8 -*-
import pathlib
import shutil

# Источник и назначение
source = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\DataProcessors")
target = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\DataProcessors")

# Список DataProcessor'ов для копирования (исключая ТестСозданиеФорм, который уже есть)
dataprocessors = [
    "ЗаполниеТестовойНоменклатуры",
    "ИмпортЕкспортНоменклатуры",
    "ИмпортНоменклатуры",
    "РабочееМестоКассира",
    "ТестоваяНастройкаКасс",
    "ТестовоеЗаполнениеДанных",
    "ТестовоеЗаполнениеЦен",
    "ТестовоеЗаполнениеШтрихкодов",
    "УправлениеНастройками",
]

# Создать целевую папку если её нет
target.mkdir(parents=True, exist_ok=True)

print("Копирование DataProcessor'ов...")
for dp in dataprocessors:
    source_xml = source / f"{dp}.xml"
    source_dir = source / dp
    target_xml = target / f"{dp}.xml"
    target_dir = target / dp
    
    # Копировать XML файл
    if source_xml.exists() and not target_xml.exists():
        shutil.copy2(source_xml, target_xml)
        print(f"  ✓ {dp}.xml")
    elif target_xml.exists():
        print(f"  - {dp}.xml (уже существует)")
    else:
        print(f"  ✗ {dp}.xml (не найден в источнике)")
    
    # Копировать папку с формами/модулями
    if source_dir.exists() and not target_dir.exists():
        shutil.copytree(source_dir, target_dir)
        print(f"  ✓ {dp}/ (папка)")
    elif target_dir.exists():
        print(f"  - {dp}/ (уже существует)")
    else:
        print(f"  ~ {dp}/ (папка не требуется)")

print("\nКопирование завершено!")
