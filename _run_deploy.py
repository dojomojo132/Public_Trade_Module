# -*- coding: utf-8 -*-
import subprocess
import sys

script = r"D:\Git\Public_Trade_Module\Документация\Валидация\deploy-config.ps1"

result = subprocess.run(
    ["powershell", "-ExecutionPolicy", "Bypass", "-File", script, "-Action", "Full"],
    cwd=r"D:\Git\Public_Trade_Module",
    encoding="utf-8",
    errors="replace"
)

sys.exit(result.returncode)
