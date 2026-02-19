# -*- coding: utf-8 -*-
import subprocess
import os

os.chdir(r"D:\Git\Public_Trade_Module")
os.environ["GIT_CONFIG_PARAMETERS"] = "'core.quotePath=false'"

# Show original ManagedApplicationModule from the rollback commit
result = subprocess.run(
    ["git", "show", "960be69:Конфигурация/Ext/ManagedApplicationModule.bsl"],
    capture_output=True, encoding="utf-8", errors="replace"
)
print("=== ORIGINAL ManagedApplicationModule (pre-BPO) ===")
print(result.stdout[:3000] if result.stdout else "(empty)")
print("STDERR:", result.stderr[:500] if result.stderr else "(none)")

# Show original МенеджерОборудования
result2 = subprocess.run(
    ["git", "show", "960be69:Конфигурация/CommonModules/МенеджерОборудования/Ext/Module.bsl"],
    capture_output=True, encoding="utf-8", errors="replace"
)
print("\n=== ORIGINAL МенеджерОборудования (pre-BPO) ===")
print(result2.stdout[:3000] if result2.stdout else "(empty)")
print("STDERR:", result2.stderr[:500] if result2.stderr else "(none)")

# Also check git log for last few commits
result3 = subprocess.run(
    ["git", "log", "--oneline", "-5"],
    capture_output=True, encoding="utf-8", errors="replace"
)
print("\n=== LAST 5 COMMITS ===")
print(result3.stdout)
