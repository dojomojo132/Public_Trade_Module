# -*- coding: utf-8 -*-
import pathlib
import shutil

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
check = base / "Проверка"

# Файлы для копирования из основной папки в Проверка
files_to_copy = [
    # Перечисление ВидыКасс
    ("Enums/ВидыКасс.xml", "Enums/ВидыКасс.xml"),
    # Справочник Кассы (обновленный)
    ("Catalogs/Кассы.xml", "Catalogs/Кассы.xml"),
    # Отчет ПродажиПоСчетам
    ("Reports/ПродажиПоСчетам.xml", "Reports/ПродажиПоСчетам.xml"),
    ("Reports/ПродажиПоСчетам/Templates/ОсновнаяСхемаКомпоновкиДанных.xml", 
     "Reports/ПродажиПоСчетам/Templates/ОсновнаяСхемаКомпоновкиДанных.xml"),
    ("Reports/ПродажиПоСчетам/Templates/ОсновнаяСхемаКомпоновкиДанных/Ext/Template.xml",
     "Reports/ПродажиПоСчетам/Templates/ОсновнаяСхемаКомпоновкиДанных/Ext/Template.xml"),
    # Модуль формы ЧекККМ (обновленный)
    ("Documents/ЧекККМ/Forms/ФормаДокумента/Ext/Form/Module.bsl",
     "Documents/ЧекККМ/Forms/ФормаДокумента/Ext/Form/Module.bsl"),
    # Configuration.xml и ConfigDumpInfo.xml
    ("Configuration.xml", "Configuration.xml"),
    ("ConfigDumpInfo.xml", "ConfigDumpInfo.xml"),
    # Подсистемы
    ("Subsystems/Финансы.xml", "Subsystems/Финансы.xml"),
    ("Subsystems/Торговля.xml", "Subsystems/Торговля.xml"),
    ("Subsystems/Все.xml", "Subsystems/Все.xml"),
]

print("Копирование файлов в Проверка...")
for src_rel, dst_rel in files_to_copy:
    src = base / src_rel
    dst = check / dst_rel
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"  ✓ {src_rel}")
    else:
        print(f"  ✗ {src_rel} (НЕ НАЙДЕН!)")

print("\nГотово!")
