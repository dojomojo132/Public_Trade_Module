"""
Прямой запуск 1cv8.exe LoadConfigFromFiles для PTM_Driver_Vchasno с длинным таймаутом.
"""
import subprocess, time, os

V8EXE = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
IB = r"D:\Confiq\Public Trade Module"
EXT_PATH = r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Driver_Vchasno"
LOG = r"D:\Git\Public_Trade_Module\logs\manual-load-test.log"

args = [
    V8EXE, "DESIGNER",
    "/F", IB,
    "/N", "Админ",
    "/LoadConfigFromFiles", EXT_PATH,
    "-Extension", "PTM_Driver_Vchasno",
    "/DisableStartupDialogs",
    "/DisableStartupMessages",
    "/Out", LOG,
]

print("Запускаем 1cv8.exe...")
print("Командная строка:", " ".join(args[:6]))
t0 = time.time()

try:
    result = subprocess.run(args, capture_output=True, text=True, timeout=600)
    elapsed = time.time() - t0
    print(f"Завершён за {elapsed:.1f} сек, exit code: {result.returncode}")
    if os.path.exists(LOG):
        with open(LOG, encoding="utf-8-sig", errors="replace") as f:
            print("Лог:")
            print(f.read()[:2000])
except subprocess.TimeoutExpired:
    elapsed = time.time() - t0
    print(f"ТАЙМАУТ через {elapsed:.0f} сек!")
except Exception as e:
    print(f"Ошибка: {e}")
