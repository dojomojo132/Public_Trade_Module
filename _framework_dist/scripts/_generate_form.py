# -*- coding: utf-8 -*-
"""
Генератор форм 1С из бинарных шаблонов.
Создаёт дескриптор, Form.xml и Module.bsl с правильным BOM + CRLF.

Использование:
    python scripts/_generate_form.py --type catalog-element --object Номенклатура --form ФормаЭлемента
    python scripts/_generate_form.py --type catalog-group --object Номенклатура --form ФормаГруппы
    python scripts/_generate_form.py --type catalog-list --object Номенклатура --form ФормаСписка
    python scripts/_generate_form.py --type document --object ПриходТовара --form ФормаДокумента
    python scripts/_generate_form.py --type dataprocessor --object ИмпортНоменклатуры --form Форма

    # Только проверить шаблоны:
    python scripts/_generate_form.py --check

    # Сухой запуск (показать что будет создано, без записи):
    python scripts/_generate_form.py --type document --object Тест --form ФормаДокумента --dry-run
"""

import argparse
import pathlib
import uuid
import secrets
import sys
import re

# === КОНСТАНТЫ ===

BOM = b'\xef\xbb\xbf'

PROJECT_ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
TEMPLATES_DIR = PROJECT_ROOT / "Документация" / "Шаблоны" / "binary"

# Путь конфигурации
CONFIG_PATHS = [
    PROJECT_ROOT / "Конфигурация",
]

# Маппинг тип формы → файл шаблона Form.xml
FORM_TEMPLATES = {
    "catalog-element": "catalog-element.xml",
    "catalog-group":   "catalog-group.xml",
    "catalog-list":    "catalog-list.xml",
    "document":        "document.xml",
    "dataprocessor":   "dataprocessor.xml",
}

# Маппинг тип формы → папка объектов
TYPE_FOLDERS = {
    "catalog-element": "Catalogs",
    "catalog-group":   "Catalogs",
    "catalog-list":    "Catalogs",
    "document":        "Documents",
    "dataprocessor":   "DataProcessors",
}

# Маппинг тип формы → метатип для list-form MainTable
META_TYPE_MAP = {
    "catalog-element": "Catalog",
    "catalog-group":   "Catalog",
    "catalog-list":    "Catalog",
    "document":        "Document",
    "dataprocessor":   "DataProcessor",
}

# Маппинг тип формы → свойство DefaultForm в родительском .xml
DEFAULT_FORM_PROPERTY = {
    "catalog-element": "DefaultObjectForm",
    "catalog-group":   "DefaultFolderForm",
    "catalog-list":    "DefaultListForm",
    "document":        "DefaultObjectForm",
    "dataprocessor":   "DefaultObjectForm",
}

# Тип метаданных для ConfigDumpInfo
CDI_META_TYPE = {
    "catalog-element": "Catalog",
    "catalog-group":   "Catalog",
    "catalog-list":    "Catalog",
    "document":        "Document",
    "dataprocessor":   "DataProcessor",
}


def generate_uuid():
    """Генерирует UUID v4 в lowercase."""
    return str(uuid.uuid4())


def generate_config_version():
    """Генерирует configVersion для ConfigDumpInfo (32 hex + 00000000)."""
    return secrets.token_hex(16) + "00000000"


def form_synonym(form_name):
    """
    Преобразует CamelCase имя формы в читаемый синоним.
    ФормаДокумента → Форма документа
    ФормаГруппы → Форма группы
    ФормаЭлемента → Форма элемента
    ФормаСписка → Форма списка
    """
    # Разбиваем CamelCase
    parts = re.findall(r'[А-ЯЁA-Z][а-яёa-z0-9]*', form_name)
    if not parts:
        return form_name
    # Первое слово с заглавной, остальные — со строчной
    result = parts[0]
    for part in parts[1:]:
        result += " " + part.lower()
    return result


