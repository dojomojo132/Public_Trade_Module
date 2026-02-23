# -*- coding: utf-8 -*-
import pathlib
import shutil
import os

base_config = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
test_config = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")

# Папки конфигурации (кроме Проверка)
folders = [
    "AccumulationRegisters", "Catalogs", "CommonModules", "CommonPictures",
    "CommonTemplates", "Constants", "DataProcessors", "Documents", "Enums",
    "Ext", "InformationRegisters", "Languages", "Reports", "Roles",
    "StyleItems", "Styles", "Subsystems"
]

print("Синхронизация конфигурации в папку Проверка...")
print(f"Источник: {base_config}")
print(f"Назначение: {test_config}\n")

# Сохранить мой новый ТестСозданиеФорм перед синхронизацией
new_dataprocessor = test_config / "DataProcessors" / "ТестСозданиеФорм"
new_dataprocessor_xml = test_config / "DataProcessors" / "ТестСозданиеФорм.xml"

backup_dir = test_config.parent / "_test_backup"
backup_dir.mkdir(exist_ok=True)

if new_dataprocessor.exists() or new_dataprocessor_xml.exists():
    print("Сохранение ТестСозданиеФорм в резервную копию...")
    backup_test_dp = backup_dir / "ТестСозданиеФорм"
    if backup_test_dp.exists():
        shutil.rmtree(backup_test_dp)
    if new_dataprocessor.exists():
        shutil.copytree(new_dataprocessor, backup_test_dp)
    if new_dataprocessor_xml.exists():
        shutil.copy2(new_dataprocessor_xml, backup_dir / "ТестСозданиеФорм.xml")
    print("  ✓ ТестСозданиеФорм сохранен в резервную копию\n")

# Копировать все папки из основной конфигурации
for folder_name in folders:
    src_folder = base_config / folder_name
    dst_folder = test_config / folder_name
    
    if not src_folder.exists():
        continue
    
    # Удалить текущую папку если существует
    if dst_folder.exists():
        shutil.rmtree(dst_folder)
    
    # Скопировать новую папку
    try:
        shutil.copytree(src_folder, dst_folder)
        print(f"  ✓ {folder_name}/ - скопирована")
    except Exception as e:
        print(f"  ✗ {folder_name}/ - ошибка: {e}")

# Копировать XML файлы (Configuration.xml, ConfigDumpInfo.xml)
for filename in ["Configuration.xml", "ConfigDumpInfo.xml"]:
    src_file = base_config / filename
    dst_file = test_config / filename
    if src_file.exists():
        shutil.copy2(src_file, dst_file)
        print(f"  ✓ {filename} - скопирован")

# Восстановить мой новый ТестСозданиеФорм
if (backup_dir / "ТестСозданиеФорм").exists() or (backup_dir / "ТестСозданиеФорм.xml").exists():
    print("\nВосстановление ТестСозданиеФорм...")
    test_dp_folder = test_config / "DataProcessors" / "ТестСозданиеФорм"
    test_dp_xml = test_config / "DataProcessors" / "ТестСозданиеФорм.xml"
    
    backup_test_dp = backup_dir / "ТестСозданиеФорм"
    if backup_test_dp.exists():
        if test_dp_folder.exists():
            shutil.rmtree(test_dp_folder)
        shutil.copytree(backup_test_dp, test_dp_folder)
        print("  ✓ ТестСозданиеФорм папка восстановлена")
    
    backup_test_xml = backup_dir / "ТестСозданиеФорм.xml"
    if backup_test_xml.exists():
        if test_dp_xml.exists():
            test_dp_xml.unlink()
        shutil.copy2(backup_test_xml, test_dp_xml)
        print("  ✓ ТестСозданиеФорм.xml восстановлен")

print("\nСинхронизация завершена!")
print("ВАЖНО: Нужно вручную добавить:")
print("  1. <DataProcessor>ТестСозданиеФорм</DataProcessor> в Configuration.xml")
print("  2. Записи для ТестСозданиеФорм в ConfigDumpInfo.xml")
