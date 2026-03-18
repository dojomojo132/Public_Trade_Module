"""Fix XML format of PTM_Driver_Emulator extension to match platform canonical format."""
import pathlib
import re

BASE = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Driver_Emulator")

# --- 1. Language: rewrite to canonical format ---
lang = BASE / "Languages" / "Русский.xml"
# Read current to extract UUID
txt = lang.read_text(encoding="utf-8")
m = re.search(r'uuid="([^"]+)"', txt)
lang_uuid = m.group(1) if m else "ff143173-71b7-4385-9abd-be966c1a5001"

LANG_XML = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses"'
    ' xmlns:app="http://v8.1c.ru/8.2/managed-application/core"'
    ' xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config"'
    ' xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi"'
    ' xmlns:ent="http://v8.1c.ru/8.1/data/enterprise"'
    ' xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform"'
    ' xmlns:style="http://v8.1c.ru/8.1/data/ui/style"'
    ' xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system"'
    ' xmlns:v8="http://v8.1c.ru/8.1/data/core"'
    ' xmlns:v8ui="http://v8.1c.ru/8.1/data/ui"'
    ' xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web"'
    ' xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows"'
    ' xmlns:xen="http://v8.1c.ru/8.3/xcf/enums"'
    ' xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef"'
    ' xmlns:xr="http://v8.1c.ru/8.3/xcf/readable"'
    ' xmlns:xs="http://www.w3.org/2001/XMLSchema"'
    ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
    ' version="2.20">\n'
    f'\t<Language uuid="{lang_uuid}">\n'
    '\t\t<InternalInfo/>\n'
    '\t\t<Properties>\n'
    '\t\t\t<ObjectBelonging>Adopted</ObjectBelonging>\n'
    '\t\t\t<Name>Русский</Name>\n'
    '\t\t\t<Comment/>\n'
    '\t\t</Properties>\n'
    '\t</Language>\n'
    '</MetaDataObject>'
)
lang.write_text(LANG_XML, encoding="utf-8")
print(f"[OK] Language: rewritten to canonical format (uuid={lang_uuid})")

# --- 2. Remove version="2.20" from child elements ---
CHILD_TAGS = r"(?:Role|Subsystem|CommonModule|Language|DataProcessor)"
for f in BASE.rglob("*.xml"):
    if f.name in ("Configuration.xml", "ConfigDumpInfo.xml"):
        continue
    if f.name == "Русский.xml":
        continue  # Already fixed
    txt = f.read_text(encoding="utf-8")
    new_txt = re.sub(
        rf'(<{CHILD_TAGS}\s+uuid="[^"]+") version="2\.20"',
        r"\1",
        txt,
    )
    if new_txt != txt:
        f.write_text(new_txt, encoding="utf-8")
        print(f"[OK] {f.name}: removed version attribute")
    else:
        print(f"[--] {f.name}: no version attribute found (already OK)")

print("\nDone.")
