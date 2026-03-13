"""Run validate-config.ps1 and extract only ОШИБКА/ПРЕДУП/ИТОГО lines."""
import subprocess
import re
import sys

result = subprocess.run(
    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
     "-File", r"D:\Git\Public_Trade_Module\Документация\Валидация\validate-config.ps1"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    cwd=r"D:\Git\Public_Trade_Module"
)

output = result.stdout + "\n" + result.stderr
lines = output.splitlines()

print("=== ERRORS ===")
error_count = 0
for line in lines:
    stripped = line.strip()
    if not stripped:
        continue
    if any(kw in stripped for kw in ["ОШИБКА", "FAIL", "ОШИБОК:", "ПРЕДУП", "ИТОГО"]):
        print(stripped)
        if "ОШИБКА" in stripped or "FAIL" in stripped:
            error_count += 1

print(f"\n=== Extracted {error_count} error lines ===")
