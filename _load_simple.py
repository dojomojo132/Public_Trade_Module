# -*- coding: utf-8 -*-
import subprocess
import sys

ib = r"D:\Git\Public_Trade_Module\ИБ\PTM"
config = r"D:\Git\Public_Trade_Module\Конфигурация"
exe = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"

print("Запуск загрузки конфигурации...")
print(f"ИБ: {ib}")
print(f"Конфигурация: {config}")
print("-" * 60)

# Загрузка конфигурации без логов - вывод сразу в консоль
result = subprocess.run(
    [exe, "DESIGNER", f"/F{ib}", f"/LoadConfigFromFiles{config}", "/DisableStartupDialogs"],
    capture_output=False,  # Вывод напрямую в консоль
    text=True
)

print("-" * 60)
print(f"Код завершения: {result.returncode}")

if result.returncode == 0:
    print("✓ Загрузка завершена успешно")
else:
    print(f"✗ Ошибка загрузки (код {result.returncode})")

sys.exit(result.returncode)
