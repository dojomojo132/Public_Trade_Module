# -*- coding: utf-8 -*-
import subprocess
import os

os.chdir(r"D:\Git\Public_Trade_Module")

# Откат папки Конфигурация/ к коммиту 960be69 (до БПО)
result = subprocess.run(
    ["git", "checkout", "960be69", "--", "Конфигурация/"],
    capture_output=True, text=True, encoding="utf-8"
)

print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)

if result.returncode == 0:
    print("\n✓ Откат конфигурации к 960be69 выполнен успешно!")
else:
    print("\n✗ Ошибка при откате!")
