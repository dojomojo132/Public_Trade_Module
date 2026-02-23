# -*- coding: utf-8 -*-
"""Fix validation errors:
1. Restore missing CommonModule _ДемоОфлайнОборудованиеВызовСервера from git f8d6d1a
2. Remove duplicate Configuration.БиблиотекаПодключаемогоОборудования from ConfigDumpInfo.xml
"""
import subprocess
import pathlib
import shutil
import re

REPO = pathlib.Path(r"D:\Git\Public_Trade_Module")
CONFIG = REPO / "Конфигурация"
CHECK = CONFIG / "Проверка"
BPO_COMMIT = "f8d6d1a"

# ===== 1. Restore missing CommonModule =====
print("=" * 60)
print("ЭТАП 1: Восстановление _ДемоОфлайнОборудованиеВызовСервера")
print("=" * 60)

# Check what files exist for this module in the BPO commit
module_name = "_ДемоОфлайнОборудованиеВызовСервера"
# Files we need:
# CommonModules/_ДемоОфлайнОборудованиеВызовСервера.xml
# CommonModules/_ДемоОфлайнОборудованиеВызовСервера/Ext/Module.bsl

# List files from git for this module
result = subprocess.run(
    ["git", "ls-tree", "-r", "--name-only", BPO_COMMIT, "--"],
    capture_output=True, text=True, cwd=str(REPO),
    encoding="utf-8"
)

# Find relevant files
module_files = []
for line in result.stdout.splitlines():
    # Look for the module in Конфигурация/Проверка path (that's the source)
    if module_name in line and "CommonModules" in line:
        module_files.append(line)

print(f"Найдено файлов в git: {len(module_files)}")
for f in module_files:
    print(f"  {f}")

# Restore files from git to both folders
restored = 0
for git_path in module_files:
    # Get the file content from git
    result = subprocess.run(
        ["git", "show", f"{BPO_COMMIT}:{git_path}"],
        capture_output=True, cwd=str(REPO),
        encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        # Try binary mode
        result = subprocess.run(
            ["git", "show", f"{BPO_COMMIT}:{git_path}"],
            capture_output=True, cwd=str(REPO)
        )
        if result.returncode != 0:
            print(f"  ✗ Не удалось получить: {git_path}")
            continue
        content_bytes = result.stdout
        is_binary = True
    else:
        content_text = result.stdout
        is_binary = False
    
    # Determine target paths
    # The git path might be like: Конфигурация/Проверка/CommonModules/...
    # We need to write to BOTH Конфигурация/ and Конфигурация/Проверка/
    
    if "Проверка/" in git_path:
        rel = git_path.split("Проверка/", 1)[1]
    elif "Конфигурация/" in git_path:
        rel = git_path.split("Конфигурация/", 1)[1]
    else:
        rel = git_path
    
    targets = [CONFIG / rel, CHECK / rel]
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        if is_binary:
            target.write_bytes(content_bytes)
        else:
            target.write_text(content_text, encoding="utf-8")
        print(f"  ✓ {target.relative_to(REPO)}")
        restored += 1

print(f"\nВосстановлено файлов: {restored}")

# ===== 2. Fix ConfigDumpInfo.xml duplicates =====
print("\n" + "=" * 60)
print("ЭТАП 2: Удаление дубликатов из ConfigDumpInfo.xml")
print("=" * 60)

for folder_name, folder in [("Конфигурация", CONFIG), ("Проверка", CHECK)]:
    cdi_path = folder / "ConfigDumpInfo.xml"
    if not cdi_path.exists():
        print(f"  ✗ {cdi_path} не найден")
        continue
    
    content = cdi_path.read_text(encoding="utf-8-sig")
    
    # Find and remove the Configuration.БиблиотекаПодключаемогоОборудования block
    # Pattern: <Metadata name="Configuration.БиблиотекаПодключаемогоОборудования" ...>
    #          ... nested entries ...
    #         </Metadata>
    # OR self-closing: <Metadata name="Configuration.БиблиотекаПодключаемогоОборудования" .../>
    
    # First try to find multi-line block
    pattern = r'\s*<Metadata\s+name="Configuration\.БиблиотекаПодключаемогоОборудования"[^>]*>.*?</Metadata>'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        block = match.group()
        # Count nested entries
        nested_count = block.count("<Metadata")
        print(f"  {folder_name}: Найден блок Configuration.БиблиотекаПодключаемогоОборудования ({nested_count} записей)")
        content = content[:match.start()] + content[match.end():]
        cdi_path.write_text(content, encoding="utf-8-sig")
        print(f"  ✓ Блок удалён из {folder_name}/ConfigDumpInfo.xml")
    else:
        # Try self-closing tag
        pattern_sc = r'\s*<Metadata\s+name="Configuration\.БиблиотекаПодключаемогоОборудования"[^/]*/>'
        match_sc = re.search(pattern_sc, content)
        if match_sc:
            content = content[:match_sc.start()] + content[match_sc.end():]
            cdi_path.write_text(content, encoding="utf-8-sig")
            print(f"  ✓ Самозакрывающийся тег удалён из {folder_name}/ConfigDumpInfo.xml")
        else:
            print(f"  - {folder_name}: Блок Configuration.БиблиотекаПодключаемогоОборудования не найден")

print("\n✓ Все исправления применены!")
