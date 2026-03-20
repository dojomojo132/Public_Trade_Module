# -*- coding: utf-8 -*-
import shutil, pathlib

src = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Driver_Vchasno\DataProcessors\Вчсн_КассаПанель\Forms\Форма\Ext\Form\Module.bsl")
dst = pathlib.Path(r"D:\Git\Public_Trade_Module\scripts\archive\_Module_backup.bsl")

shutil.copy2(src, dst)
print(f"Backed up {src.name} -> {dst}")

# Now replace with empty module (BOM + CRLF)
empty = "\ufeff\r\n"
src.write_text(empty, encoding="utf-8-sig", newline="")
print(f"Replaced {src.name} with empty module")
