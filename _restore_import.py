# -*- coding: utf-8 -*-
"""Restore improved ИмпортНоменклатуры files from _saved_import/"""
import pathlib
import shutil

BASE = pathlib.Path(r"D:\Git\Public_Trade_Module")
SAVED = BASE / "_saved_import"
KONF = BASE / "Конфигурация"
PROV = KONF / "Проверка"

# Mapping: saved file → destination relative to DataProcessors/ИмпортНоменклатуры/
mappings = {
    "ObjectModule.bsl": "Ext/ObjectModule.bsl",  
    "FormModule.bsl": "Forms/Форма/Ext/Form/Module.bsl",
    "FormXml.xml": "Forms/Форма/Ext/Form.xml",
    "DataProcessorXml.xml": None,  # goes to DataProcessors/ИмпортНоменклатуры.xml
}

for saved_name, rel_dest in mappings.items():
    src = SAVED / saved_name
    if not src.exists():
        print(f"  SKIP {saved_name} — not found")
        continue
    
    content = src.read_bytes()
    
    if rel_dest is None:
        # This is the main XML file
        for base in [KONF, PROV]:
            dest = base / "DataProcessors" / "ИмпортНоменклатуры.xml"
            dest.write_bytes(content)
            print(f"  ✓ {saved_name} → {dest.relative_to(BASE)}")
    else:
        for base in [KONF, PROV]:
            dest = base / "DataProcessors" / "ИмпортНоменклатуры" / rel_dest
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content)
            print(f"  ✓ {saved_name} → {dest.relative_to(BASE)}")

# Also check if CDI needs updating for ИмпортНоменклатуры
# Compare current CDI with saved CDI reference
print("\n=== Checking CDI entries ===")
cdi_current = (KONF / "ConfigDumpInfo.xml").read_text(encoding='utf-8')
if "ИмпортНоменклатуры" in cdi_current:
    print("  ИмпортНоменклатуры already in CDI")
else:
    print("  WARNING: ИмпортНоменклатуры NOT in CDI!")

# Check Configuration.xml
config = (KONF / "Configuration.xml").read_text(encoding='utf-8')
if "ИмпортНоменклатуры" in config:
    print("  ИмпортНоменклатуры already in Configuration.xml")
else:
    print("  WARNING: ИмпортНоменклатуры NOT in Configuration.xml!")

print("\nDone!")
