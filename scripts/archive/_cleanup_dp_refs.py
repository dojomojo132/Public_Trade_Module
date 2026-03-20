# -*- coding: utf-8 -*-
"""Clean up references to Анл_МассоваяУстановкаНалоговыхГрупп from config files."""
import pathlib
import re

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Analytics")
DP_NAME = "Анл_МассоваяУстановкаНалоговыхГрупп"

# 1. Configuration.xml — remove <DataProcessor> entry from ChildObjects
cfg = ROOT / "Configuration.xml"
text = cfg.read_text(encoding="utf-8-sig")
old = f"\t\t\t<DataProcessor>{DP_NAME}</DataProcessor>\n"
if old in text:
    text = text.replace(old, "")
    cfg.write_text(text, encoding="utf-8-sig")
    print(f"Configuration.xml: removed DataProcessor entry")
else:
    print(f"Configuration.xml: entry not found")

# Also check InternalInfo for ContainedObject
pattern_co = re.compile(r'\s*<xr:ContainedObject>[^<]*DataProcessor\.' + DP_NAME + r'[^<]*</xr:ContainedObject>\s*\n?', re.DOTALL)
# Actually, let's check for multiline ContainedObject blocks
lines = text.split('\n')
new_lines = []
skip = False
for line in lines:
    if f'DataProcessor.{DP_NAME}' in line:
        skip = True
        print(f"Configuration.xml: removed InternalInfo ContainedObject line")
        continue
    new_lines.append(line)

if len(new_lines) != len(lines):
    cfg.write_text('\n'.join(new_lines), encoding="utf-8-sig")
    text = '\n'.join(new_lines)

# 2. ConfigDumpInfo.xml — remove all Metadata entries
cdi = ROOT / "ConfigDumpInfo.xml"
cdi_text = cdi.read_text(encoding="utf-8-sig")
cdi_lines = cdi_text.split('\n')
cdi_new = [l for l in cdi_lines if DP_NAME not in l]
removed = len(cdi_lines) - len(cdi_new)
if removed > 0:
    cdi.write_text('\n'.join(cdi_new), encoding="utf-8-sig")
    print(f"ConfigDumpInfo.xml: removed {removed} entries")
else:
    print(f"ConfigDumpInfo.xml: no entries found")

# 3. Subsystem — remove Content item
sub = ROOT / "Subsystems" / "Анл_Аналитика.xml"
sub_text = sub.read_text(encoding="utf-8-sig")
# Remove the xr:Item line containing the reference
sub_lines = sub_text.split('\n')
sub_new = [l for l in sub_lines if f'DataProcessor.{DP_NAME}' not in l]
removed_sub = len(sub_lines) - len(sub_new)
if removed_sub > 0:
    sub.write_text('\n'.join(sub_new), encoding="utf-8-sig")
    print(f"Subsystem: removed {removed_sub} content entries")
else:
    print(f"Subsystem: no entries found")

# Verify
print("\nVerification:")
for fname in ["Configuration.xml", "ConfigDumpInfo.xml"]:
    f = ROOT / fname
    t = f.read_text(encoding="utf-8-sig")
    count = t.count(DP_NAME)
    print(f"  {fname}: {count} references remaining")

sub_t = sub.read_text(encoding="utf-8-sig")
print(f"  Subsystem: {sub_t.count(DP_NAME)} references remaining")

print("\nDone!")
