# -*- coding: utf-8 -*-
"""Отключение безопасного режима расширения MCP_Сервер.

Шаги:
1. Выгрузить расширение в CFE
2. Загрузить CFE обратно с /UnsafeActionProtection-
3. UpdateDBCfg для расширения
"""
import subprocess
import pathlib
import sys

V8_EXE = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
IB_PATH = r"D:\Confiq\Public Trade Module"
WORK_DIR = pathlib.Path(r"D:\Git\Public_Trade_Module")
CFE_FILE = WORK_DIR / "logs" / "_mcp_ext_temp.cfe"
LOG_DIR = WORK_DIR / "logs"

LOG_DIR.mkdir(exist_ok=True)

def run_1c(args, log_name, description, timeout=120):
    """Запустить 1cv8.exe с параметрами."""
    log_file = LOG_DIR / f"_mcp_{log_name}.log"
    cmd = [
        V8_EXE, "DESIGNER",
        "/F", IB_PATH,
        "/N", "Админ",
        *args,
        "/DisableStartupDialogs",
        "/DisableStartupMessages",
        "/Out", str(log_file)
    ]
    
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=True, timeout=timeout)
    
    log_text = ""
    if log_file.exists():
        for enc in ["utf-8-sig", "utf-8", "cp1251"]:
            try:
                log_text = log_file.read_text(encoding=enc).strip()
                break
            except:
                pass
    
    print(f"Exit code: {result.returncode}")
    if log_text:
        print(f"Лог: {log_text[:500]}")
    
    if result.returncode != 0:
        print(f"\n!!! ОШИБКА !!!")
        if result.stderr:
            print(f"STDERR: {result.stderr.decode('cp866', errors='replace')[:500]}")
        return False
    
    return True


# Шаг 1: Выгрузить расширение в CFE
ok = run_1c(
    ["/ConfigExtensionUnLoad", str(CFE_FILE), "-Extension", "MCP_Сервер"],
    "ext_unload_cfe",
    "Шаг 1: Выгрузка расширения в CFE..."
)
if not ok:
    print("\nОШИБКА: Не удалось выгрузить расширение в CFE")
    sys.exit(1)

if not CFE_FILE.exists():
    print(f"\nОШИБКА: CFE файл не создан: {CFE_FILE}")
    sys.exit(1)

print(f"\n✓ CFE создан: {CFE_FILE} ({CFE_FILE.stat().st_size} байт)")


# Шаг 2: Загрузить CFE обратно с отключённым безопасным режимом
ok = run_1c(
    ["/ConfigExtensionLoad", str(CFE_FILE), "-Extension", "MCP_Сервер", "/UnsafeActionProtection-"],
    "ext_load_unsafe",
    "Шаг 2: Загрузка CFE с /UnsafeActionProtection-..."
)
if not ok:
    print("\nОШИБКА: Не удалось загрузить CFE с UnsafeActionProtection-")
    sys.exit(1)

print("\n✓ Расширение загружено с отключённым безопасным режимом!")


# Шаг 3: Обновление БД
ok = run_1c(
    ["/UpdateDBCfg", "-Extension", "MCP_Сервер"],
    "ext_updatedb_unsafe",
    "Шаг 3: Обновление БД расширения..."
)
if not ok:
    print("\nОШИБКА: Не удалось обновить БД расширения")
    sys.exit(1)

print("\n✓ БД расширения обновлена!")


# Очистка
if CFE_FILE.exists():
    CFE_FILE.unlink()
    print(f"\n✓ Временный CFE удалён")

print("\n" + "="*60)
print("ГОТОВО! Безопасный режим расширения MCP_Сервер ОТКЛЮЧЁН.")
print("Теперь get_object_module сможет читать файлы с диска.")
print("="*60)
