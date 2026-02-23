# -*- coding: utf-8 -*-
"""
Recovery: restore Конфигурация from last working commit, resync to Проверка.
Saves current ИмпортНоменклатуры changes before restoration.
"""
import subprocess
import pathlib
import shutil

PROJECT = pathlib.Path(r"D:\Git\Public_Trade_Module")
KONFIG = PROJECT / "Конфигурация"
PROVERKA = KONFIG / "Проверка"

# Step 1: Save current ИмпортНоменклатуры changes (the only valuable uncommitted work besides report)
print("=== STEP 1: Save uncommitted ИмпортНоменклатуры changes ===")
import_files = {
    "ObjectModule": KONFIG / "DataProcessors" / "ИмпортНоменклатуры" / "Ext" / "ObjectModule.bsl",
    "FormModule": KONFIG / "DataProcessors" / "ИмпортНоменклатуры" / "Forms" / "Форма" / "Ext" / "Form" / "Module.bsl",
    "FormXml": KONFIG / "DataProcessors" / "ИмпортНоменклатуры" / "Forms" / "Форма" / "Ext" / "Form.xml",
    "DataProcessorXml": KONFIG / "DataProcessors" / "ИмпортНоменклатуры.xml",
}

saved_dir = PROJECT / "_saved_import"
saved_dir.mkdir(exist_ok=True)

for name, src in import_files.items():
    if src.exists():
        dest = saved_dir / f"{name}{src.suffix}"
        shutil.copy2(src, dest)
        print(f"  Saved: {name} ({src.stat().st_size} bytes)")
    else:
        print(f"  Not found: {name}")

# Also save ConfigDumpInfo for reference (to know ИмпортНоменклатуры CDI entries)
shutil.copy2(KONFIG / "ConfigDumpInfo.xml", saved_dir / "ConfigDumpInfo_current.xml")
shutil.copy2(KONFIG / "Configuration.xml", saved_dir / "Configuration_current.xml")
print("  Saved: CDI + Configuration references")

# Step 2: Restore Конфигурация from git commit 71c61b5
print("\n=== STEP 2: Restore Конфигурация from commit 71c61b5 ===")
# Reset tracked Конфигурация files to last commit
subprocess.run(["git", "checkout", "HEAD", "--", "Конфигурация/"], cwd=str(PROJECT), check=True)
print("  Restored from 71c61b5")

# Verify
config = (KONFIG / "Configuration.xml").read_text(encoding='utf-8')
print(f"  Reports in restored config: {config.count('<Report>')}")
print(f"  ИмпортНоменклатуры present: {'ИмпортНоменклатуры' in config}")
print(f"  СправочникНоменклатуры present: {'СправочникНоменклатуры' in config}")

# Step 3: Resync Конфигурация -> Проверка (fresh copy)
print("\n=== STEP 3: Resync to Проверка ===")
if PROVERKA.exists():
    shutil.rmtree(PROVERKA)
for item in KONFIG.iterdir():
    if item.name in ("Проверка", "README.md"):
        continue
    dest = PROVERKA / item.name
    if item.is_dir():
        shutil.copytree(item, dest)
    else:
        PROVERKA.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, dest)
print("  Fresh Проверка created from git-restored Конфигурация")

# Step 4: Remove report files that were NEW (untracked)
print("\n=== STEP 4: Cleanup untracked report files from Конфигурация ===")
report_xml = KONFIG / "Reports" / "СправочникНоменклатуры.xml"
report_dir = KONFIG / "Reports" / "СправочникНоменклатуры"
if report_xml.exists():
    report_xml.unlink()
    print("  Removed report XML")
if report_dir.exists():
    shutil.rmtree(report_dir)
    print("  Removed report directory")

print("\n=== DONE ===")
print("Конфигурация and Проверка restored to last working commit.")
print(f"ИмпортНоменклатуры changes saved to: {saved_dir}")
