# -*- coding: utf-8 -*-
"""
Шаблон для удаления объектов метаданных 1С с кириллицей в путях

ПРОБЛЕМА: PowerShell в VS Code полностью ломает кириллические символы.
РЕШЕНИЕ: Создать .py файл → Запустить через `python script.py`

ИСПОЛЬЗОВАНИЕ:
1. Скопировать этот шаблон в корень проекта (например, _delete_object.py)
2. Заменить {{ИмяОбъекта}} на реальное имя
3. Заменить {{ТипОбъекта}} на тип (DataProcessors, Documents, Catalogs и т.д.)
4. Запустить: python "D:\Git\Public_Trade_Module\_delete_object.py"
5. Удалить временный скрипт после завершения

ПРИМЕР:
    # Удаление обработки ТестРеквизитов:
    files = [
        pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\DataProcessors\ТестРеквизитов.xml"),
        pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\DataProcessors\ТестРеквизитов.xml"),
    ]
    folders = [
        pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\DataProcessors\ТестРеквизитов"),
        pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\DataProcessors\ТестРеквизитов"),
    ]
"""

import pathlib
import shutil

# ═══════════════════════════════════════════════════════════════════
# НАСТРОЙКА: Замените {{ИмяОбъекта}} и {{ТипОбъекта}} на реальные значения
# ═══════════════════════════════════════════════════════════════════

OBJECT_NAME = "{{ИмяОбъекта}}"  # Например: ТестРеквизитов
OBJECT_TYPE = "{{ТипОбъекта}}"  # Например: DataProcessors, Documents, Catalogs

BASE_PATH = r"D:\Git\Public_Trade_Module"

# ═══════════════════════════════════════════════════════════════════
# Файлы для удаления
# ═══════════════════════════════════════════════════════════════════

files = [
    pathlib.Path(BASE_PATH) / "Конфигурация" / "Проверка" / OBJECT_TYPE / f"{OBJECT_NAME}.xml",
    pathlib.Path(BASE_PATH) / "Конфигурация" / OBJECT_TYPE / f"{OBJECT_NAME}.xml",
]

# ═══════════════════════════════════════════════════════════════════
# Папки для удаления (если есть формы/модули)
# ═══════════════════════════════════════════════════════════════════

folders = [
    pathlib.Path(BASE_PATH) / "Конфигурация" / "Проверка" / OBJECT_TYPE / OBJECT_NAME,
    pathlib.Path(BASE_PATH) / "Конфигурация" / OBJECT_TYPE / OBJECT_NAME,
]

# ═══════════════════════════════════════════════════════════════════
# ВЫПОЛНЕНИЕ
# ═══════════════════════════════════════════════════════════════════

def main():
    print("═" * 60)
    print(f"  УДАЛЕНИЕ ОБЪЕКТА: {OBJECT_TYPE}.{OBJECT_NAME}")
    print("═" * 60)
    
    deleted_files = 0
    deleted_folders = 0
    
    # Удаление файлов
    print("\n📄 Удаление файлов...")
    for file_path in files:
        if file_path.exists():
            file_path.unlink()
            print(f"  ✓ {file_path.name}")
            deleted_files += 1
        else:
            print(f"  - {file_path.name} (не найден)")
    
    # Удаление папок
    print("\n📁 Удаление папок...")
    for folder_path in folders:
        if folder_path.exists():
            shutil.rmtree(folder_path)
            print(f"  ✓ {folder_path.name}/")
            deleted_folders += 1
        else:
            print(f"  - {folder_path.name}/ (не найдена)")
    
    # Итог
    print("\n" + "═" * 60)
    print(f"  ИТОГ: Удалено {deleted_files} файлов, {deleted_folders} папок")
    print("═" * 60)
    
    print("\n⚠️  НЕ ЗАБУДЬТЕ:")
    print("  1. Удалить запись из Configuration.xml")
    print("  2. Удалить блок из ConfigDumpInfo.xml")
    print("  3. Запустить validate-config.ps1")
    print()

if __name__ == "__main__":
    main()
