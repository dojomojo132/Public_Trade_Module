# -*- coding: utf-8 -*-
import pathlib
import shutil

# Сохранить мой новый ТестСозданиеФорм перед сбросом
test_config = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")
backup_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\_test_content_backup")

# Создать папку резервной копии
backup_dir.mkdir(exist_ok=True)

# Сохранить ТестСозданиеФорм
test_dp = test_config / "DataProcessors" / "ТестСозданиеФорм"
test_xml = test_config / "DataProcessors" / "ТестСозданиеФорм.xml"

if test_dp.exists():
    backup_dp = backup_dir / "ТестСозданиеФорм"
    if backup_dp.exists():
        shutil.rmtree(backup_dp)
    shutil.copytree(test_dp, backup_dp)
    print("✓ ТестСозданиеФорм папка сохранена")

if test_xml.exists():
    shutil.copy2(test_xml, backup_dir / "ТестСозданиеФорм.xml")
    print("✓ ТестСозданиеФорм.xml сохранен")

# Также сохраним Configuration.xml и ConfigDumpInfo.xml с моей добавкой
config_xml = test_config / "Configuration.xml"
config_dump = test_config / "ConfigDumpInfo.xml"

if config_xml.exists():
    shutil.copy2(config_xml, backup_dir / "Configuration_with_test.xml")
    print("✓ Configuration.xml с ТестСозданиеФорм сохранен")

if config_dump.exists():
    shutil.copy2(config_dump, backup_dir / "ConfigDumpInfo_with_test.xml")
    print("✓ ConfigDumpInfo.xml с ТестСозданиеФорм сохранен")

print("\nРезервные копии сохранены в: D:\\Git\\Public_Trade_Module\\_test_content_backup\\")
