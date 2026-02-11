# -*- coding: utf-8 -*-
import pathlib
import shutil
import os

# Пути
base_config = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
test_config = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")

print("Копирование Configuration.xml и ConfigDumpInfo.xml из основной конфигурации...")

# Копировать Configuration.xml
src_config = base_config / "Configuration.xml"
dst_config = test_config / "Configuration.xml"
if src_config.exists():
    shutil.copy2(src_config, dst_config)
    print(f"  ✓ Configuration.xml скопирован")
else:
    print(f"  ✗ Configuration.xml не найден в источнике")

# Копировать ConfigDumpInfo.xml
src_dump = base_config / "ConfigDumpInfo.xml"
dst_dump = test_config / "ConfigDumpInfo.xml"
if src_dump.exists():
    shutil.copy2(src_dump, dst_dump)
    print(f"  ✓ ConfigDumpInfo.xml скопирован")
else:
    print(f"  ✗ ConfigDumpInfo.xml не найден в источнике")

# Список папок для удаления из Проверки если существуют
test_config_old = test_config / "_old_backup"
if not test_config_old.exists():
    test_config_old.mkdir(exist_ok=True)

# Резервная копия текущего ConfigDumpInfo
backup_dump = test_config_old / "ConfigDumpInfo_new.xml"
if (test_config / "ConfigDumpInfo.xml").exists():
    shutil.copy2(test_config / "ConfigDumpInfo.xml", backup_dump)
    print(f"  ✓ Резервная копия ConfigDumpInfo сохранена")

print("\nКопирование завершено!")
print(f"Примечание: Нужно вручную добавить <DataProcessor>ТестСозданиеФорм</DataProcessor> в Configuration.xml")
