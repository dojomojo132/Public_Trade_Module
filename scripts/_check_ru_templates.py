"""Check _ru templates: folders, Configuration.xml, ConfigDumpInfo.xml alignment."""
import os
import re
from pathlib import Path

ROOT = Path(r"D:\Git\Public_Trade_Module\Конфигурация")
CT_DIR = ROOT / "CommonTemplates"
CONFIG = ROOT / "Configuration.xml"
CDI = ROOT / "ConfigDumpInfo.xml"

# 1. _ru folders on disk
ru_folders = sorted(d for d in os.listdir(CT_DIR) if os.path.isdir(CT_DIR / d) and d.endswith("_ru"))
print(f"=== _ru folders on disk: {len(ru_folders)} ===")
for f in ru_folders:
    print(f"  {f}")

# 2. _ru entries in Configuration.xml
config_text = CONFIG.read_text(encoding="utf-8-sig")
ru_in_config = sorted(set(re.findall(r"<CommonTemplate>(\S+_ru)</CommonTemplate>", config_text)))
print(f"\n=== _ru in Configuration.xml: {len(ru_in_config)} ===")
for name in ru_in_config:
    print(f"  {name}")

# 3. _ru main CDI entries (CommonTemplate.XXX_ru without .Template suffix)
cdi_text = CDI.read_text(encoding="utf-8-sig")
# All CDI entries for _ru templates
ru_cdi_all = sorted(set(re.findall(r'name="(CommonTemplate\.\S+_ru[^"]*)"', cdi_text)))
print(f"\n=== _ru CDI entries (all): {len(ru_cdi_all)} ===")
for e in ru_cdi_all:
    print(f"  {e}")

# Main-level CDI entries (exactly CommonTemplate.XXX_ru, no sub-objects)
ru_cdi_main = sorted(set(re.findall(r'name="(CommonTemplate\.[^"]+_ru)"', cdi_text)))
# Filter out those that have .Template etc after _ru
ru_cdi_main = [e for e in ru_cdi_main if e.count(".") == 1]  # exactly one dot
print(f"\n=== _ru CDI main entries: {len(ru_cdi_main)} ===")
for e in ru_cdi_main:
    print(f"  {e}")

# 4. Delta: in Configuration.xml but NOT in CDI main
missing_cdi = []
for name in ru_in_config:
    full = f"CommonTemplate.{name}"
    if full not in ru_cdi_main:
        missing_cdi.append(name)
print(f"\n=== MISSING _ru CDI main entries: {len(missing_cdi)} ===")
for name in missing_cdi:
    print(f"  {name}")

# 5. Also check: in Configuration.xml but no folder on disk
missing_folders = [name for name in ru_in_config if name not in ru_folders]
print(f"\n=== MISSING _ru folders on disk: {len(missing_folders)} ===")
for name in missing_folders:
    print(f"  {name}")
