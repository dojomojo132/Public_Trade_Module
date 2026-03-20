"""
Деплой расширения с очисткой cfl-файлов перед каждым запуском 1cv8.
"""
import subprocess, time, os, glob

V8EXE = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
IB = r"D:\Confiq\Public Trade Module"
EXT_NAME = "PTM_Driver_Vchasno"
EXT_PATH = r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Driver_Vchasno"
LOG_DIR = r"D:\Git\Public_Trade_Module\logs"


def clear_locks():
    """Удалить все .cfl и 1Cv8tmp.* файлы из базы"""
    count = 0
    for f in os.scandir(IB):
        if f.name.endswith('.cfl') or ('tmp' in f.name.lower() and '1cv8' in f.name.lower()):
            try:
                os.remove(f.path)
                count += 1
            except OSError as e:
                print(f"  Не удалось удалить {f.name}: {e}")
    if count:
        print(f"  Очищено {count} lock-файлов")
    return count


def run_1cv8(tag, extra_args, timeout=60):
    """Запустить 1cv8 с очисткой locks до и после"""
    log = os.path.join(LOG_DIR, f"ext-deploy-{tag}-{int(time.time())}.log")
    args = [
        V8EXE, "DESIGNER",
        "/F", IB, "/N", "Админ",
        *extra_args,
        "/DisableStartupDialogs", "/DisableStartupMessages",
        "/Out", log,
    ]

    print(f"\n{'─'*60}")
    print(f"[{tag}] Очищаем locks...")
    clear_locks()

    print(f"[{tag}] Запускаем 1cv8...")
    t0 = time.time()
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        elapsed = time.time() - t0
        print(f"[{tag}] Exit code: {result.returncode}  ({elapsed:.1f} сек)")

        # Читаем лог
        if os.path.exists(log) and os.path.getsize(log) > 0:
            for enc in ("utf-8-sig", "utf-8", "cp1251"):
                try:
                    with open(log, encoding=enc) as f:
                        content = f.read().strip()
                    if content:
                        print(f"[{tag}] Лог: {content[:500]}")
                    break
                except Exception:
                    pass

        return result.returncode
    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        print(f"[{tag}] ТАЙМАУТ через {elapsed:.0f} сек! Убиваем 1cv8...")
        try:
            import signal
            # Find and kill 1cv8.exe
            for proc in __import__('subprocess').run(
                ['tasklist', '/FI', 'IMAGENAME eq 1cv8.exe', '/FO', 'CSV'],
                capture_output=True, text=True
            ).stdout.splitlines()[1:]:
                if '1cv8.exe' in proc:
                    pid = int(proc.split(',')[1].strip('"'))
                    os.kill(pid, 9)
                    print(f"  Убит процесс {pid}")
        except Exception as e:
            print(f"  Не удалось убить 1cv8: {e}")
        return -1
    finally:
        print(f"[{tag}] Очищаем locks после выполнения...")
        clear_locks()


# === Деплой ===
print(f"{'='*60}")
print(f"Деплой расширения: {EXT_NAME}")
print(f"Путь: {EXT_PATH}")
print(f"{'='*60}")

# Step 1: Load
load_code = run_1cv8("load", [
    "/LoadConfigFromFiles", EXT_PATH,
    "-Extension", EXT_NAME,
])

if load_code not in (0, 1):
    print(f"\n❌ Load завершился с ошибкой: {load_code}")
    exit(1)

print(f"\n✅ Load: {'OK' if load_code == 0 else 'OK (с предупреждениями)'}")

# Step 2: Update
update_code = run_1cv8("update", [
    "/UpdateDBCfg",
    "-Extension", EXT_NAME,
])

if update_code not in (0, 1):
    print(f"\n❌ Update завершился с ошибкой: {update_code}")
    exit(1)

print(f"\n✅ Update: {'OK' if update_code == 0 else 'OK (с предупреждениями)'}")
print(f"\n{'='*60}")
print(f"✅ Деплой {EXT_NAME} ВЫПОЛНЕН")
print(f"{'='*60}")
