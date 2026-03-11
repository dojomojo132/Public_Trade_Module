# -*- coding: utf-8 -*-
"""
Удаление неиспользуемых CommonTemplates из конфигурации PTM.
Удаляет:
  1. XML-элементы из Configuration.xml
  2. Записи из ConfigDumpInfo.xml
  3. Записи из подсистем
  4. Папки и дескрипторы с диска
"""
import os
import re
import shutil
import pathlib

ROOT = pathlib.Path(r'd:\Git\Public_Trade_Module')
CONFIG_DIR = ROOT / 'Конфигурация'
CHECK_DIR = CONFIG_DIR / 'Проверка'

# ===== СПИСКИ =====
# Шаблоны, которые ОСТАВЛЯЕМ (используются в BSL + в каталоге ДрайверыОборудования)
KEEP = {
    # BSL-зависимые (13)
    'КомпонентаИнтеграцииНСПК',
    'Драйвер1СПринтерЧеков',
    'Драйвер1СДисплейПокупателя',
    'ДрайверМертехРаспознавательMertechAI',
    'Драйвер1СУстройстваВводаNative',
    'Драйвер1СЭлектронныеВесы',
    'КомпонентаПечатиШтрихкодов',
    'КомпонентаHttpBridge',
    'Драйвер1ССканер',
    'ШаблонДисплеяПокупателя',
    'КодВидаНоменклатурнойКлассификации',
    'СертификатыНУЦМинцифры_ru',
    'ШаблонДисплеяПокупателяЧек',
    # Каталог ДрайверыОборудования (4)
    'ДрайверАТОЛУстройстваВвода8X_ru',
    'ДрайверМассаКЭлектронныеВесыИСПечатьюЭтикеток_ru',
    'ДрайверМертехВесыСПечатьюЭтикетокРаспознаватель_ru',
    'ДрайверЭвоторККТ54ФЗ_ru',
}

def get_all_templates(base_dir):
    """Получить все шаблоны с диска"""
    ct_dir = base_dir / 'CommonTemplates'
    if not ct_dir.exists():
        return []
    return [d.name for d in ct_dir.iterdir() if d.is_dir()]

def get_remove_list(base_dir):
    """Получить список шаблонов к удалению"""
    all_templates = get_all_templates(base_dir)
    return [t for t in all_templates if t not in KEEP]

def remove_from_configuration_xml(config_xml_path, remove_list):
    """Удалить <CommonTemplate>ИМЯ</CommonTemplate> из Configuration.xml"""
    content = config_xml_path.read_text(encoding='utf-8-sig')
    original_len = len(content)
    removed = 0
    
    for name in remove_list:
        # Паттерн: <CommonTemplate>ИМЯ</CommonTemplate> с опциональными пробелами/табами
        pattern = r'\s*<CommonTemplate>' + re.escape(name) + r'</CommonTemplate>'
        new_content, count = re.subn(pattern, '', content)
        if count > 0:
            content = new_content
            removed += count
    
    if removed > 0:
        config_xml_path.write_text(content, encoding='utf-8-sig')
    
    print(f"  Configuration.xml: удалено {removed} записей ({original_len - len(content)} байт)")
    return removed

def remove_from_configdumpinfo(cdi_path, remove_list):
    """Удалить записи CommonTemplate.ИМЯ из ConfigDumpInfo.xml"""
    content = cdi_path.read_text(encoding='utf-8-sig')
    original_len = len(content)
    removed = 0
    
    for name in remove_list:
        # Записи могут быть в разных форматах, ищем все с CommonTemplate.ИМЯ
        # Паттерн: строки содержащие CommonTemplate.ИМЯ (одна или несколько)
        patterns = [
            # <Metadata name="CommonTemplate.ИМЯ" ... />
            r'\s*<Metadata[^>]*name="CommonTemplate\.' + re.escape(name) + r'"[^>]*/>\s*',
            # <Metadata name="CommonTemplate.ИМЯ" ...>...</Metadata>
            r'\s*<Metadata[^>]*name="CommonTemplate\.' + re.escape(name) + r'"[^>]*>.*?</Metadata>\s*',
        ]
        for pattern in patterns:
            new_content, count = re.subn(pattern, '\n', content, flags=re.DOTALL)
            if count > 0:
                content = new_content
                removed += count
    
    if removed > 0:
        cdi_path.write_text(content, encoding='utf-8-sig')
    
    print(f"  ConfigDumpInfo.xml: удалено {removed} записей ({original_len - len(content)} байт)")
    return removed

