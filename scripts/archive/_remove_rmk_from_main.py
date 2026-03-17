# -*- coding: utf-8 -*-
"""
Удаление DataProcessor.РабочееМестоКассира из основной конфигурации PTM.
Обработка уже скопирована в расширение PTM_Analytics как Анл_РабочееМестоКассира.
"""
import os
import re
import shutil

PROJECT = r"D:\Git\Public_Trade_Module"
MAIN_CFG = os.path.join(PROJECT, "Конфигурация")
DP_NAME = "РабочееМестоКассира"
DP_FULL = f"DataProcessor.{DP_NAME}"

errors = []

# ── 1. Remove from Configuration.xml ──
print("=== 1. Удаление из Configuration.xml ===")
config_path = os.path.join(MAIN_CFG, "Configuration.xml")
with open(config_path, "r", encoding="utf-8-sig") as f:
    config = f.read()

pattern = rf'\s*<DataProcessor>{re.escape(DP_NAME)}</DataProcessor>'
new_config = re.sub(pattern, '', config)
if new_config == config:
    print(f"  ⚠️ Не найден <DataProcessor>{DP_NAME}</DataProcessor>")
    errors.append("Configuration.xml: DataProcessor not found")
else:
    with open(config_path, "w", encoding="utf-8-sig") as f:
        f.write(new_config)
    print(f"  Удалён <DataProcessor>{DP_NAME}</DataProcessor>")

# ── 2. Remove from ConfigDumpInfo.xml ──
print("\n=== 2. Удаление из ConfigDumpInfo.xml ===")
cdi_path = os.path.join(MAIN_CFG, "ConfigDumpInfo.xml")
with open(cdi_path, "r", encoding="utf-8-sig") as f:
    cdi = f.read()

# Count entries before removal
count_before = len(re.findall(rf'{re.escape(DP_FULL)}', cdi))

# Remove all CDI entries matching DataProcessor.РабочееМестоКассира
# Handle both self-closing tags and tags with children (hierarchical format)
# Pattern 1: Self-closing <Metadata name="DataProcessor.РМК..." ... />
cdi = re.sub(
    rf'\s*<Metadata\s+name="{re.escape(DP_FULL)}[^"]*"[^/]*/>', 
    '', cdi
)

# Pattern 2: Opening+closing pair <Metadata name="DataProcessor.РМК...">...</Metadata>
cdi = re.sub(
    rf'\s*<Metadata\s+name="{re.escape(DP_FULL)}"[^>]*>.*?</Metadata>',
    '', cdi, flags=re.DOTALL
)

count_after = len(re.findall(rf'{re.escape(DP_FULL)}', cdi))
removed = count_before - count_after

with open(cdi_path, "w", encoding="utf-8-sig") as f:
    f.write(cdi)
print(f"  Удалено {removed} CDI-записей (было {count_before})")

if count_after > 0:
    print(f"  ⚠️ Осталось {count_after} ссылок!")
    errors.append(f"CDI: {count_after} entries remaining")

# ── 3. Remove from Subsystems ──
print("\n=== 3. Удаление из подсистем ===")
subsystems_dir = os.path.join(MAIN_CFG, "Subsystems")
for fname in os.listdir(subsystems_dir):
    if not fname.endswith(".xml"):
        continue
    fpath = os.path.join(subsystems_dir, fname)
    with open(fpath, "r", encoding="utf-8-sig") as f:
        content = f.read()
    
    if DP_FULL not in content:
        continue
    
    # Remove the xr:Item line
    new_content = re.sub(
        rf'\s*<(?:xr:)?Item[^>]*>{re.escape(DP_FULL)}</(?:xr:)?Item>',
        '', content
    )
    if new_content != content:
        with open(fpath, "w", encoding="utf-8-sig") as f:
            f.write(new_content)
        print(f"  Удалён из {fname}")

# ── 4. Delete files from disk ──
print("\n=== 4. Удаление файлов ===")
dp_xml = os.path.join(MAIN_CFG, "DataProcessors", f"{DP_NAME}.xml")
dp_dir = os.path.join(MAIN_CFG, "DataProcessors", DP_NAME)

if os.path.exists(dp_xml):
    os.remove(dp_xml)
    print(f"  Удалён: {DP_NAME}.xml")
else:
    print(f"  ⚠️ Файл не найден: {DP_NAME}.xml")

if os.path.isdir(dp_dir):
    shutil.rmtree(dp_dir)
    print(f"  Удалена папка: {DP_NAME}/")
else:
    print(f"  ⚠️ Папка не найдена: {DP_NAME}/")

# ── Summary ──
if errors:
    print(f"\n⚠️ ОШИБКИ: {errors}")
else:
    print(f"\n✅ DataProcessor.{DP_NAME} удалён из основной конфигурации")
    print(f"   Следующий шаг: python scripts/_ps_wrapper.py deploy -Action Full -SkipDtBackup -SkipCheck")
