# -*- coding: utf-8 -*-
"""Fix Номенклатура: CodeType=Number, DescriptionLength=150"""
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module")

files = [
    base / "Конфигурация" / "Проверка" / "Catalogs" / "Номенклатура.xml",
    base / "Конфигурация" / "Catalogs" / "Номенклатура.xml",
]

for f in files:
    content = f.read_text(encoding="utf-8")
    
    # 1. CodeType: String → Number
    content = content.replace("<CodeType>String</CodeType>", "<CodeType>Number</CodeType>")
    
    # 2. DescriptionLength: 25 → 150
    content = content.replace("<DescriptionLength>25</DescriptionLength>", "<DescriptionLength>150</DescriptionLength>")
    
    # 3. При числовом коде CodeAllowedLength не нужен — убираем
    # Actually, CodeAllowedLength is for String codes. For Number, it's ignored but doesn't cause errors.
    # Let's leave it — 1C will just ignore it.
    
    f.write_text(content, encoding="utf-8")
    folder = "Проверка" if "Проверка" in str(f) else "Конфигурация"
    print(f"  [OK] {folder}: CodeType=Number, DescriptionLength=150")

print("Done!")
