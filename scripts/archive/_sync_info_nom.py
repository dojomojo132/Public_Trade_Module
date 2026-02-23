# -*- coding: utf-8 -*-
"""Sync new DataProcessor to Проверка folder and fix orphan files"""
import pathlib
import shutil
import re

BASE = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
SRC = BASE
DST = BASE / "Проверка"

print("=" * 60)
print("  СИНХРОНИЗАЦИЯ Конфигурация → Конфигурация/Проверка")
print("=" * 60)

# 1. Delete orphan files from Проверка
print("\n--- 1. Удаление орфан-файлов из Проверка ---")
orphans_files = [
    DST / "Catalogs" / "ДенежныеСтатьи.xml",
    DST / "CommonModules" / "ЛогированиеОшибок.xml",
]
orphans_dirs = [
    DST / "Catalogs" / "ДенежныеСтатьи",
    DST / "CommonModules" / "ЛогированиеОшибок",
]
for f in orphans_files:
    if f.exists():
        f.unlink()
        print(f"  OK Удален: {f.name}")
    else:
        print(f"  - {f.name} (не найден)")
for d in orphans_dirs:
    if d.exists():
        shutil.rmtree(d)
        print(f"  OK Удалена папка: {d.name}/")

# 2. Delete orphan report from Проверка (already done but ensure)
print("\n--- 2. Проверка удаления отчёта СправочникНоменклатуры ---")
rep_xml = DST / "Reports" / "СправочникНоменклатуры.xml"
rep_dir = DST / "Reports" / "СправочникНоменклатуры"
if rep_xml.exists():
    rep_xml.unlink()
    print("  OK Удален СправочникНоменклатуры.xml")
else:
    print("  - СправочникНоменклатуры.xml уже удален")
if rep_dir.exists():
    shutil.rmtree(rep_dir)
    print("  OK Удалена папка СправочникНоменклатуры/")
else:
    print("  - Папка СправочникНоменклатуры/ уже удалена")

# 3. Copy new DataProcessor to Проверка
print("\n--- 3. Копирование ИнформацияНоменклатуры в Проверка ---")
src_xml = SRC / "DataProcessors" / "ИнформацияНоменклатуры.xml"
dst_xml = DST / "DataProcessors" / "ИнформацияНоменклатуры.xml"
src_dir = SRC / "DataProcessors" / "ИнформацияНоменклатуры"
dst_dir = DST / "DataProcessors" / "ИнформацияНоменклатуры"

if src_xml.exists():
    shutil.copy2(src_xml, dst_xml)
    print(f"  OK Скопирован: ИнформацияНоменклатуры.xml")
else:
    print(f"  ОШИБКА: исходный файл не найден!")

if src_dir.exists():
    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    shutil.copytree(src_dir, dst_dir)
    print(f"  OK Скопирована папка: ИнформацияНоменклатуры/")
else:
    print(f"  ОШИБКА: исходная папка не найдена!")

# 4. Update Проверка/Configuration.xml
print("\n--- 4. Обновление Configuration.xml в Проверка ---")
config_path = DST / "Configuration.xml"
config = config_path.read_text(encoding="utf-8")

# Add new DataProcessor
if "ИнформацияНоменклатуры" not in config:
    config = config.replace(
        "\t\t\t<DataProcessor>ИмпортНоменклатуры</DataProcessor>",
        "\t\t\t<DataProcessor>ИмпортНоменклатуры</DataProcessor>\n\t\t\t<DataProcessor>ИнформацияНоменклатуры</DataProcessor>"
    )
    print("  OK Добавлен DataProcessor.ИнформацияНоменклатуры")
else:
    print("  - DataProcessor.ИнформацияНоменклатуры уже есть")

# Remove Report.СправочникНоменклатуры if present
if "<Report>СправочникНоменклатуры</Report>" in config:
    config = config.replace("\t\t\t<Report>СправочникНоменклатуры</Report>\n", "")
    print("  OK Удален Report.СправочникНоменклатуры")

config_path.write_text(config, encoding="utf-8")

# 5. Update Проверка/ConfigDumpInfo.xml
print("\n--- 5. Обновление ConfigDumpInfo.xml в Проверка ---")
cdi_path = DST / "ConfigDumpInfo.xml"
cdi = cdi_path.read_text(encoding="utf-8")

# Remove any Report.СправочникНоменклатуры entries
cdi = re.sub(r'\s*<Metadata name="Report\.СправочникНоменклатуры"[^>]*/>', '', cdi)
cdi = re.sub(
    r'\s*<Metadata name="Report\.СправочникНоменклатуры"[^>]*>\s*'
    r'(?:<Metadata name="Report\.СправочникНоменклатуры\.[^/]*/>[\s]*)*'
    r'</Metadata>',
    '', cdi
)

