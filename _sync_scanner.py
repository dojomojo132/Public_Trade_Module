# -*- coding: utf-8 -*-
import shutil
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
proverka = base / "Проверка"

files = [
    "Catalogs/Номенклатура/Forms/ФормаСписка/Ext/Form.xml",
    "Catalogs/Номенклатура/Forms/ФормаСписка/Ext/Form/Module.bsl",
]

for f in files:
    src = base / f
    dst = proverka / f
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dst))
        print(f"  ✓ {f}")
    else:
        print(f"  ✗ {f} (не найден)")

print("\nСинхронизация завершена.")
