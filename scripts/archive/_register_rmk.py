# -*- coding: utf-8 -*-
"""
Re-register DataProcessor.Анл_РабочееМестоКассира in extension metadata.
The DataProcessor files already exist on disk (from Dump + fix).
This script only updates: Configuration.xml, ConfigDumpInfo.xml, Subsystem.
Also ensures Form.xml has the correct type reference.
"""
import os
import re
import uuid

EXT_CFG = r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Analytics"
NEW_NAME = "Анл_РабочееМестоКассира"

# ── 1. Read UUIDs from existing DataProcessor XML ──
print("=== 1. Чтение UUID из существующих файлов ===")
dp_xml_path = os.path.join(EXT_CFG, "DataProcessors", f"{NEW_NAME}.xml")
with open(dp_xml_path, "r", encoding="utf-8-sig") as f:
    dp_xml = f.read()

# Extract main DP UUID
dp_uuid = re.search(r'<DataProcessor uuid="([^"]+)"', dp_xml).group(1)
print(f"  DataProcessor UUID: {dp_uuid}")

# Extract all attribute UUIDs
attr_uuids = {}
# Regular attributes
for m in re.finditer(r'<Attribute uuid="([^"]+)">\s*<Properties>\s*<Name>(\w+)</Name>', dp_xml):
    uid, name = m.group(1), m.group(2)
    # Determine if it's a TS attribute (inside TabularSection)
    pos = m.start()
    if '<TabularSection' in dp_xml[max(0,pos-2000):pos]:
        # Check if we're inside a TabularSection block
        ts_start = dp_xml.rfind('<TabularSection', 0, pos)
        ts_end = dp_xml.find('</TabularSection>', pos)
        if ts_start != -1 and ts_end != -1:
            ts_name = re.search(r'<Name>(\w+)</Name>', dp_xml[ts_start:pos]).group(1)
            attr_uuids[f"TabularSection.{ts_name}.Attribute.{name}"] = uid
            continue
    attr_uuids[f"Attribute.{name}"] = uid

# Tabular section UUID
ts_match = re.search(r'<TabularSection uuid="([^"]+)">\s*<InternalInfo>.*?<Properties>\s*<Name>(\w+)</Name>', dp_xml, re.DOTALL)
if ts_match:
    ts_uuid, ts_name = ts_match.group(1), ts_match.group(2)
    attr_uuids[f"TabularSection.{ts_name}"] = ts_uuid

# Form UUID
form_xml_path = os.path.join(EXT_CFG, "DataProcessors", NEW_NAME, "Forms", "Форма.xml")
with open(form_xml_path, "r", encoding="utf-8-sig") as f:
    form_meta = f.read()
form_uuid = re.search(r'<Form uuid="([^"]+)"', form_meta).group(1)
attr_uuids["Form.Форма"] = form_uuid

for k, v in sorted(attr_uuids.items()):
    print(f"  {k}: {v}")

# ── 2. Fix Form.xml type reference ──
print("\n=== 2. Проверка типа в Form.xml ===")
form_desc_path = os.path.join(EXT_CFG, "DataProcessors", NEW_NAME, "Forms", "Форма", "Ext", "Form.xml")
with open(form_desc_path, "r", encoding="utf-8-sig") as f:
    form_desc = f.read()

old_type = "DataProcessorObject.РабочееМестоКассира"
new_type = f"DataProcessorObject.{NEW_NAME}"
if old_type in form_desc:
    form_desc = form_desc.replace(old_type, new_type)
    with open(form_desc_path, "w", encoding="utf-8-sig") as f:
        f.write(form_desc)
    print(f"  Заменено: {old_type} → {new_type}")
elif new_type in form_desc:
    print(f"  Уже исправлен: {new_type}")
else:
    print(f"  ⚠️ Тип не найден!")

