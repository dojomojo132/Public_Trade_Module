# -*- coding: utf-8 -*-
import subprocess, sys, pathlib, time

V8 = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
IB = r"D:\Confiq\Public Trade Module"
LOG = r"D:\Git\Public_Trade_Module\logs\ext_update.log"

pathlib.Path(LOG).parent.mkdir(parents=True, exist_ok=True)

cmd = [
    V8, "DESIGNER",
    "/F", IB,
    "/N", "Admin",
    "/UpdateDBCfg",
    "-Extension", "MCP_\u0421\u0435\u0440\u0432\u0435\u0440",
    "/DisableStartupDialogs",
    "/DisableStartupMessages",
    "/Out", LOG,
]

print(f"Running UpdateDBCfg for extension...")
r = subprocess.run(cmd, timeout=120)
print(f"Exit code: {r.returncode}")

if pathlib.Path(LOG).exists():
    txt = pathlib.Path(LOG).read_text(encoding="utf-8-sig")
    print(f"Log:\n{txt}" if txt.strip() else "Log: (empty)")

sys.exit(r.returncode)