# Add DataProcessor.ИнформацияНоменклатуры entries
if "DataProcessor.ИнформацияНоменклатуры" not in cdi:
    new_cdi_block = '''		<Metadata name="DataProcessor.ИнформацияНоменклатуры" id="a1b2c3d4-e5f6-4789-abcd-ef0123456789" configVersion="7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d00000000">
			<Metadata name="DataProcessor.ИнформацияНоменклатуры.TabularSection.Товары" id="f6a7b8c9-d0e1-4234-f012-345678901234"/>
			<Metadata name="DataProcessor.ИнформацияНоменклатуры.TabularSection.Товары.Attribute.Артикул" id="55e6f7a8-b9c0-4312-def0-123456789012"/>
			<Metadata name="DataProcessor.ИнформацияНоменклатуры.TabularSection.Товары.Attribute.Наименование" id="66f7a8b9-c0d1-4423-ef01-234567890123"/>
			<Metadata name="DataProcessor.ИнформацияНоменклатуры.TabularSection.Товары.Attribute.ЕдиницаИзмерения" id="77a8b9c0-d1e2-4534-f012-345678901234"/>
			<Metadata name="DataProcessor.ИнформацияНоменклатуры.TabularSection.Товары.Attribute.Цена" id="88b9c0d1-e2f3-4645-0123-456789012345"/>
			<Metadata name="DataProcessor.ИнформацияНоменклатуры.TabularSection.Товары.Attribute.Остаток" id="99c0d1e2-f3a4-4756-1234-567890123456"/>
			<Metadata name="DataProcessor.ИнформацияНоменклатуры.TabularSection.Товары.Attribute.ШтрихКод" id="aad1e2f3-a4b5-4867-2345-678901234567"/>
		</Metadata>
		<Metadata name="DataProcessor.ИнформацияНоменклатуры.Form.Форма" id="bbe2f3a4-b5c6-4978-3456-789012345678" configVersion="8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e00000000"/>
		<Metadata name="DataProcessor.ИнформацияНоменклатуры.Form.Форма.Form" id="bbe2f3a4-b5c6-4978-3456-789012345678.0" configVersion="9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f00000000"/>
'''
    # Insert before DataProcessor.ТестовоеЗаполнениеДанных
    anchor = '<Metadata name="DataProcessor.ТестовоеЗаполнениеДанных"'
    cdi = cdi.replace('\t\t' + anchor, new_cdi_block + '\t\t' + anchor)
    print("  OK Добавлен DataProcessor.ИнформацияНоменклатуры в CDI")
else:
    print("  - DataProcessor.ИнформацияНоменклатуры уже в CDI")

# Remove Catalog.ДенежныеСтатьи and CommonModule.ЛогированиеОшибок from CDI
cdi = re.sub(r'\s*<Metadata name="Catalog\.ДенежныеСтатьи"[^/]*/>', '', cdi)
cdi = re.sub(
    r'\s*<Metadata name="Catalog\.ДенежныеСтатьи"[^>]*>[\s\S]*?</Metadata>',
    '', cdi
)
cdi = re.sub(r'\s*<Metadata name="CommonModule\.ЛогированиеОшибок"[^/]*/>', '', cdi)
cdi = re.sub(
    r'\s*<Metadata name="CommonModule\.ЛогированиеОшибок"[^>]*>[\s\S]*?</Metadata>',
    '', cdi
)

cdi_path.write_text(cdi, encoding="utf-8")

# 6. Update Проверка/Subsystems/Склад.xml
print("\n--- 6. Обновление Subsystems/Склад.xml в Проверка ---")
sub_path = DST / "Subsystems" / "Склад.xml"
sub = sub_path.read_text(encoding="utf-8")

# Remove Report.СправочникНоменклатуры from subsystem
sub = re.sub(r'\s*<xr:Item[^>]*>Report\.СправочникНоменклатуры</xr:Item>', '', sub)

# Add DataProcessor.ИнформацияНоменклатуры
if "DataProcessor.ИнформацияНоменклатуры" not in sub:
    sub = sub.replace(
        '<xr:Item xsi:type="xr:MDObjectRef">Report.Продажи</xr:Item>',
        '<xr:Item xsi:type="xr:MDObjectRef">Report.Продажи</xr:Item>\n\t\t\t\t<xr:Item xsi:type="xr:MDObjectRef">DataProcessor.ИнформацияНоменклатуры</xr:Item>'
    )
    print("  OK Добавлен DataProcessor.ИнформацияНоменклатуры в подсистему Склад")
else:
    print("  - Уже в подсистеме")

sub_path.write_text(sub, encoding="utf-8")

print("\n" + "=" * 60)
print("  СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА")
print("=" * 60)
