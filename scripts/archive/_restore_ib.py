# -*- coding: utf-8 -*-
import pathlib
import subprocess
import sys

backups_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\backups")
ib_path = pathlib.Path(r"D:\Confiq\Public Trade Module")
v8_exe = pathlib.Path(r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe")

# Найти последний DT-бэкап
dt_files = sorted(backups_dir.glob("*.dt"), key=lambda f: f.stat().st_mtime, reverse=True)

if not dt_files:
    print("DT-бэкапы не найдены!")
    sys.exit(1)

print("Доступные DT-бэкапы:")
for f in dt_files:
    size_mb = f.stat().st_size / (1024*1024)
    mtime = f.stat().st_mtime
    from datetime import datetime
    dt = datetime.fromtimestamp(mtime)
    print(f"  {f.name}  ({size_mb:.1f} MB)  {dt:%Y-%m-%d %H:%M:%S}")

latest = dt_files[0]
print(f"\nВосстанавливаю ИБ из: {latest.name}")
print(f"ИБ: {ib_path}")

# Команда восстановления: RESTOREIB
cmd = [
    str(v8_exe),
    "DESIGNER",
    f'/F "{ib_path}"',
    f'/RestoreIB "{latest}"',
    "/DisableStartupDialogs",
    "/DisableStartupMessages"
]

cmd_str = f'"{v8_exe}" DESIGNER /F "{ib_path}" /RestoreIB "{latest}" /DisableStartupDialogs /DisableStartupMessages'
print(f"\nКоманда: {cmd_str}")

result = subprocess.run(cmd_str, shell=True, capture_output=True, text=True, timeout=600)
print(f"\nExit code: {result.returncode}")
if result.stdout:
    print(f"STDOUT: {result.stdout[:500]}")
if result.stderr:
    print(f"STDERR: {result.stderr[:500]}")

if result.returncode == 0:
    print("\n✓ ИБ успешно восстановлена!")
else:
    print("\n✗ Ошибка восстановления!")
