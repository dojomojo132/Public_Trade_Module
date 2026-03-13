"""Fix CDI: move nested _ru main entries to top level under ConfigVersions."""
import xml.etree.ElementTree as ET
from pathlib import Path
import shutil

CDI = Path(r"D:\Git\Public_Trade_Module\Конфигурация\ConfigDumpInfo.xml")

# Backup
shutil.copy2(CDI, CDI.with_suffix(".xml.bak_ru"))

tree = ET.parse(CDI)
root = tree.getroot()

ns = "http://v8.1c.ru/8.3/xcf/dumpinfo"
ET.register_namespace("", ns)

cv = root.find(f"{{{ns}}}ConfigVersions")
if cv is None:
    print("ConfigVersions not found!")
    exit(1)

# Find all Metadata elements recursively
all_meta = list(root.iter(f"{{{ns}}}Metadata"))
print(f"Total Metadata elements: {len(all_meta)}")

# Top-level entries (direct children of ConfigVersions)
top_level_names = set()
for child in cv:
    if child.tag == f"{{{ns}}}Metadata":
        name = child.get("name", "")
        top_level_names.add(name)

print(f"Top-level entries: {len(top_level_names)}")

# Find nested _ru main entries (name ends with _ru, not at top level)
nested_ru = []
for m in all_meta:
    name = m.get("name", "")
    if name.endswith("_ru") and name not in top_level_names:
        nested_ru.append(m)

print(f"Nested _ru main entries to promote: {len(nested_ru)}")

# Remove them from their parents and add to ConfigVersions
promoted = 0
for m in nested_ru:
    # Find parent
    for parent in root.iter():
        if m in list(parent):
            parent.remove(m)
            cv.append(m)
            promoted += 1
            print(f"  Promoted: {m.get('name')}")
            break

print(f"\nPromoted {promoted} entries to top level")

# Also check: are there _ru.Template entries that are nested?
nested_ru_tmpl = []
for m in all_meta:
    name = m.get("name", "")
    if "_ru.Template" in name and name not in top_level_names:
        # Check if it's top-level now (might have been promoted alongside)
        is_top = False
        for child in cv:
            if child is m:
                is_top = True
                break
        if not is_top:
            nested_ru_tmpl.append(m)

if nested_ru_tmpl:
    print(f"\nNested _ru.Template entries to promote: {len(nested_ru_tmpl)}")
    for m in nested_ru_tmpl:
        for parent in root.iter():
            if m in list(parent):
                parent.remove(m)
                cv.append(m)
                print(f"  Promoted: {m.get('name')}")
                break

# Write back
tree.write(CDI, xml_declaration=True, encoding="UTF-8")

# Verify
tree2 = ET.parse(CDI)
root2 = tree2.getroot()
cv2 = root2.find(f"{{{ns}}}ConfigVersions")
top2 = [c for c in cv2 if c.tag == f"{{{ns}}}Metadata"]
ru_top2 = [c for c in top2 if c.get("name", "").endswith("_ru")]
print(f"\nAfter fix: {len(top2)} top-level entries, {len(ru_top2)} _ru main entries at top level")
