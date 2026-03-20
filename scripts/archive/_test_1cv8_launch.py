"""Test basic 1cv8 DESIGNER launch time"""
import os, subprocess, time

IB = r"D:\Confiq\Public Trade Module"
V8 = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"

# Kill all 1cv8
subprocess.run(["taskkill", "/IM", "1cv8.exe", "/F"], capture_output=True)
time.sleep(2)

# Clean lock files
for f in os.scandir(IB):
    if f.name.endswith(".cfl") or "tmp" in f.name.lower():
        try:
            os.remove(f.path)
        except OSError:
            pass

# Test: just open and close Designer (no operations)
log = r"D:\Git\Public_Trade_Module\logs\test-designer.log"
print("Starting 1cv8 DESIGNER (bare)...")
t0 = time.time()
result = subprocess.run([
    V8, "DESIGNER", "/F", IB, "/N", "Админ",
    "/DisableStartupDialogs", "/DisableStartupMessages",
    "/Out", log,
], capture_output=True, text=True, timeout=30)
elapsed = time.time() - t0
print(f"Exit: {result.returncode}, Time: {elapsed:.1f}s")

if os.path.exists(log) and os.path.getsize(log) > 0:
    with open(log, encoding="utf-8-sig", errors="replace") as f:
        print("Log:", f.read()[:500])
else:
    print("Log: (empty)")
