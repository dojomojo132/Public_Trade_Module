# -*- coding: utf-8 -*-
import subprocess, os
os.chdir(r"D:\Git\Public_Trade_Module")
subprocess.run(["git", "add", "-A"], check=True)
r = subprocess.run(["git", "commit", "-m", "BACKUP: 2026-02-19 перед улучшением подсистемы сканера"], capture_output=True, text=True, encoding="utf-8")
print("Commit:", r.stdout.strip() if r.stdout else r.stderr.strip())
r2 = subprocess.run(["git", "push"], capture_output=True, text=True, encoding="utf-8")
print("Push:", r2.stderr.strip() if r2.stderr else "OK")
