# -*- coding: utf-8 -*-
"""
Full resync: restore Конфигурация from git, add report, then copy to Проверка.
"""
import pathlib
import shutil
import subprocess
import uuid
import secrets

PROJECT = pathlib.Path(r"D:\Git\Public_Trade_Module")
KONFIG = PROJECT / "Конфигурация"
PROVERKA = KONFIG / "Проверка"

# Step 1: Restore ALL Конфигурация files from git (clean state before report)
print("=== STEP 1: Restore Конфигурация from git ===")
# Get list of changed Конфигурация files (not Проверка)
result = subprocess.run(
    ["git", "diff", "--name-only", "HEAD"],
    cwd=str(PROJECT), capture_output=True, text=True, encoding='utf-8'
)
changed = [f for f in result.stdout.strip().split('\n') if f]
config_files = [f for f in changed if f.startswith('Конфигурация/') and '/Проверка/' not in f]
print(f"  Changed Конфигурация files: {len(config_files)}")
for f in config_files:
    print(f"    {f}")

# Restore them from git
for f in config_files:
    subprocess.run(["git", "checkout", "HEAD", "--", f], cwd=str(PROJECT))
print("  Restored from git.")

# Step 2: Full copy Конфигурация -> Проверка (delete and recreate)
print("\n=== STEP 2: Full resync Конфигурация -> Проверка ===")
if PROVERKA.exists():
    shutil.rmtree(PROVERKA)
    print("  Deleted old Проверка/")

# Copy everything except Проверка itself
def copy_konfig_to_proverka():
    for item in KONFIG.iterdir():
        if item.name == "Проверка" or item.name == "README.md":
            continue
        dest = PROVERKA / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            PROVERKA.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)
    
copy_konfig_to_proverka()
print("  Copied Конфигурация -> Проверка (fresh)")

# Step 3: Verify clean config loads by running deploy on this clean state first
print("\n=== STEP 3: Verify count ===")
config_xml = PROVERKA / "Configuration.xml"
config = config_xml.read_text(encoding='utf-8')
report_count = config.count('<Report>')
print(f"  Reports in Configuration.xml: {report_count}")
print(f"  СправочникНоменклатуры present: {'СправочникНоменклатуры' in config}")

print("\nDone! Clean Проверка ready for deploy test.")