def write_bom_file(path, content):
    """
    Записывает файл с BOM (3 байта: ef bb bf) + CRLF + UTF-8.
    Это ЕДИНСТВЕННЫЙ корректный способ записи XML/BSL для 1С.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    # Нормализуем окончания строк в CRLF
    content = content.replace('\r\n', '\n').replace('\n', '\r\n')
    raw_bytes = BOM + content.encode('utf-8')
    path.write_bytes(raw_bytes)
    return len(raw_bytes)


def read_template(template_name):
    """Читает шаблон из директории binary/."""
    template_path = TEMPLATES_DIR / template_name
    if not template_path.exists():
        print(f"  ОШИБКА: Шаблон не найден: {template_path}")
        sys.exit(1)
    # Читаем как bytes, пропускаем BOM если есть
    raw = template_path.read_bytes()
    if raw.startswith(BOM):
        raw = raw[3:]
    return raw.decode('utf-8')


def check_templates():
    """Проверяет наличие всех шаблонов."""
    print("=== Проверка шаблонов ===\n")
    all_ok = True
    
    templates_to_check = ["descriptor.xml"] + list(FORM_TEMPLATES.values()) + ["module-form.bsl"]
    
    for name in templates_to_check:
        path = TEMPLATES_DIR / name
        if path.exists():
            size = path.stat().st_size
            # Проверяем что содержит плейсхолдеры
            content = path.read_text(encoding='utf-8-sig')
            placeholders = re.findall(r'\{\{(\w+)\}\}', content)
            ph_str = ", ".join(placeholders) if placeholders else "(нет плейсхолдеров)"
            print(f"  ✓ {name:30s} [{size:5d} байт]  Плейсхолдеры: {ph_str}")
        else:
            print(f"  ✗ {name:30s} — НЕ НАЙДЕН!")
            all_ok = False
    
    print()
    if all_ok:
        print("Все шаблоны на месте.")
    else:
        print("ОШИБКА: Не все шаблоны найдены!")
    return all_ok


def generate_form(form_type, object_name, form_name, dry_run=False):
    """
    Генерирует полный набор файлов формы.
    
    Создаёт:
    1. Дескриптор: {TypeFolder}/{Object}/Forms/{FormName}.xml
    2. Form.xml:   {TypeFolder}/{Object}/Forms/{FormName}/Ext/Form.xml
    3. Module.bsl: {TypeFolder}/{Object}/Forms/{FormName}/Ext/Form/Module.bsl
    """
    
    form_uuid = generate_uuid()
    type_folder = TYPE_FOLDERS[form_type]
    meta_type = META_TYPE_MAP[form_type]
    synonym = form_synonym(form_name)
    
    print(f"\n{'='*60}")
    print(f"  Генерация формы: {form_name}")
    print(f"  Тип: {form_type}")
    print(f"  Объект: {object_name}")
    print(f"  UUID: {form_uuid}")
    print(f"  Синоним: {synonym}")
    print(f"{'='*60}\n")
    
    # === 1. Дескриптор ===
    descriptor_template = read_template("descriptor.xml")
    descriptor_content = descriptor_template \
        .replace("{{FORM_UUID}}", form_uuid) \
        .replace("{{FORM_NAME}}", form_name) \
        .replace("{{FORM_SYNONYM}}", synonym)
    
    # === 2. Form.xml ===
    form_template = read_template(FORM_TEMPLATES[form_type])
    form_content = form_template \
        .replace("{{OBJECT_NAME}}", object_name) \
        .replace("{{META_TYPE}}", meta_type)
    
    # === 3. Module.bsl ===
    module_content = read_template("module-form.bsl")
    
    # === Записываем в оба пути ===
    files_created = []
    
    for base_path in CONFIG_PATHS:
        forms_dir = base_path / type_folder / object_name / "Forms"
        
        descriptor_path = forms_dir / f"{form_name}.xml"
        form_xml_path = forms_dir / form_name / "Ext" / "Form.xml"
        module_path = forms_dir / form_name / "Ext" / "Form" / "Module.bsl"
        
        if dry_run:
            print(f"  [DRY RUN] {descriptor_path}")
            print(f"  [DRY RUN] {form_xml_path}")
            print(f"  [DRY RUN] {module_path}")
        else:
            # Проверяем что не перезаписываем существующие файлы
            for p in [descriptor_path, form_xml_path, module_path]:
                if p.exists():
                    print(f"  ⚠ ФАЙЛ УЖЕ СУЩЕСТВУЕТ: {p}")
                    print(f"    Используйте --force для перезаписи")
                    # Продолжаем, но предупреждаем
            
            size1 = write_bom_file(descriptor_path, descriptor_content)
            size2 = write_bom_file(form_xml_path, form_content)
            size3 = write_bom_file(module_path, module_content)
            
            files_created.extend([
                (descriptor_path, size1),
                (form_xml_path, size2),
                (module_path, size3),
            ])
            
            rel = base_path.relative_to(PROJECT_ROOT)
            print(f"  ✓ {rel}/{type_folder}/{object_name}/Forms/{form_name}.xml [{size1} байт]")
            print(f"  ✓ {rel}/{type_folder}/{object_name}/Forms/{form_name}/Ext/Form.xml [{size2} байт]")
            print(f"  ✓ {rel}/{type_folder}/{object_name}/Forms/{form_name}/Ext/Form/Module.bsl [{size3} байт]")
        print()
    
    # === Верификация BOM ===
    if not dry_run and files_created:
        print("--- Верификация BOM ---")
        all_bom_ok = True
        for fpath, _ in files_created:
            raw = fpath.read_bytes()[:3]
            if raw == BOM:
                print(f"  ✓ BOM OK: {fpath.name}")
            else:
                print(f"  ✗ BOM ОШИБКА: {fpath.name} — первые 3 байта: {raw.hex()}")
                all_bom_ok = False
        
        if all_bom_ok:
            print("  Все файлы имеют корректный BOM (ef bb bf)")
        print()
    
    # === Чеклист ===
    cdi_type = CDI_META_TYPE[form_type]
    default_form_prop = DEFAULT_FORM_PROPERTY[form_type]
    
    print("=" * 60)
    print("  ЧЕКЛИСТ — обновите вручную (или через агента):")
    print("=" * 60)
    print()
    print(f"  1. {type_folder}/{object_name}.xml → <ChildObjects>:")
    print(f"     Добавить: <Form>{form_name}</Form>")
    print()
    print(f"  2. {type_folder}/{object_name}.xml → <Properties>:")
    print(f"     Установить: <{default_form_prop}>{cdi_type}.{object_name}.Form.{form_name}</{default_form_prop}>")
    print()
    print(f"  3. ConfigDumpInfo.xml:")
    print(f"     В секции <Metadata name=\"{cdi_type}.{object_name}\" ...> добавить:")
    print(f"     <Metadata name=\"{cdi_type}.{object_name}.Form.{form_name}\" id=\"{form_uuid}\"/>")
    print()
    print(f"  4. Запустить: validate-config.ps1")
    print(f"  5. Запустить: deploy-config.ps1 -Action Full")
    print()
    
    return {
        "form_uuid": form_uuid,
        "form_name": form_name,
        "object_name": object_name,
        "form_type": form_type,
        "type_folder": type_folder,
        "meta_type": meta_type,
        "cdi_type": cdi_type,
        "default_form_prop": default_form_prop,
        "files_created": len(files_created),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Генератор форм 1С из бинарных шаблонов",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Типы форм:
  catalog-element   — Форма элемента справочника (UseForFoldersAndItems=Items)
  catalog-group     — Форма группы справочника (UseForFoldersAndItems=Folders)
  catalog-list      — Форма списка справочника (DynamicList)
  document          — Форма документа (AutoTime, PostingMode, RegisterRecords)
  dataprocessor     — Форма обработки (DataProcessorObject)

Примеры:
  %(prog)s --type catalog-element --object Контрагенты --form ФормаЭлемента
  %(prog)s --type document --object РасходТовара --form ФормаДокумента
  %(prog)s --check
  %(prog)s --type catalog-list --object Склады --form ФормаСписка --dry-run
        """
    )
    
    parser.add_argument("--type", "-t", choices=list(FORM_TEMPLATES.keys()),
                        help="Тип формы")
    parser.add_argument("--object", "-o",
                        help="Имя объекта-владельца (например: Номенклатура)")
    parser.add_argument("--form", "-f",
                        help="Имя формы (например: ФормаЭлемента)")
    parser.add_argument("--dry-run", "-n", action="store_true",
                        help="Показать что будет создано, без записи")
    parser.add_argument("--check", "-c", action="store_true",
                        help="Проверить наличие всех шаблонов")
    
    args = parser.parse_args()
    
    if args.check:
        check_templates()
        return
    
    if not args.type or not args.object or not args.form:
        parser.error("Требуются --type, --object и --form (или --check)")
    
    result = generate_form(args.type, args.object, args.form, dry_run=args.dry_run)
    
    if not args.dry_run:
        print(f"Готово! Создано {result['files_created']} файлов.")
        print(f"UUID формы: {result['form_uuid']}")
    else:
        print("[DRY RUN] Файлы НЕ были записаны.")


if __name__ == "__main__":
    main()
