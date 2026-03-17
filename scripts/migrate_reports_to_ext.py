#!/usr/bin/env python3
"""
Миграция 6 отчётов из основной конфигурации PTM в расширение PTM_Analytics.

Операции:
1. Смена префикса расширения Test_ → Анл_
2. Переименование существующих объектов расширения
3. Создание 6 новых отчётов в расширении (копия DCS-шаблонов)
4. Удаление 6 отчётов из основной конфигурации (Configuration.xml, CDI, подсистемы)

Использование:
    python scripts/migrate_reports_to_ext.py [--dry-run]
"""

import os
import re
import shutil
import sys
import uuid
from pathlib import Path

DRY_RUN = "--dry-run" in sys.argv

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "Конфигурация"
EXT = ROOT / "Конфигурация_PTM_Analytics"

OLD_PREFIX = "Test_"
NEW_PREFIX = "Анл_"

# ============================================================
# Отчёты для миграции: {оригинальное_имя: синоним}
# ============================================================
REPORTS_TO_MIGRATE = {
    "Возвраты": "Возвраты",
    "ВаловаяПрибыль": "Валовая прибыль",
    "ПродажиПоСчетам": "Продажи по кассам",
    "ДвижениеДенежныхСредств": "Движение денежных средств",
    "ПродажиЗаСмену": "Продажи за смену",
    "ДвижениеТоваров": "Движение товаров",
}

# Подсистемы → отчёты, которые нужно удалить оттуда
SUBSYSTEM_REMOVALS = {
    "Склад": ["Возвраты", "ДвижениеТоваров"],
    "Торговля": ["ВаловаяПрибыль", "ПродажиПоСчетам"],
    "Финансы": ["ПродажиПоСчетам"],
    "Все": ["ПродажиПоСчетам", "ДвижениеДенежныхСредств"],
}

# XML namespaces (полный набор для совместимости с 1С 8.3.27)
XML_NS = (
    'xmlns="http://v8.1c.ru/8.3/MDClasses" '
    'xmlns:app="http://v8.1c.ru/8.2/managed-application/core" '
    'xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" '
    'xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" '
    'xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" '
    'xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" '
    'xmlns:style="http://v8.1c.ru/8.1/data/ui/style" '
    'xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" '
    'xmlns:v8="http://v8.1c.ru/8.1/data/core" '
    'xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" '
    'xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" '
    'xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" '
    'xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" '
    'xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" '
    'xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" '
    'xmlns:xs="http://www.w3.org/2001/XMLSchema" '
    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
    'version="2.20"'
)

BOM = b"\xef\xbb\xbf"

# ============================================================
# Утилиты
# ============================================================

def gen_uuid():
    return str(uuid.uuid4())


