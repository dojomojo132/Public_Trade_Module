"""
Копирование DataProcessor.РабочееМестоКассира в расширение PTM_Analytics.
Оригинал в основной конфигурации НЕ удаляется.
"""
import os
import re
import shutil
import uuid
import sys

DRY_RUN = "--dry-run" in sys.argv

PROJECT = r"D:\Git\Public_Trade_Module"
MAIN_CFG = os.path.join(PROJECT, "Конфигурация")
EXT_CFG = os.path.join(PROJECT, "Конфигурация_PTM_Analytics")

OLD_NAME = "РабочееМестоКассира"
NEW_NAME = "Анл_РабочееМестоКассира"
PREFIX = "Анл_"

print(f"{'DRY-RUN' if DRY_RUN else 'ВЫПОЛНЕНИЕ'}: копирование {OLD_NAME} → {NEW_NAME}")
print()

# ── UUID Generation ──
def new_uuid():
    return str(uuid.uuid4())

# Generate all needed UUIDs
UUIDS = {
    "dp":       new_uuid(),  # DataProcessor root
    "obj_tid":  new_uuid(),  # GeneratedType Object TypeId
    "obj_vid":  new_uuid(),  # GeneratedType Object ValueId
    "mgr_tid":  new_uuid(),  # GeneratedType Manager TypeId
    "mgr_vid":  new_uuid(),  # GeneratedType Manager ValueId
    # Attributes
    "attr_tekgr":  new_uuid(),  # ТекущаяГруппа
    "attr_ppt":    new_uuid(),  # ПолеПоискаТовара
    "attr_ppt2":   new_uuid(),  # ПолеПоискаТовара2
    "attr_kassa":  new_uuid(),  # Касса
    "attr_ks":     new_uuid(),  # КассоваяСмена
    # Tabular section
    "ts_tch":      new_uuid(),  # ТЧ
    "ts_tch_tid":  new_uuid(),  # ТЧ TypeId
    "ts_tch_vid":  new_uuid(),  # ТЧ ValueId
    "ts_row_tid":  new_uuid(),  # ТЧ Row TypeId
    "ts_row_vid":  new_uuid(),  # ТЧ Row ValueId
    "ts_nom":      new_uuid(),  # Номенклатура
    "ts_kol":      new_uuid(),  # Количество
    "ts_cena":     new_uuid(),  # Цена
    "ts_summa":    new_uuid(),  # Сумма
    "ts_mark":     new_uuid(),  # АкцизнаяМарка
    "ts_shk":      new_uuid(),  # Штрихкод
    "ts_mst":      new_uuid(),  # МаркаСтатус
    # Form
    "form":        new_uuid(),  # Form.Форма
}

# Source UUID → New UUID mapping
UUID_MAP = {
    "1876b53a-c567-4e3a-9e12-123456789abc": UUIDS["dp"],
    "1876b53a-c567-4e3a-9e12-123456789abd": UUIDS["obj_tid"],
    "1876b53a-c567-4e3a-9e12-123456789abe": UUIDS["obj_vid"],
    "1876b53a-c567-4e3a-9e12-123456789abf": UUIDS["mgr_tid"],
    "1876b53a-c567-4e3a-9e12-123456789ac0": UUIDS["mgr_vid"],
    "1876b53a-c567-4e3a-9e12-123456789ac1": UUIDS["attr_tekgr"],
    "1876b53a-c567-4e3a-9e12-123456789ac2": UUIDS["attr_ppt"],
    "1876b53a-c567-4e3a-9e12-123456789ac3": UUIDS["attr_ppt2"],
    "71108e12-679f-48ad-9d68-dda816773b62": UUIDS["attr_kassa"],
    "40639cd1-a22f-4f1c-af2c-3dfb81250c8a": UUIDS["attr_ks"],
    "1876b53a-c567-4e3a-9e12-123456789ac4": UUIDS["ts_tch"],
    "1876b53a-c567-4e3a-9e12-123456789ac5": UUIDS["ts_tch_tid"],
    "1876b53a-c567-4e3a-9e12-123456789ac6": UUIDS["ts_tch_vid"],
    "1876b53a-c567-4e3a-9e12-123456789ac7": UUIDS["ts_row_tid"],
    "1876b53a-c567-4e3a-9e12-123456789ac8": UUIDS["ts_row_vid"],
    "1876b53a-c567-4e3a-9e12-123456789ac9": UUIDS["ts_nom"],
    "1876b53a-c567-4e3a-9e12-123456789aca": UUIDS["ts_kol"],
    "1876b53a-c567-4e3a-9e12-123456789acb": UUIDS["ts_cena"],
    "1876b53a-c567-4e3a-9e12-123456789acc": UUIDS["ts_summa"],
    "400bbbd8-e76d-46da-856c-03d4f823e3b8": UUIDS["ts_mark"],
    "500bbbd8-e76d-46da-856c-03d4f823e3c9": UUIDS["ts_shk"],
    "601ccce9-f87e-47eb-967d-14e5f934f4da": UUIDS["ts_mst"],
    "1876b53a-c567-4e3a-9e12-123456789acd": UUIDS["form"],
}

