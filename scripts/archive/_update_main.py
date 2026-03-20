"""Just run UpdateDBCfg on the main config - maybe it needs restructuring"""
import os, subprocess, time

V8 = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
IB = r"D:\Confiq\Public Trade Module"
LOG = r"D:\Git\Public_Trade_Module\logs\update-main.log"

# Clean all locks
for f in os.scandir(IB):
    if f.name.endswith('.cfl') or 'tmp' in f.name.lower():
        try: os.remove(f.path)
        except: pass

# Kill orphan 1cv8
subprocess.run(["taskkill", "/IM", "1cv8.exe", "/F"], capture_output=True)
time.sleep(2)

# Try update main config
print("Trying UpdateDBCfg on main config...")
t0 = time.time()
p = subprocess.Popen(
    [V8, "DESIGNER", "/F", IB, "/N", "Админ",
     "/UpdateDBCfg",
     "/DisableStartupDialogs", "/DisableStartupMessages",
     "/Out", LOG],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
try:
    stdout, stderr = p.communicate(timeout=60)
    elapsed = time.time() - t0
    print(f"Exit: {p.returncode} ({elapsed:.1f}s)")
except subprocess.TimeoutExpired:
    p.kill()
    p.communicate()
    print(f"TIMEOUT after {time.time()-t0:.0f}s")

if os.path.exists(LOG) and os.path.getsize(LOG) > 0:
    for enc in ("utf-8-sig", "cp1251"):
        try:
            with open(LOG, encoding=enc) as f:
                print("Log:", f.read()[:1000])
            break
        except: pass
