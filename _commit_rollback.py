# -*- coding: utf-8 -*-
import subprocess
import os

os.chdir(r"D:\Git\Public_Trade_Module")

# Коммит откат
subprocess.run(["git", "add", "-A"], check=True)
result = subprocess.run(
    ["git", "commit", "-m", "ROLLBACK: 2026-02-19 откат конфигурации до состояния ДО БПО (к коммиту 960be69)"],
    capture_output=True, text=True, encoding="utf-8"
)
print("Commit:", result.stdout)
if result.stderr:
    print("Stderr:", result.stderr)
print("Return code:", result.returncode)

# Push
result2 = subprocess.run(
    ["git", "push"],
    capture_output=True, text=True, encoding="utf-8"
)
print("\nPush stdout:", result2.stdout)
print("Push stderr:", result2.stderr)
print("Push return code:", result2.returncode)