def replace_uuids_and_names(content):
    """Replace old UUIDs with new ones and rename the DataProcessor."""
    for old_uuid, new_uuid_val in UUID_MAP.items():
        content = content.replace(old_uuid, new_uuid_val)
    # Replace DataProcessor name in metadata references
    content = content.replace(
        f"DataProcessorObject.{OLD_NAME}",
        f"DataProcessorObject.{NEW_NAME}"
    )
    content = content.replace(
        f"DataProcessorManager.{OLD_NAME}",
        f"DataProcessorManager.{NEW_NAME}"
    )
    content = content.replace(
        f"DataProcessorTabularSection.{OLD_NAME}",
        f"DataProcessorTabularSection.{NEW_NAME}"
    )
    content = content.replace(
        f"DataProcessorTabularSectionRow.{OLD_NAME}",
        f"DataProcessorTabularSectionRow.{NEW_NAME}"
    )
    content = content.replace(
        f"<Name>{OLD_NAME}</Name>",
        f"<Name>{NEW_NAME}</Name>"
    )
    content = content.replace(
        f"DataProcessor.{OLD_NAME}.Form.Форма",
        f"DataProcessor.{NEW_NAME}.Form.Форма"
    )
    return content

# ── Step 1: Copy and transform main XML ──
print("=== 1. Создание основного XML обработки ===")
src_xml = os.path.join(MAIN_CFG, "DataProcessors", f"{OLD_NAME}.xml")
dst_xml = os.path.join(EXT_CFG, "DataProcessors", f"{NEW_NAME}.xml")

with open(src_xml, "r", encoding="utf-8-sig") as f:
    content = f.read()

content = replace_uuids_and_names(content)
# Keep the synonym as is (Рабочее место кассира (РМК)) - that's the display name

os.makedirs(os.path.dirname(dst_xml), exist_ok=True)
if not DRY_RUN:
    with open(dst_xml, "w", encoding="utf-8-sig") as f:
        f.write(content)
print(f"  {NEW_NAME}.xml создан")

# ── Step 2: Copy form metadata XML (Форма.xml) ──
print("\n=== 2. Копирование метаданных формы ===")
src_form_meta = os.path.join(MAIN_CFG, "DataProcessors", OLD_NAME, "Forms", "Форма.xml")
dst_form_dir = os.path.join(EXT_CFG, "DataProcessors", NEW_NAME, "Forms")
dst_form_meta = os.path.join(dst_form_dir, "Форма.xml")

with open(src_form_meta, "r", encoding="utf-8-sig") as f:
    form_meta = f.read()

form_meta = replace_uuids_and_names(form_meta)

os.makedirs(dst_form_dir, exist_ok=True)
if not DRY_RUN:
    with open(dst_form_meta, "w", encoding="utf-8-sig") as f:
        f.write(form_meta)
print(f"  Форма.xml создан")

# ── Step 3: Copy Form.xml (form descriptor) ──
print("\n=== 3. Копирование дескриптора формы ===")
src_form_xml = os.path.join(MAIN_CFG, "DataProcessors", OLD_NAME, "Forms", "Форма", "Ext", "Form.xml")
dst_form_xml_dir = os.path.join(EXT_CFG, "DataProcessors", NEW_NAME, "Forms", "Форма", "Ext")
dst_form_xml = os.path.join(dst_form_xml_dir, "Form.xml")

os.makedirs(dst_form_xml_dir, exist_ok=True)
if not DRY_RUN:
    # Form.xml is binary-safe copy - no UUID replacement needed
    # (form XML uses element IDs, not metadata UUIDs)
    shutil.copy2(src_form_xml, dst_form_xml)
print(f"  Form.xml скопирован")

# ── Step 4: Copy Module.bsl ──
print("\n=== 4. Копирование BSL-модуля формы ===")
src_bsl = os.path.join(MAIN_CFG, "DataProcessors", OLD_NAME, "Forms", "Форма", "Ext", "Form", "Module.bsl")
dst_bsl_dir = os.path.join(EXT_CFG, "DataProcessors", NEW_NAME, "Forms", "Форма", "Ext", "Form")
dst_bsl = os.path.join(dst_bsl_dir, "Module.bsl")

os.makedirs(dst_bsl_dir, exist_ok=True)
if not DRY_RUN:
    shutil.copy2(src_bsl, dst_bsl)

line_count = sum(1 for _ in open(src_bsl, encoding="utf-8-sig"))
print(f"  Module.bsl скопирован ({line_count} строк)")

# ── Step 5: Update extension Configuration.xml ──
print("\n=== 5. Обновление Configuration.xml расширения ===")
ext_config = os.path.join(EXT_CFG, "Configuration.xml")
with open(ext_config, "r", encoding="utf-8-sig") as f:
    config_content = f.read()

if f"<DataProcessor>{NEW_NAME}</DataProcessor>" in config_content:
    print("  Уже присутствует, пропуск")
