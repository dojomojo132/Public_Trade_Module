"""
Миграция 5 объектов в расширение PTM_Analytics:
  1. Отчёт Продажи → Анл_Продажи
  2. Отчёт Взаиморасчеты → Анл_Взаиморасчеты
  3. Обработка УправлениеНастройками → Анл_УправлениеНастройками
  4. Обработка ТестовоеЗаполнениеДанных → Анл_ТестовоеЗаполнениеДанных
  5. Обработка ТестыРМК → Анл_ТестыРМК
"""

import shutil
import uuid
import re
from pathlib import Path

ROOT = Path(r"D:\Git\Public_Trade_Module")
SRC = ROOT / "Конфигурация"
DST = ROOT / "Конфигурация_PTM_Analytics"

def new_uuid():
    return str(uuid.uuid4())

# ── Маппинг объектов ──
REPORTS = [
    {
        "old": "Продажи",
        "new": "Анл_Продажи",
        "type": "Report",
        "folder": "Reports",
        "uuid": new_uuid(),
        "tmpl_uuid": new_uuid(),
        "has_form": False,
        "has_obj_module": False,
    },
    {
        "old": "Взаиморасчеты",
        "new": "Анл_Взаиморасчеты",
        "type": "Report",
        "folder": "Reports",
        "uuid": new_uuid(),
        "tmpl_uuid": new_uuid(),
        "has_form": False,
        "has_obj_module": False,
    },
]

DATAPROCESSORS = [
    {
        "old": "УправлениеНастройками",
        "new": "Анл_УправлениеНастройками",
        "type": "DataProcessor",
        "folder": "DataProcessors",
        "uuid": new_uuid(),
        "form_uuid": new_uuid(),
        "has_form": True,
        "has_obj_module": False,
    },
    {
        "old": "ТестовоеЗаполнениеДанных",
        "new": "Анл_ТестовоеЗаполнениеДанных",
        "type": "DataProcessor",
        "folder": "DataProcessors",
        "uuid": new_uuid(),
        "form_uuid": new_uuid(),
        "has_form": True,
        "has_obj_module": True,
    },
    {
        "old": "ТестыРМК",
        "new": "Анл_ТестыРМК",
        "type": "DataProcessor",
        "folder": "DataProcessors",
        "uuid": new_uuid(),
        "form_uuid": new_uuid(),
        "has_form": True,
        "has_obj_module": False,
    },
]

ALL = REPORTS + DATAPROCESSORS

def copy_tree(src_dir, dst_dir):
    """Копирует папку рекурсивно."""
    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    shutil.copytree(src_dir, dst_dir)
    print(f"  COPY {src_dir.name}/ → {dst_dir.relative_to(ROOT)}")

def copy_file(src_file, dst_file):
    """Копирует файл."""
    dst_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_file, dst_file)
    print(f"  COPY {src_file.name} → {dst_file.relative_to(ROOT)}")

def fix_descriptor_xml(obj):
    """Исправляет дескрипторный XML: переименовывает объект, обновляет UUID."""
    folder = obj["folder"]
    dst_xml = DST / folder / f"{obj['new']}.xml"
    
    # Читаем исходный XML
    src_xml = SRC / folder / f"{obj['old']}.xml"
    content = src_xml.read_bytes().decode("utf-8-sig")
    
    # Заменяем UUID корневого объекта
    old_uuid_match = re.search(r'uuid="([^"]+)"', content)
    if old_uuid_match:
        content = content.replace(old_uuid_match.group(1), obj["uuid"], 1)
    
    # Заменяем имена
    content = content.replace(f"<Name>{obj['old']}</Name>", f"<Name>{obj['new']}</Name>")
    
    # Заменяем GeneratedType names
    if obj["type"] == "Report":
        content = content.replace(f"ReportObject.{obj['old']}", f"ReportObject.{obj['new']}")
        content = content.replace(f"ReportManager.{obj['old']}", f"ReportManager.{obj['new']}")
        content = content.replace(f"Report.{obj['old']}.Template", f"Report.{obj['new']}.Template")
    elif obj["type"] == "DataProcessor":
        content = content.replace(f"DataProcessorObject.{obj['old']}", f"DataProcessorObject.{obj['new']}")
        content = content.replace(f"DataProcessorManager.{obj['old']}", f"DataProcessorManager.{obj['new']}")
        content = content.replace(f"DataProcessor.{obj['old']}.Form", f"DataProcessor.{obj['new']}.Form")
    
    # Генерируем новые TypeId/ValueId для GeneratedType
    for tag in ["TypeId", "ValueId"]:
        for match in re.finditer(rf"<xr:{tag}>([^<]+)</xr:{tag}>", content):
            content = content.replace(match.group(0), f"<xr:{tag}>{new_uuid()}</xr:{tag}>", 1)
    
    dst_xml.parent.mkdir(parents=True, exist_ok=True)
    dst_xml.write_bytes(content.encode("utf-8-sig"))
    print(f"  FIX  {dst_xml.relative_to(ROOT)}")

def fix_form_xml(obj):
    """Исправляет Form.xml: заменяет тип данных DataProcessorObject.OldName → DataProcessorObject.NewName."""
    form_xml = DST / obj["folder"] / obj["new"] / "Forms" / "Форма" / "Ext" / "Form.xml"
    if not form_xml.exists():
        print(f"  WARN Form.xml not found: {form_xml}")
        return
    
    content = form_xml.read_bytes().decode("utf-8-sig")
    content = content.replace(
        f"DataProcessorObject.{obj['old']}",
        f"DataProcessorObject.{obj['new']}"
    )
    form_xml.write_bytes(content.encode("utf-8-sig"))
    print(f"  FIX  Form.xml type ref → DataProcessorObject.{obj['new']}")

