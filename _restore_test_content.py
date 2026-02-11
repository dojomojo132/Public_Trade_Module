# -*- coding: utf-8 -*-
import pathlib
import shutil

backup_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\_test_content_backup")
test_config = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")
dp_folder = test_config / "DataProcessors"

print("Восстановление ТестСозданиеФорм из резервной копии...")

# Восстановить папку
if (backup_dir / "ТестСозданиеФорм").exists():
    target_dp = dp_folder / "ТестСозданиеФорм"
    if target_dp.exists():
        shutil.rmtree(target_dp)
    shutil.copytree(backup_dir / "ТестСозданиеФорм", target_dp)
    print("✓ Папка ТестСозданиеФорм восстановлена")

# Восстановить XML файл
if (backup_dir / "ТестСозданиеФорм.xml").exists():
    target_xml = dp_folder / "ТестСозданиеФорм.xml"
    if target_xml.exists():
        target_xml.unlink()
    shutil.copy2(backup_dir / "ТестСозданиеФорм.xml", target_xml)
    print("✓ ТестСозданиеФорм.xml восстановлен")

# Восстановить Configuration.xml с мой добавкой
if (backup_dir / "Configuration_with_test.xml").exists():
    target_config = test_config / "Configuration.xml"
    if target_config.exists():
        target_config.unlink()
    shutil.copy2(backup_dir / "Configuration_with_test.xml", target_config)
    print("✓ Configuration.xml с ТестСозданиеФорм восстановлен")

# Восстановить ConfigDumpInfo.xml с мой добавкой
if (backup_dir / "ConfigDumpInfo_with_test.xml").exists():
    target_dump = test_config / "ConfigDumpInfo.xml"
    if target_dump.exists():
        target_dump.unlink()
    shutil.copy2(backup_dir / "ConfigDumpInfo_with_test.xml", target_dump)
    print("✓ ConfigDumpInfo.xml с ТестСозданиеФорм восстановлен")

print("\nВосстановление завершено!")
print("Папка Проверка готова к деплою с новым ТестСозданиеФорм")