else:
    # Add before </ChildObjects>
    config_content = config_content.replace(
        "\t\t</ChildObjects>",
        f"\t\t\t<DataProcessor>{NEW_NAME}</DataProcessor>\n\t\t</ChildObjects>"
    )
    if not DRY_RUN:
        with open(ext_config, "w", encoding="utf-8-sig") as f:
            f.write(config_content)
    print(f"  Добавлен <DataProcessor>{NEW_NAME}</DataProcessor>")

# ── Step 6: Update extension ConfigDumpInfo.xml ──
print("\n=== 6. Обновление ConfigDumpInfo.xml расширения ===")
ext_cdi = os.path.join(EXT_CFG, "ConfigDumpInfo.xml")
with open(ext_cdi, "r", encoding="utf-8-sig") as f:
    cdi_content = f.read()

if f"DataProcessor.{NEW_NAME}" in cdi_content:
    print("  Уже присутствует, пропуск")
else:
    # Build CDI entries — flat format matching existing extension CDI style
    cdi_entries = []
    
    # Main DataProcessor entry
    cdi_entries.append(f'\t\t<Metadata name="DataProcessor.{NEW_NAME}" id="{UUIDS["dp"]}" configVersion="{uuid.uuid4().hex[:40]}"/>')
    
    # Attribute and TabularSection entries (flat, each self-closing)
    for attr_name, key in [
        ("Attribute.ТекущаяГруппа", "attr_tekgr"),
        ("Attribute.ПолеПоискаТовара", "attr_ppt"),
        ("Attribute.ПолеПоискаТовара2", "attr_ppt2"),
        ("Attribute.Касса", "attr_kassa"),
        ("Attribute.КассоваяСмена", "attr_ks"),
        ("TabularSection.ТЧ", "ts_tch"),
        ("TabularSection.ТЧ.Attribute.Номенклатура", "ts_nom"),
        ("TabularSection.ТЧ.Attribute.Количество", "ts_kol"),
        ("TabularSection.ТЧ.Attribute.Цена", "ts_cena"),
        ("TabularSection.ТЧ.Attribute.Сумма", "ts_summa"),
        ("TabularSection.ТЧ.Attribute.АкцизнаяМарка", "ts_mark"),
        ("TabularSection.ТЧ.Attribute.Штрихкод", "ts_shk"),
        ("TabularSection.ТЧ.Attribute.МаркаСтатус", "ts_mst"),
    ]:
        cdi_entries.append(f'\t\t<Metadata name="DataProcessor.{NEW_NAME}.{attr_name}" id="{UUIDS[key]}"/>')
    
    # Form CDI entries (flat, with configVersion)
    cdi_entries.append(f'\t\t<Metadata name="DataProcessor.{NEW_NAME}.Form.Форма" id="{UUIDS["form"]}" configVersion="{uuid.uuid4().hex[:40]}"/>')
    cdi_entries.append(f'\t\t<Metadata name="DataProcessor.{NEW_NAME}.Form.Форма.Form" id="{UUIDS["form"]}.0" configVersion="{uuid.uuid4().hex[:40]}"/>')

    cdi_block = "\n".join(cdi_entries) + "\n"

    # Insert before </ConfigVersions>
    cdi_content = cdi_content.replace(
        "\t</ConfigVersions>",
        cdi_block + "\t</ConfigVersions>"
    )
    if not DRY_RUN:
        with open(ext_cdi, "w", encoding="utf-8-sig") as f:
            f.write(cdi_content)
    print(f"  CDI-записи добавлены ({len(cdi_entries)} записей)")

# ── Step 7: Update subsystem Анл_Аналитика ──
print("\n=== 7. Добавление в подсистему Анл_Аналитика ===")
subsys_path = os.path.join(EXT_CFG, "Subsystems", "Анл_Аналитика.xml")
if os.path.exists(subsys_path):
    with open(subsys_path, "r", encoding="utf-8-sig") as f:
        subsys_content = f.read()

    if f"DataProcessor.{NEW_NAME}" in subsys_content:
        print("  Уже в подсистеме, пропуск")
    else:
        # Add before </Content>
        subsys_content = subsys_content.replace(
            "\t\t\t</Content>",
            f'\t\t\t\t<xr:Item xsi:type="xr:MDObjectRef">DataProcessor.{NEW_NAME}</xr:Item>\n\t\t\t</Content>'
        )
        if not DRY_RUN:
            with open(subsys_path, "w", encoding="utf-8-sig") as f:
                f.write(subsys_content)
        print(f"  Добавлен DataProcessor.{NEW_NAME}")
else:
    print(f"  Подсистема не найдена: {subsys_path}")

print(f"\n{'DRY-RUN завершён' if DRY_RUN else 'Миграция завершена!'}")
print(f"\nФайлы расширения:")
print(f"  {dst_xml}")
print(f"  {dst_form_meta}")
print(f"  {dst_form_xml}")
print(f"  {dst_bsl}")