def gen_config_version():
    """40-символьный hex для configVersion."""
    return uuid.uuid4().hex[:40]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, content: str):
    """Записать UTF-8 с BOM (стандарт 1С XML)."""
    if DRY_RUN:
        print(f"  [DRY-RUN] write: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(BOM + content.encode("utf-8"))


def copy_binary(src: Path, dst: Path):
    """Побайтовое копирование (для DCS-шаблонов)."""
    if DRY_RUN:
        print(f"  [DRY-RUN] copy: {src} → {dst}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def rename_path(old: Path, new: Path):
    if DRY_RUN:
        print(f"  [DRY-RUN] rename: {old} → {new}")
        return
    if old.exists():
        new.parent.mkdir(parents=True, exist_ok=True)
        old.rename(new)


def log(msg):
    print(f"  {msg}")


# ============================================================
# 1. Смена префикса расширения
# ============================================================

def rename_prefix():
    print("\n=== 1. Смена префикса Test_ → Анл_ ===")

    # 1.1 Переименование папки и файла отчёта
    old_report = "Test_АнализПродаж"
    new_report = "Анл_АнализПродаж"

    old_dir = EXT / "Reports" / old_report
    new_dir = EXT / "Reports" / new_report
    old_xml = EXT / "Reports" / f"{old_report}.xml"
    new_xml = EXT / "Reports" / f"{new_report}.xml"

    if old_dir.exists():
        rename_path(old_dir, new_dir)
        log(f"Папка: {old_report}/ → {new_report}/")
    if old_xml.exists():
        rename_path(old_xml, new_xml)
        log(f"Файл: {old_report}.xml → {new_report}.xml")

    # 1.2 Обновить содержимое отчёта XML
    report_xml = new_xml
    if report_xml.exists() and not DRY_RUN:
        text = read_text(report_xml)
        text = text.replace(old_report, new_report)
        write_text(report_xml, text)
        log(f"Содержимое {new_report}.xml обновлено")

    # 1.3 Переименование роли
    old_role = "Test_ОсновнаяРоль"
    new_role = "Анл_ОсновнаяРоль"
    old_role_xml = EXT / "Roles" / f"{old_role}.xml"
    new_role_xml = EXT / "Roles" / f"{new_role}.xml"

    if old_role_xml.exists():
        rename_path(old_role_xml, new_role_xml)
        log(f"Роль: {old_role}.xml → {new_role}.xml")
    if new_role_xml.exists() and not DRY_RUN:
        text = read_text(new_role_xml)
        text = text.replace(old_role, new_role)
        write_text(new_role_xml, text)
        log(f"Содержимое {new_role}.xml обновлено")

    # 1.4 Обновить Configuration.xml расширения
    config_xml = EXT / "Configuration.xml"
    if config_xml.exists() and not DRY_RUN:
        text = read_text(config_xml)
        text = text.replace(f"<NamePrefix>{OLD_PREFIX}</NamePrefix>",
                          f"<NamePrefix>{NEW_PREFIX}</NamePrefix>")
        text = text.replace(f"Role.{old_role}", f"Role.{new_role}")
        text = text.replace(f"<Role>{old_role}</Role>",
                          f"<Role>{new_role}</Role>")
        text = text.replace(f"<Report>{old_report}</Report>",
                          f"<Report>{new_report}</Report>")
        write_text(config_xml, text)
        log("Configuration.xml обновлён (префикс, роль, отчёт)")

    # 1.5 Обновить ConfigDumpInfo.xml расширения
    cdi_xml = EXT / "ConfigDumpInfo.xml"
    if cdi_xml.exists() and not DRY_RUN:
        text = read_text(cdi_xml)
        text = text.replace(old_report, new_report)
        text = text.replace(old_role, new_role)
        write_text(cdi_xml, text)
        log("ConfigDumpInfo.xml обновлён")


# ============================================================
# 2. Создание отчётов в расширении
# ============================================================

def create_report_xml(report_name: str, synonym: str) -> str:
    """Генерирует XML-метаданные для отчёта расширения."""
    ext_name = NEW_PREFIX + report_name
    report_uuid = gen_uuid()
    obj_type_id = gen_uuid()
    obj_value_id = gen_uuid()
    mgr_type_id = gen_uuid()
    mgr_value_id = gen_uuid()

    return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject {XML_NS}>
\t<Report uuid="{report_uuid}">
\t\t<InternalInfo>
\t\t\t<xr:GeneratedType name="ReportObject.{ext_name}" category="Object">
\t\t\t\t<xr:TypeId>{obj_type_id}</xr:TypeId>
\t\t\t\t<xr:ValueId>{obj_value_id}</xr:ValueId>
\t\t\t</xr:GeneratedType>
\t\t\t<xr:GeneratedType name="ReportManager.{ext_name}" category="Manager">
\t\t\t\t<xr:TypeId>{mgr_type_id}</xr:TypeId>
\t\t\t\t<xr:ValueId>{mgr_value_id}</xr:ValueId>
\t\t\t</xr:GeneratedType>
\t\t</InternalInfo>
\t\t<Properties>
\t\t\t<Name>{ext_name}</Name>
\t\t\t<Synonym>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>{synonym}</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Synonym>
\t\t\t<Comment/>
\t\t\t<UseStandardCommands>true</UseStandardCommands>
\t\t\t<DefaultForm/>
\t\t\t<AuxiliaryForm/>
\t\t\t<MainDataCompositionSchema>Report.{ext_name}.Template.ОсновнаяСхемаКомпоновкиДанных</MainDataCompositionSchema>
\t\t\t<DefaultSettingsForm/>
\t\t\t<AuxiliarySettingsForm/>
\t\t\t<DefaultVariantForm/>
\t\t\t<VariantsStorage/>
\t\t\t<SettingsStorage/>
\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>
\t\t\t<ExtendedPresentation/>
\t\t\t<Explanation/>
\t\t</Properties>
\t\t<ChildObjects>
\t\t\t<Template>ОсновнаяСхемаКомпоновкиДанных</Template>
\t\t</ChildObjects>
\t</Report>
</MetaDataObject>"""


def create_reports_in_extension():
    print("\n=== 2. Создание отчётов в расширении ===")

    reports_dir = EXT / "Reports"
    created_names = []

    for orig_name, synonym in REPORTS_TO_MIGRATE.items():
        ext_name = NEW_PREFIX + orig_name
        log(f"Создаю {ext_name} (Синоним: \"{synonym}\")...")

        # 2.1 Создать XML-метаданные отчёта
        xml_content = create_report_xml(orig_name, synonym)
        write_text(reports_dir / f"{ext_name}.xml", xml_content)

        # 2.2 Скопировать DCS-шаблон (бинарно — сохраняет формат и BOM)
        src_template = (MAIN / "Reports" / orig_name / "Templates" /
                       "ОсновнаяСхемаКомпоновкиДанных" / "Ext" / "Template.xml")
        dst_template = (reports_dir / ext_name / "Templates" /
                       "ОсновнаяСхемаКомпоновкиДанных" / "Ext" / "Template.xml")

        if src_template.exists():
            copy_binary(src_template, dst_template)
            log(f"  DCS-шаблон скопирован: {src_template.name}")
        else:
            log(f"  ⚠️ DCS-шаблон не найден: {src_template}")

        created_names.append(ext_name)

    return created_names


# ============================================================
# 3. Обновление Configuration.xml расширения
# ============================================================

def update_ext_configuration_xml(new_reports: list[str]):
    print("\n=== 3. Обновление Configuration.xml расширения ===")

    config_xml = EXT / "Configuration.xml"
    if not config_xml.exists():
        log("⚠️ Configuration.xml не найден!")
        return

    if DRY_RUN:
        log("[DRY-RUN] Добавление отчётов в Configuration.xml")
        return

    text = read_text(config_xml)

    # Найти </ChildObjects> и добавить отчёты перед ним
    report_lines = "\n".join(f"\t\t\t<Report>{name}</Report>" for name in new_reports)
    text = text.replace("</ChildObjects>", f"{report_lines}\n\t\t</ChildObjects>")

    write_text(config_xml, text)
    log(f"Добавлено {len(new_reports)} отчётов в ChildObjects")


# ============================================================
# 4. Обновление ConfigDumpInfo.xml расширения
# ============================================================

def update_ext_cdi(new_reports: list[str]):
    print("\n=== 4. Обновление ConfigDumpInfo.xml расширения ===")

    cdi_xml = EXT / "ConfigDumpInfo.xml"
    if not cdi_xml.exists():
        log("⚠️ ConfigDumpInfo.xml не найден!")
        return

    if DRY_RUN:
        log("[DRY-RUN] Добавление CDI-записей")
        return

    text = read_text(cdi_xml)

    # Генерируем CDI-записи для каждого отчёта
    cdi_entries = []
    for ext_name in new_reports:
        report_id = gen_uuid()
        template_id = gen_uuid()
        cv1 = gen_config_version()
        cv2 = gen_config_version()
        cv3 = gen_config_version()

        cdi_entries.append(
            f'\t\t<Metadata name="Report.{ext_name}" '
            f'id="{report_id}" configVersion="{cv1}"/>'
        )
        cdi_entries.append(
            f'\t\t<Metadata name="Report.{ext_name}.Template.ОсновнаяСхемаКомпоновкиДанных" '
            f'id="{template_id}" configVersion="{cv2}"/>'
        )
        cdi_entries.append(
            f'\t\t<Metadata name="Report.{ext_name}.Template.ОсновнаяСхемаКомпоновкиДанных.Template" '
            f'id="{template_id}.0" configVersion="{cv3}"/>'
        )

    entries_text = "\n".join(cdi_entries)
    text = text.replace("</ConfigVersions>", f"{entries_text}\n\t</ConfigVersions>")

    write_text(cdi_xml, text)
    log(f"Добавлено {len(cdi_entries)} CDI-записей")


# ============================================================
# 5. Удаление отчётов из основной конфигурации
# ============================================================

def remove_from_main_configuration_xml():
    print("\n=== 5. Удаление отчётов из Configuration.xml основной конфигурации ===")

    config_xml = MAIN / "Configuration.xml"
    if not config_xml.exists():
        log("⚠️ Configuration.xml не найден!")
        return

    if DRY_RUN:
        log("[DRY-RUN] Удаление отчётов из Configuration.xml")
        return

    text = read_text(config_xml)

    for name in REPORTS_TO_MIGRATE:
        pattern = f"\t\t\t<Report>{name}</Report>\n"
        if pattern in text:
            text = text.replace(pattern, "")
            log(f"Удалён: Report.{name}")
        else:
            # Попробовать без \n в конце
            pattern2 = f"\t\t\t<Report>{name}</Report>"
            if pattern2 in text:
                text = text.replace(pattern2 + "\n", "")
                text = text.replace(pattern2, "")
                log(f"Удалён: Report.{name}")
            else:
                log(f"⚠️ Не найден: Report.{name}")

    write_text(config_xml, text)


def remove_from_main_cdi():
    print("\n=== 6. Удаление отчётов из ConfigDumpInfo.xml основной конфигурации ===")

    cdi_xml = MAIN / "ConfigDumpInfo.xml"
    if not cdi_xml.exists():
        log("⚠️ ConfigDumpInfo.xml не найден!")
        return

    if DRY_RUN:
        log("[DRY-RUN] Удаление CDI-записей")
        return

    text = read_text(cdi_xml)
    removed = 0

    for name in REPORTS_TO_MIGRATE:
        # Удалить все строки содержащие Report.{name}
        lines = text.split("\n")
        new_lines = []
        for line in lines:
            if f'"Report.{name}"' in line or f'"Report.{name}.' in line:
                removed += 1
            else:
                new_lines.append(line)
        text = "\n".join(new_lines)

    write_text(cdi_xml, text)
    log(f"Удалено {removed} CDI-записей")


# ============================================================
# 7. Удаление из подсистем
# ============================================================

def remove_from_subsystems():
    print("\n=== 7. Удаление отчётов из подсистем ===")

    for subsystem, reports in SUBSYSTEM_REMOVALS.items():
        subsystem_xml = MAIN / "Subsystems" / f"{subsystem}.xml"
        if not subsystem_xml.exists():
            log(f"⚠️ Подсистема не найдена: {subsystem}")
            continue

        if DRY_RUN:
            log(f"[DRY-RUN] Удаление из {subsystem}: {reports}")
            continue

        text = read_text(subsystem_xml)
        for report_name in reports:
            # Удалить строку с Report.{name} из Content
            pattern = re.compile(
                r'\s*<xr:Item xsi:type="xr:MDObjectRef">Report\.' +
                re.escape(report_name) +
                r'</xr:Item>\n?'
            )
            text, count = pattern.subn("", text)
            if count > 0:
                log(f"Удалён Report.{report_name} из подсистемы {subsystem}")
            else:
                log(f"⚠️ Report.{report_name} не найден в {subsystem}")

        write_text(subsystem_xml, text)


# ============================================================
# 8. Проверка BOM
# ============================================================

def check_bom():
    print("\n=== 8. Проверка BOM ===")
    issues = 0

    for ext_name in [NEW_PREFIX + n for n in REPORTS_TO_MIGRATE]:
        template = (EXT / "Reports" / ext_name / "Templates" /
                   "ОсновнаяСхемаКомпоновкиДанных" / "Ext" / "Template.xml")
        if template.exists():
            data = template.read_bytes()
            if data[:6] == b'\xef\xbb\xbf\xef\xbb\xbf':
                log(f"⚠️ Double BOM: {template}")
                template.write_bytes(BOM + data[6:])
                log(f"  → Исправлен")
                issues += 1
            elif data[:3] == BOM:
                log(f"✓ {ext_name} — BOM корректен")
            else:
                log(f"⚠️ {ext_name} — нет BOM")
                issues += 1

    report_xmls = list((EXT / "Reports").glob(f"{NEW_PREFIX}*.xml"))
    for f in report_xmls:
        data = f.read_bytes()
        if data[:6] == b'\xef\xbb\xbf\xef\xbb\xbf':
            log(f"⚠️ Double BOM: {f.name}")
            f.write_bytes(BOM + data[6:])
            log(f"  → Исправлен")
            issues += 1

    if issues == 0:
        log("✓ Все файлы — BOM корректен")


# ============================================================
# Основной процесс
# ============================================================

def main():
    print("=" * 60)
    print("МИГРАЦИЯ ОТЧЁТОВ PTM → PTM_Analytics")
    print(f"Префикс: {OLD_PREFIX} → {NEW_PREFIX}")
    print(f"Отчётов: {len(REPORTS_TO_MIGRATE)}")
    if DRY_RUN:
        print("РЕЖИМ: DRY-RUN (без изменений)")
    print("=" * 60)

    # Проверки
    if not MAIN.exists():
        print(f"ОШИБКА: Не найдена папка {MAIN}")
        sys.exit(1)
    if not EXT.exists():
        print(f"ОШИБКА: Не найдена папка {EXT}")
        sys.exit(1)

    # Проверка что все исходные отчёты существуют
    missing = []
    for name in REPORTS_TO_MIGRATE:
        src = MAIN / "Reports" / name / "Templates" / "ОсновнаяСхемаКомпоновкиДанных" / "Ext" / "Template.xml"
        if not src.exists():
            missing.append(name)
    if missing:
        print(f"ОШИБКА: DCS-шаблоны не найдены: {missing}")
        sys.exit(1)

    # Выполнение
    rename_prefix()
    new_reports = create_reports_in_extension()
    update_ext_configuration_xml(new_reports)
    update_ext_cdi(new_reports)
    remove_from_main_configuration_xml()
    remove_from_main_cdi()
    remove_from_subsystems()
    if not DRY_RUN:
        check_bom()

    print("\n" + "=" * 60)
    print("ГОТОВО!")
    if DRY_RUN:
        print("Это был DRY-RUN. Запустите без --dry-run для применения.")
    else:
        print(f"Создано {len(new_reports)} отчётов в расширении.")
        print(f"Удалено {len(REPORTS_TO_MIGRATE)} отчётов из основной конфигурации.")
        print()
        print("СЛЕДУЮЩИЕ ШАГИ:")
        print("  1. python scripts/deploy_ext.py --ext PTM_Analytics --action Full")
        print("  2. python scripts/_ps_wrapper.py deploy -Action Full -SkipDtBackup -SkipCheck")
        print("  3. В Конфигураторе: добавить отчёты расширения в подсистемы")
        print("  4. python scripts/deploy_ext.py --ext PTM_Analytics --action Dump")
    print("=" * 60)


if __name__ == "__main__":
    main()
