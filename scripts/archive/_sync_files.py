# -*- coding: utf-8 -*-
import pathlib
import shutil

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
src = base / "Проверка"

# Files to copy from Проверка to main Конфигурация
copies = [
    # Номенклатура ФормаЭлемента Form.xml
    ("Catalogs/Номенклатура/Forms/ФормаЭлемента/Ext/Form.xml",
     "Catalogs/Номенклатура/Forms/ФормаЭлемента/Ext/Form.xml"),
    # УправлениеНастройками Module.bsl
    ("DataProcessors/УправлениеНастройками/Forms/Форма/Ext/Form/Module.bsl",
     "DataProcessors/УправлениеНастройками/Forms/Форма/Ext/Form/Module.bsl"),
    # УправлениеНастройками Form.xml
    ("DataProcessors/УправлениеНастройками/Forms/Форма/Ext/Form.xml",
     "DataProcessors/УправлениеНастройками/Forms/Форма/Ext/Form.xml"),
    # РабочееМестоКассира Module.bsl
    ("DataProcessors/РабочееМестоКассира/Forms/Форма/Ext/Form/Module.bsl",
     "DataProcessors/РабочееМестоКассира/Forms/Форма/Ext/Form/Module.bsl"),
]

print("Copying files from Проверка/ to main Конфигурация/...")
for src_rel, dst_rel in copies:
    src_path = src / src_rel
    dst_path = base / dst_rel
    if src_path.exists():
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)
        print(f"  ✓ {dst_rel}")
    else:
        print(f"  ✗ SOURCE NOT FOUND: {src_rel}")

print("\nDone!")
