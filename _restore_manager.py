# -*- coding: utf-8 -*-
"""Restore BPO version of МенеджерОборудования module and XML from git f8d6d1a.
Our custom PTM scanner module is incompatible with BPO infrastructure.
BPO's МенеджерОборудования is a server module that provides API for all BPO modules."""
import subprocess
import pathlib

REPO = pathlib.Path(r"D:\Git\Public_Trade_Module")
BPO_COMMIT = "f8d6d1a"

# Files to restore from BPO commit
files_to_restore = [
    "Конфигурация/CommonModules/МенеджерОборудования.xml",
    "Конфигурация/CommonModules/МенеджерОборудования/Ext/Module.bsl",
    "Конфигурация/Проверка/CommonModules/МенеджерОборудования.xml",
    "Конфигурация/Проверка/CommonModules/МенеджерОборудования/Ext/Module.bsl",
]

print("=" * 60)
print("Восстановление БПО-версии МенеджерОборудования")
print("=" * 60)

for git_path in files_to_restore:
    target = REPO / git_path
    
    # Get file from BPO commit
    result = subprocess.run(
        ["git", "show", f"{BPO_COMMIT}:{git_path}"],
        capture_output=True, cwd=str(REPO),
        encoding="utf-8", errors="replace"
    )
    
    if result.returncode != 0:
        print(f"  ✗ Не найден в git: {git_path}")
        continue
    
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(result.stdout, encoding="utf-8")
    
    # Count lines to show module size
    lines = result.stdout.splitlines()
    print(f"  ✓ {git_path} ({len(lines)} строк)")

print("\n✓ Готово!")
print("\nМенеджерОборудования теперь содержит полный БПО API.")
print("Кастомный сканер-код заменён на БПО-инфраструктуру.")
