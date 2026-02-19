# -*- coding: utf-8 -*-
"""Remove UsePurposes from Configuration.xml - it was added by BPO merge 
and is not compatible with the current XDTO schema."""
import pathlib
import re

REPO = pathlib.Path(r"D:\Git\Public_Trade_Module")

for folder in ["Конфигурация", "Конфигурация/Проверка"]:
    config_path = REPO / folder / "Configuration.xml"
    if not config_path.exists():
        continue
    
    content = config_path.read_text(encoding="utf-8")
    
    # Remove UsePurposes block
    pattern = r'\s*<UsePurposes>.*?</UsePurposes>'
    new_content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    if new_content != content:
        config_path.write_text(new_content, encoding="utf-8")
        print(f"✓ {folder}: Удалён блок UsePurposes")
    else:
        print(f"- {folder}: UsePurposes не найден")

print("\n✓ Готово!")