def copy_objects():
    """Копирует файлы всех объектов."""
    for obj in REPORTS:
        folder = obj["folder"]
        # Копируем папку отчёта (шаблоны)
        src_dir = SRC / folder / obj["old"]
        dst_dir = DST / folder / obj["new"]
        copy_tree(src_dir, dst_dir)
        # Фиксим дескриптор
        fix_descriptor_xml(obj)
        # Копируем дескриптор шаблона (он обычно без ссылок на имя)
    
    for obj in DATAPROCESSORS:
        folder = obj["folder"]
        # Копируем папку обработки (формы, модули)
        src_dir = SRC / folder / obj["old"]
        dst_dir = DST / folder / obj["new"]
        copy_tree(src_dir, dst_dir)
        # Фиксим дескриптор
        fix_descriptor_xml(obj)
        # Фиксим ссылки в Form.xml
        if obj["has_form"]:
            fix_form_xml(obj)

def update_configuration_xml():
    """Добавляет новые объекты в Configuration.xml расширения."""
    cfg = DST / "Configuration.xml"
    content = cfg.read_bytes().decode("utf-8-sig")
    
    # Находим </ChildObjects> и вставляем перед ним
    insert_lines = []
    for obj in ALL:
        tag = obj["type"]
        insert_lines.append(f"\t\t\t<{tag}>{obj['new']}</{tag}>")
    
    insert_block = "\n".join(insert_lines) + "\n"
    content = content.replace("\t\t</ChildObjects>", insert_block + "\t\t</ChildObjects>")
    
    cfg.write_bytes(content.encode("utf-8-sig"))
    print(f"  UPD  Configuration.xml (+{len(ALL)} objects)")

def update_cdi():
    """Добавляет записи в ConfigDumpInfo.xml."""
    cdi = DST / "ConfigDumpInfo.xml"
    content = cdi.read_bytes().decode("utf-8-sig")
    
    entries = []
    for obj in REPORTS:
        # Report entry
        entries.append(f'\t\t<Metadata name="Report.{obj["new"]}" id="{obj["uuid"]}"/>')
        # Template descriptor
        entries.append(f'\t\t<Metadata name="Report.{obj["new"]}.Template.ОсновнаяСхемаКомпоновкиДанных" id="{obj["tmpl_uuid"]}"/>')
        # Template content
        entries.append(f'\t\t<Metadata name="Report.{obj["new"]}.Template.ОсновнаяСхемаКомпоновкиДанных.Template" id="{obj["tmpl_uuid"]}.0"/>')
    
    for obj in DATAPROCESSORS:
        # DataProcessor entry
        entries.append(f'\t\t<Metadata name="DataProcessor.{obj["new"]}" id="{obj["uuid"]}"/>')
        # Form entries
        if obj["has_form"]:
            entries.append(f'\t\t<Metadata name="DataProcessor.{obj["new"]}.Form.Форма" id="{obj["form_uuid"]}"/>')
            entries.append(f'\t\t<Metadata name="DataProcessor.{obj["new"]}.Form.Форма.Form" id="{obj["form_uuid"]}.0"/>')
    
    insert_block = "\n".join(entries) + "\n"
    content = content.replace("\t</ConfigVersions>", insert_block + "\t</ConfigVersions>")
    
    cdi.write_bytes(content.encode("utf-8-sig"))
    print(f"  UPD  ConfigDumpInfo.xml (+{len(entries)} entries)")

def update_subsystem():
    """Добавляет новые объекты в подсистему Анл_Аналитика."""
    sub = DST / "Subsystems" / "Анл_Аналитика.xml"
    content = sub.read_bytes().decode("utf-8-sig")
    
    items = []
    for obj in ALL:
        items.append(f'\t\t\t\t<xr:Item xsi:type="xr:MDObjectRef">{obj["type"]}.{obj["new"]}</xr:Item>')
    
    insert_block = "\n".join(items) + "\n"
    content = content.replace("\t\t\t</Content>", insert_block + "\t\t\t</Content>")
    
    sub.write_bytes(content.encode("utf-8-sig"))
    print(f"  UPD  Subsystems/Анл_Аналитика.xml (+{len(ALL)} items)")

def check_double_bom():
    """Проверяет double BOM в созданных файлах."""
    count = 0
    for p in DST.rglob("*.xml"):
        data = p.read_bytes()
        if data[:6] == b'\xef\xbb\xbf\xef\xbb\xbf':
            p.write_bytes(b'\xef\xbb\xbf' + data[6:])
            count += 1
            print(f"  FIX  Double BOM removed: {p.relative_to(ROOT)}")
    if count == 0:
        print("  OK   No double BOM issues")

def main():
    print("=" * 60)
    print("Миграция 5 объектов в PTM_Analytics")
    print("=" * 60)
    
    print("\n[1/6] Копирование файлов...")
    copy_objects()
    
    print("\n[2/6] Обновление Configuration.xml...")
    update_configuration_xml()
    
    print("\n[3/6] Обновление ConfigDumpInfo.xml...")
    update_cdi()
    
    print("\n[4/6] Обновление подсистемы...")
    update_subsystem()
    
    print("\n[5/6] Проверка BOM...")
    check_double_bom()
    
    print("\n[6/6] Итог:")
    print(f"  Отчёты:    {', '.join(r['new'] for r in REPORTS)}")
    print(f"  Обработки: {', '.join(d['new'] for d in DATAPROCESSORS)}")
    print("\n✅ Готово! Следующий шаг: python scripts/deploy_ext.py --ext PTM_Analytics --action Full")

if __name__ == "__main__":
    main()
