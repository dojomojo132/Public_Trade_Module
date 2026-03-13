# -*- coding: utf-8 -*-
"""Diagnose missing CDI entries at sub-object level"""
import re
from pathlib import Path

DEV = Path(r"D:\Git\Public_Trade_Module\Конфигурация")
IB = Path(r"D:\Git\Public_Trade_Module\Проверка")

# Read CDI
cdi_path = DEV / "ConfigDumpInfo.xml"
cdi_content = cdi_path.read_text(encoding='utf-8-sig')

# Get all CDI entries for CommonTemplates
cdi_entries = {}
for m in re.finditer(r'<Metadata\s+name="(CommonTemplate\.[^"]+)"[^>]*>', cdi_content):
    name = m.group(1)
    base = name.split('.')[1]  # Template name
    if base not in cdi_entries:
        cdi_entries[base] = []
    cdi_entries[base].append(name)

# Get all CT files in dev
dev_templates = set()
for f in (DEV / "CommonTemplates").iterdir():
    if f.is_file() and f.suffix == '.xml':
        dev_templates.add(f.stem)

print(f"Templates with files: {len(dev_templates)}")
print(f"Templates in CDI: {len(cdi_entries)}")

# Show CDI entry counts for each template
print("\n=== CDI entries per template ===")
for t in sorted(dev_templates):
    entries = cdi_entries.get(t, [])
    # Check if directory/sub-objects exist
    t_dir = DEV / "CommonTemplates" / t
    has_dir = t_dir.exists()
    sub_files = list(t_dir.rglob("*")) if has_dir else []
    print(f"  {t}: {len(entries)} CDI entries, {'DIR exists' if has_dir else 'NO DIR'}, {len(sub_files)} sub-files")
    if len(entries) < 2 and has_dir:
        print(f"    ⚠ POSSIBLY MISSING sub-object CDI entries!")
        # Show what IB dump has
        ib_entries = []
        ib_cdi = IB / "ConfigDumpInfo.xml"
        if ib_cdi.exists():
            ib_content = ib_cdi.read_text(encoding='utf-8-sig')
            for m2 in re.finditer(r'<Metadata\s+name="(CommonTemplate\.' + re.escape(t) + r'[^"]*)"[^>]*>', ib_content):
                ib_entries.append(m2.group(0))
        if ib_entries:
            print(f"    IB has {len(ib_entries)} entries:")
            for e in ib_entries:
                print(f"      {e[:100]}...")

# Find templates missing from CDI entirely
missing = dev_templates - set(cdi_entries.keys())
if missing:
    print(f"\n⚠ Templates COMPLETELY missing from CDI: {sorted(missing)}")

# Find templates with less than 2 CDI entries (likely missing sub-objects)
print(f"\n=== Templates with < 2 CDI entries (potentially incomplete) ===")
count = 0
for t in sorted(dev_templates):
    entries = cdi_entries.get(t, [])
    if len(entries) < 2:
        t_dir = DEV / "CommonTemplates" / t
        if t_dir.exists():
            print(f"  {t}: {len(entries)} entries")
            count += 1
print(f"  Total: {count}")
