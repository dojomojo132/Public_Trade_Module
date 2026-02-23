# -*- coding: utf-8 -*-
"""Проверяем 1Cv8.dt в git истории и ищем рабочий бэкап."""
import subprocess, pathlib

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")

# Смотрим историю 1Cv8.dt
print("=== История 1Cv8.dt в git ===")
result = subprocess.run(
    ["git", "log", "--oneline", "--", "1Cv8.dt"],
    capture_output=True, text=True, encoding="utf-8",
    cwd=str(ROOT)
)
print(result.stdout[:2000])

# Размер текущего 1Cv8.dt
dt_path = ROOT / "1Cv8.dt"
if dt_path.exists():
    sz = dt_path.stat().st_size
    print(f"Текущий 1Cv8.dt: {sz // 1048576} MB ({sz} bytes)")
    import time
    print(f"Дата изменения: {time.ctime(dt_path.stat().st_mtime)}")
else:
    print("1Cv8.dt не найден в корне проекта!")

# Проверяем размер в git
print()
print("=== Размеры 1Cv8.dt в последних коммитах ===")
log_result = subprocess.run(
    ["git", "log", "--oneline", "-10", "--", "1Cv8.dt"],
    capture_output=True, text=True, encoding="utf-8",
    cwd=str(ROOT)
)
for line in log_result.stdout.strip().split("\n")[:10]:
    if not line.strip():
        continue
    commit = line.split()[0]
    size_result = subprocess.run(
        ["git", "cat-file", "-s", f"{commit}:1Cv8.dt"],
        capture_output=True, text=True, encoding="utf-8",
        cwd=str(ROOT)
    )
    size = size_result.stdout.strip() if size_result.returncode == 0 else "unknown"
    size_mb = int(size) // 1048576 if size.isdigit() else "?"
    print(f"  {line.strip()} - {size_mb} MB")
