"""
Удаление 6 мигрированных отчётов из основной конфигурации.
Расширение уже задеплоено - трогать не нужно.
"""
import os
import shutil
import re
import sys

DRY_RUN = "--dry-run" in sys.argv

BASE = os.path.join(r"D:\Git\Public_Trade_Module", "Конфигурация")

REPORTS_TO_REMOVE = [
    "Возвраты",
    "ДвижениеТоваров",
    "ВаловаяПрибыль",
    "ПродажиПоСчетам",
    "ДвижениеДенежныхСредств",
    "ПродажиЗаСмену",
]

SUBSYSTEM_REMOVALS = {
    "Склад": ["Возвраты", "ДвижениеТоваров"],
    "Торговля": ["ВаловаяПрибыль", "ПродажиПоСчетам"],
    "Финансы": ["ПродажиПоСчетам"],
    "Все": ["ПродажиПоСчетам", "ДвижениеДенежныхСредств"],
}

print(f"{'DRY-RUN' if DRY_RUN else 'ВЫПОЛНЕНИЕ'}: удаление 6 отчётов из основной конфигурации\n")

# 1. Configuration.xml — удалить <Report>...</Report>
config_path = os.path.join(BASE, "Configuration.xml")
with open(config_path, "r", encoding="utf-8-sig") as f:
    content = f.read()

original = content
for name in REPORTS_TO_REMOVE:
    pattern = rf'\s*<Report>{re.escape(name)}</Report>'
    content = re.sub(pattern, '', content)

if content != original:
    removed_count = sum(1 for name in REPORTS_TO_REMOVE if f"<Report>{name}</Report>" in original)
    print(f"[1] Configuration.xml: удалено {removed_count} записей Report")
    if not DRY_RUN:
        with open(config_path, "w", encoding="utf-8-sig") as f:
            f.write(content)
else:
    print("[1] Configuration.xml: записи уже удалены")

# 2. ConfigDumpInfo.xml — удалить CDI-записи
cdi_path = os.path.join(BASE, "ConfigDumpInfo.xml")
with open(cdi_path, "r", encoding="utf-8-sig") as f:
    cdi = f.read()

original_cdi = cdi
for name in REPORTS_TO_REMOVE:
    # Remove Report entry, Template metadata entry, Template content entry
    # CDI format varies: order="..." or configVersion="..."
    patterns = [
        rf'\s*<Metadata name="Report\.{re.escape(name)}"[^/]*/>\s*',
        rf'\s*<Metadata name="Report\.{re.escape(name)}\.Template\.ОсновнаяСхемаКомпоновкиДанных"[^/]*/>\s*',
        rf'\s*<Metadata name="Report\.{re.escape(name)}\.Template\.ОсновнаяСхемаКомпоновкиДанных\.Template"[^/]*/>\s*',
    ]
    for p in patterns:
        cdi = re.sub(p, '', cdi)

if cdi != original_cdi:
    print(f"[2] ConfigDumpInfo.xml: CDI-записи удалены")
    if not DRY_RUN:
        with open(cdi_path, "w", encoding="utf-8-sig") as f:
            f.write(cdi)
else:
    print("[2] ConfigDumpInfo.xml: записи уже удалены")

# 3. Подсистемы — удалить ссылки на отчёты
subsystems_dir = os.path.join(BASE, "Subsystems")
for subsys_name, reports in SUBSYSTEM_REMOVALS.items():
    subsys_path = os.path.join(subsystems_dir, f"{subsys_name}.xml")
    if not os.path.exists(subsys_path):
        print(f"[3] Подсистема {subsys_name}: файл не найден, пропуск")
        continue
    with open(subsys_path, "r", encoding="utf-8-sig") as f:
        sub_content = f.read()
    original_sub = sub_content
    for rname in reports:
        # Handle both formats: <Item>Report.X</Item> and <xr:Item xsi:type="...">Report.X</xr:Item>
        pattern = rf'\s*<(?:xr:)?Item[^>]*>Report\.{re.escape(rname)}</(?:xr:)?Item>'
        sub_content = re.sub(pattern, '', sub_content)
    if sub_content != original_sub:
        print(f"[3] Подсистема {subsys_name}: ссылки удалены")
        if not DRY_RUN:
            with open(subsys_path, "w", encoding="utf-8-sig") as f:
                f.write(sub_content)
    else:
        print(f"[3] Подсистема {subsys_name}: ссылки уже удалены")

# 4. Удалить файлы отчётов с диска
reports_dir = os.path.join(BASE, "Reports")
for name in REPORTS_TO_REMOVE:
    xml_file = os.path.join(reports_dir, f"{name}.xml")
    folder = os.path.join(reports_dir, name)
    deleted = []
    if os.path.exists(xml_file):
        if not DRY_RUN:
            os.remove(xml_file)
        deleted.append("xml")
    if os.path.isdir(folder):
        if not DRY_RUN:
            shutil.rmtree(folder)
        deleted.append("folder")
    if deleted:
        print(f"[4] {name}: удалено {', '.join(deleted)}")
    else:
        print(f"[4] {name}: файлы уже удалены")

print(f"\n{'DRY-RUN завершён' if DRY_RUN else 'Удаление завершено'}")
