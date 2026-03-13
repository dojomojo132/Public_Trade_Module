"""Check CDI structure: are _ru entries top-level or nested?"""
import xml.etree.ElementTree as ET
from pathlib import Path

CDI = Path(r"D:\Git\Public_Trade_Module\Конфигурация\ConfigDumpInfo.xml")
tree = ET.parse(CDI)
root = tree.getroot()

ns = {"di": "http://v8.1c.ru/8.3/xcf/dumpinfo"}

# Find ConfigVersions
cv = root.find("di:ConfigVersions", ns)
if cv is None:
    # Try without namespace
    cv = root.find("ConfigVersions")
    if cv is None:
        print("ConfigVersions not found!")
        import sys; sys.exit(1)

# Count top-level Metadata entries
top_level = cv.findall("di:Metadata", ns)
if not top_level:
    top_level = cv.findall("Metadata")

print(f"Top-level Metadata entries: {len(top_level)}")

# Check which _ru templates are top-level
ru_top = [m for m in top_level if m.get("name", "").endswith("_ru")]
ru_top_tmpl = [m for m in top_level if "_ru." in m.get("name", "")]
print(f"_ru main entries at top level: {len(ru_top)}")
print(f"_ru.Template entries at top level: {len(ru_top_tmpl)}")

# Now check ALL Metadata anywhere via recursive search
all_meta = root.findall(".//di:Metadata", ns)
if not all_meta:
    all_meta = root.findall(".//{http://v8.1c.ru/8.3/xcf/dumpinfo}Metadata")
if not all_meta:
    # Try no namespace
    all_meta = root.findall(".//Metadata")
    
print(f"\nAll Metadata entries (recursive): {len(all_meta)}")

ru_all = [m for m in all_meta if m.get("name", "").endswith("_ru")]
ru_all_tmpl = [m for m in all_meta if "_ru." in m.get("name", "")]
print(f"_ru main entries (recursive): {len(ru_all)}")
print(f"_ru.xxx entries (recursive): {len(ru_all_tmpl)}")

# Sample: print first 5 top-level entries and check if _ru is among them
print("\n=== Sample top-level entries (first 10) ===")
for m in top_level[:10]:
    print(f"  {m.get('name')}")

# Print _ru top-level entries if any
if ru_top:
    print(f"\n=== _ru top-level entries (first 5) ===")
    for m in ru_top[:5]:
        print(f"  {m.get('name')}")
else:
    print("\n!!! NO _ru entries at top level - they are nested !!!")
    # Find where they are
    for m in ru_all[:3]:
        # Find parent
        parent = None
        for p in root.iter():
            if m in list(p):
                parent = p
                break
        if parent is not None:
            print(f"  {m.get('name')} -> parent tag={parent.tag}, parent name={parent.get('name', 'N/A')}")
