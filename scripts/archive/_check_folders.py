# -*- coding: utf-8 -*-
import pathlib

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")

# Проверяем подозрительные папки
suspect_folders = [
    ROOT / "окументация",
    ROOT / "Тесты",
    ROOT / "_archive",
    ROOT / "_saved_import",
    ROOT / "_test_content_backup",
    ROOT / "CF",
    ROOT / "Import data",
    ROOT / "PTM",
    ROOT / "ScannerEmulator",
]

for folder in suspect_folders:
    if folder.exists():
        items = list(folder.rglob("*"))
        files = [i for i in items if i.is_file()]
        dirs = [i for i in items if i.is_dir()]
        print(f"\n📁 {folder.name}/")
        print(f"   Папок: {len(dirs)}, Файлов: {len(files)}")
        # Показать первые 10 файлов
        for f in sorted(files)[:5]:
            print(f"   - {f.relative_to(folder)}")
        if len(files) > 5:
            print(f"   ... и ещё {len(files)-5} файлов")
    else:
        print(f"\n❌ {folder.name}/ - НЕ НАЙДЕНА")