def remove_from_subsystems(base_dir, remove_list):
    """Удалить <Item>CommonTemplate.ИМЯ</Item> из XML подсистем"""
    subsys_dir = base_dir / 'Subsystems'
    if not subsys_dir.exists():
        print("  Подсистемы: каталог не найден")
        return 0
    
    total_removed = 0
    for xml_file in subsys_dir.rglob('*.xml'):
        try:
            content = xml_file.read_text(encoding='utf-8-sig')
        except:
            continue
        
        if 'CommonTemplate' not in content:
            continue
        
        original = content
        for name in remove_list:
            pattern = r'\s*<Item>CommonTemplate\.' + re.escape(name) + r'</Item>'
            content, count = re.subn(pattern, '', content)
            total_removed += count
        
        if content != original:
            xml_file.write_text(content, encoding='utf-8-sig')
            print(f"  Подсистема: {xml_file.relative_to(base_dir)}")
    
    print(f"  Подсистемы: удалено {total_removed} записей")
    return total_removed

def remove_files(base_dir, remove_list):
    """Удалить папки и дескрипторы шаблонов"""
    ct_dir = base_dir / 'CommonTemplates'
    removed_dirs = 0
    removed_xmls = 0
    freed_bytes = 0
    
    for name in remove_list:
        # Удалить папку
        folder = ct_dir / name
        if folder.exists() and folder.is_dir():
            size = sum(f.stat().st_size for f in folder.rglob('*') if f.is_file())
            freed_bytes += size
            shutil.rmtree(folder)
            removed_dirs += 1
        
        # Удалить дескриптор XML
        xml_file = ct_dir / f'{name}.xml'
        if xml_file.exists():
            freed_bytes += xml_file.stat().st_size
            xml_file.unlink()
            removed_xmls += 1
    
    print(f"  Файлы: удалено {removed_dirs} папок + {removed_xmls} XML = {freed_bytes/1024/1024:.1f} МБ")
    return removed_dirs

def main():
    remove_list = get_remove_list(CONFIG_DIR)
    print(f"=== Удаление {len(remove_list)} неиспользуемых CommonTemplates ===")
    print(f"Оставляем: {len(KEEP)} шаблонов")
    print()
    
    # Обработка основной папки
    print("--- Конфигурация/ ---")
    config_xml = CONFIG_DIR / 'Configuration.xml'
    cdi_xml = CONFIG_DIR / 'ConfigDumpInfo.xml'
    
    if config_xml.exists():
        remove_from_configuration_xml(config_xml, remove_list)
    if cdi_xml.exists():
        remove_from_configdumpinfo(cdi_xml, remove_list)
    remove_from_subsystems(CONFIG_DIR, remove_list)
    remove_files(CONFIG_DIR, remove_list)
    
    # Обработка папки Проверка/
    print()
    print("--- Конфигурация/Проверка/ ---")
    check_config_xml = CHECK_DIR / 'Configuration.xml'
    check_cdi_xml = CHECK_DIR / 'ConfigDumpInfo.xml'
    
    if check_config_xml.exists():
        remove_from_configuration_xml(check_config_xml, remove_list)
    if check_cdi_xml.exists():
        remove_from_configdumpinfo(check_cdi_xml, remove_list)
    remove_from_subsystems(CHECK_DIR, remove_list)
    remove_files(CHECK_DIR, remove_list)
    
    # Итог
    print()
    remaining = get_all_templates(CONFIG_DIR)
    print(f"=== ИТОГ ===")
    print(f"Удалено шаблонов: {len(remove_list)}")
    print(f"Осталось шаблонов: {len(remaining)}")
    print(f"Оставшиеся: {', '.join(sorted(remaining))}")

if __name__ == '__main__':
    main()
