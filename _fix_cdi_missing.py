# -*- coding: utf-8 -*-
"""Add missing ConfigDumpInfo.xml entries for objects that exist in Configuration.xml
but have no CDI record. Reads UUID from each object's XML file."""
import pathlib
import re
import secrets

REPO = pathlib.Path(r"D:\Git\Public_Trade_Module")
CONFIG = REPO / "Конфигурация"
CHECK = CONFIG / "Проверка"

# Objects missing from ConfigDumpInfo.xml (from validation output)
MISSING_OBJECTS = [
    ("Constant", "_ДемоИзолированноеПодключенияВнешнихКомпонент"),
    ("Constant", "_ДемоОбменСПодключаемымОборудованием"),
    ("Constant", "_ДемоРаспределеннаяФискализация"),
    ("Constant", "ИдентификаторОбсужденияФискализации"),
    ("Constant", "ИспользуетсяПротоколRDPвБПО"),
    ("Constant", "ОтправкаЭлектронныхЧековПослеПробитияЧека"),
    ("Constant", "СрокХраненияОперацийОчередиЧеков"),
    ("Constant", "СрокХраненияОперацийПроверкиКМ"),
    ("Constant", "СрокХраненияОперацийСОборудованием"),
    ("Constant", "СрокХраненияПлатежныхОпераций"),
    ("Constant", "СрокХраненияФискальныхОпераций"),
    ("Constant", "ХранитьУспешныеОперацииРазрешения"),
    ("DataProcessor", "_ДемоHttpBridge"),
    ("DataProcessor", "_ДемоВыгрузкаВВесыТСД"),
]

# Map type to folder name
TYPE_TO_FOLDER = {
    "Constant": "Constants",
    "DataProcessor": "DataProcessors",
}

def get_uuid_from_xml(xml_path):
    """Extract UUID from object XML file."""
    content = xml_path.read_text(encoding="utf-8")
    # Pattern: <Constant uuid="..." or <DataProcessor uuid="..."
    match = re.search(r'uuid="([0-9a-f-]+)"', content)
    if match:
        return match.group(1)
    return None

def get_child_uuids(xml_path, obj_type, obj_name):
    """Get UUIDs for child objects (attributes, forms, tabular sections, etc.)."""
    content = xml_path.read_text(encoding="utf-8")
    entries = []
    
    # Find Attribute entries with uuid
    for m in re.finditer(r'<Attribute\s+name="([^"]+)"\s+uuid="([^"]+)"', content):
        attr_name, attr_uuid = m.group(1), m.group(2)
        entries.append(f'\t\t<Metadata name="{obj_type}.{obj_name}.Attribute.{attr_name}" id="{attr_uuid}"/>')
    
    # Find TabularSection entries with uuid
    for m in re.finditer(r'<TabularSection\s+name="([^"]+)"\s+uuid="([^"]+)"', content):
        ts_name, ts_uuid = m.group(1), m.group(2)
        entries.append(f'\t\t<Metadata name="{obj_type}.{obj_name}.TabularSection.{ts_name}" id="{ts_uuid}"/>')
    
    # Find Form entries
    for m in re.finditer(r'<Form>([^<]+)</Form>', content):
        form_name = m.group(1).strip()
        # Look for form descriptor XML
        folder = TYPE_TO_FOLDER.get(obj_type, obj_type + "s")
        form_desc = xml_path.parent / obj_name / "Forms" / f"{form_name}.xml"
        if form_desc.exists():
            form_content = form_desc.read_text(encoding="utf-8")
            form_match = re.search(r'<Form\s+uuid="([^"]+)"', form_content)
            if form_match:
                entries.append(f'\t\t<Metadata name="{obj_type}.{obj_name}.Form.{form_name}" id="{form_match.group(1)}"/>')
    
    # Find Command entries
    for m in re.finditer(r'<Command\s+name="([^"]+)"\s+uuid="([^"]+)"', content):
        cmd_name, cmd_uuid = m.group(1), m.group(2)
        entries.append(f'\t\t<Metadata name="{obj_type}.{obj_name}.Command.{cmd_name}" id="{cmd_uuid}"/>')
    
    return entries

def gen_config_version():
    """Generate configVersion: 32 random hex chars + 00000000."""
    return secrets.token_hex(16) + "00000000"

print("=" * 60)
print("Добавление недостающих записей в ConfigDumpInfo.xml")
print("=" * 60)

for folder_name, base_folder in [("Конфигурация", CONFIG), ("Проверка", CHECK)]:
    cdi_path = base_folder / "ConfigDumpInfo.xml"
    if not cdi_path.exists():
        print(f"  ✗ {cdi_path} не найден")
        continue
    
    content = cdi_path.read_text(encoding="utf-8-sig")
    
    new_entries = []
    for obj_type, obj_name in MISSING_OBJECTS:
        folder = TYPE_TO_FOLDER.get(obj_type, obj_type + "s")
        xml_path = base_folder / folder / f"{obj_name}.xml"
        
        if not xml_path.exists():
            print(f"  ✗ {folder_name}: Файл не найден: {folder}/{obj_name}.xml")
            continue
        
        uuid = get_uuid_from_xml(xml_path)
        if not uuid:
            print(f"  ✗ {folder_name}: UUID не найден в {folder}/{obj_name}.xml")
            continue
        
        # Check if already exists
        cdi_name = f"{obj_type}.{obj_name}"
        if f'name="{cdi_name}"' in content:
            print(f"  - {folder_name}: {cdi_name} уже существует")
            continue
        
        config_version = gen_config_version()
        
        # Get child entries
        children = get_child_uuids(xml_path, obj_type, obj_name)
        
        if children:
            entry = f'\t<Metadata name="{cdi_name}" id="{uuid}" configVersion="{config_version}">\n'
            entry += "\n".join(children) + "\n"
            entry += f'\t</Metadata>'
        else:
            entry = f'\t<Metadata name="{cdi_name}" id="{uuid}" configVersion="{config_version}"/>'
        
        new_entries.append(entry)
        child_count = len(children)
        print(f"  ✓ {folder_name}: {cdi_name} (uuid={uuid}, children={child_count})")
    
    if new_entries:
        # Insert before </ConfigDumpInfo>
        insert_text = "\n".join(new_entries) + "\n"
        content = content.replace("</ConfigDumpInfo>", insert_text + "</ConfigDumpInfo>")
        cdi_path.write_text(content, encoding="utf-8-sig")
        print(f"\n  → {folder_name}: добавлено {len(new_entries)} записей")
    else:
        print(f"\n  → {folder_name}: нечего добавлять")

print("\n✓ Готово!")