# ── 3. Update Configuration.xml ──
print("\n=== 3. Обновление Configuration.xml ===")
config_path = os.path.join(EXT_CFG, "Configuration.xml")
with open(config_path, "r", encoding="utf-8-sig") as f:
    config = f.read()

if f"<DataProcessor>{NEW_NAME}</DataProcessor>" in config:
    print("  Уже присутствует")
else:
    config = config.replace(
        "\t\t</ChildObjects>",
        f"\t\t\t<DataProcessor>{NEW_NAME}</DataProcessor>\n\t\t</ChildObjects>"
    )
    with open(config_path, "w", encoding="utf-8-sig") as f:
        f.write(config)
    print(f"  Добавлено: <DataProcessor>{NEW_NAME}</DataProcessor>")

# ── 4. Update ConfigDumpInfo.xml ──
print("\n=== 4. Обновление ConfigDumpInfo.xml ===")
cdi_path = os.path.join(EXT_CFG, "ConfigDumpInfo.xml")
with open(cdi_path, "r", encoding="utf-8-sig") as f:
    cdi = f.read()

if f"DataProcessor.{NEW_NAME}" in cdi:
    print("  Уже присутствует")
else:
    entries = []
    # Main DP entry
    entries.append(f'\t\t<Metadata name="DataProcessor.{NEW_NAME}" id="{dp_uuid}" configVersion="{uuid.uuid4().hex[:40]}"/>')
    
    # Attribute and TabularSection entries (sorted for consistency)
    for meta_name, uid in sorted(attr_uuids.items()):
        if meta_name.startswith("Form."):
            continue  # Handle forms separately
        entries.append(f'\t\t<Metadata name="DataProcessor.{NEW_NAME}.{meta_name}" id="{uid}"/>')
    
    # Form entries
    form_uid = attr_uuids["Form.Форма"]
    entries.append(f'\t\t<Metadata name="DataProcessor.{NEW_NAME}.Form.Форма" id="{form_uid}" configVersion="{uuid.uuid4().hex[:40]}"/>')
    entries.append(f'\t\t<Metadata name="DataProcessor.{NEW_NAME}.Form.Форма.Form" id="{form_uid}.0" configVersion="{uuid.uuid4().hex[:40]}"/>')
    
    cdi_block = "\n".join(entries) + "\n"
    cdi = cdi.replace(
        "\t</ConfigVersions>",
        cdi_block + "\t</ConfigVersions>"
    )
    with open(cdi_path, "w", encoding="utf-8-sig") as f:
        f.write(cdi)
    print(f"  Добавлено {len(entries)} CDI-записей")

# ── 5. Update Subsystem ──
print("\n=== 5. Обновление подсистемы ===")
subsys_path = os.path.join(EXT_CFG, "Subsystems", "Анл_Аналитика.xml")
with open(subsys_path, "r", encoding="utf-8-sig") as f:
    subsys = f.read()

if f"DataProcessor.{NEW_NAME}" in subsys:
    print("  Уже в подсистеме")
else:
    subsys = subsys.replace(
        "\t\t\t</Content>",
        f'\t\t\t\t<xr:Item xsi:type="xr:MDObjectRef">DataProcessor.{NEW_NAME}</xr:Item>\n\t\t\t</Content>'
    )
    with open(subsys_path, "w", encoding="utf-8-sig") as f:
        f.write(subsys)
    print(f"  Добавлен DataProcessor.{NEW_NAME}")

# ── 6. Verify Module.bsl exists ──
print("\n=== 6. Проверка Module.bsl ===")
bsl_path = os.path.join(EXT_CFG, "DataProcessors", NEW_NAME, "Forms", "Форма", "Ext", "Form", "Module.bsl")
if os.path.exists(bsl_path):
    size = os.path.getsize(bsl_path)
    print(f"  OK: {size} bytes")
else:
    print("  ⚠️ Module.bsl НЕ НАЙДЕН!")
    
print("\n✅ Регистрация завершена. Готово к деплою.")
