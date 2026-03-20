"""Load extension with longer timeout and proper lock management"""
import os, subprocess, time

V8 = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
IB = r"D:\Confiq\Public Trade Module"
EXT = "PTM_Driver_Vchasno"
EXT_PATH = r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Driver_Vchasno"
LOG_DIR = r"D:\Git\Public_Trade_Module\logs"

def clean_locks():
    for f in os.scandir(IB):
        if f.name.endswith('.cfl') or 'tmp' in f.name.lower():
            try: os.remove(f.path)
            except: pass

def run_v8(tag, extra, timeout=300):
    log = os.path.join(LOG_DIR, f"ext-{tag}-{int(time.time())}.log")
    args = [V8, "DESIGNER", "/F", IB, "/N", "Админ",
            *extra, "/WA+",
            "/DisableStartupDialogs", "/DisableStartupMessages",
            "/Out", log]
    print(f"[{tag}] Starting...")
    t0 = time.time()
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = p.communicate(timeout=timeout)
        elapsed = time.time() - t0
        print(f"[{tag}] Exit: {p.returncode} ({elapsed:.1f}s)")
    except subprocess.TimeoutExpired:
        p.kill()
        p.communicate()
        elapsed = time.time() - t0
        print(f"[{tag}] TIMEOUT after {elapsed:.0f}s")
        return -1
    
    if os.path.exists(log) and os.path.getsize(log) > 0:
        for enc in ("utf-8-sig", "cp1251"):
            try:
                with open(log, encoding=enc) as f:
                    txt = f.read().strip()
                if txt:
                    print(f"[{tag}] Log: {txt[:500]}")
                break
            except: pass
    else:
        print(f"[{tag}] Log: (empty)")
    return p.returncode

# Clean
clean_locks()

# Load
code = run_v8("load", ["/LoadConfigFromFiles", EXT_PATH, "-Extension", EXT])
clean_locks()

if code in (0, 1):
    # Update
    code2 = run_v8("update", ["/UpdateDBCfg", "-Extension", EXT])
    clean_locks()
    if code2 in (0, 1):
        print("\nDEPLOY OK")
    else:
        print(f"\nUpdate FAILED: {code2}")
else:
    print(f"\nLoad FAILED: {code}")
