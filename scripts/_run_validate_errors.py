"""Run validate and extract only error lines."""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "scripts/_ps_wrapper.py", "validate"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    cwd=r"D:\Git\Public_Trade_Module"
)

output = result.stdout + result.stderr
lines = output.splitlines()
errors = [l for l in lines if "ОШИБКА" in l or "ОШИБОК" in l or "FAIL" in l]
print(f"Total error lines: {len(errors)}")
for line in errors:
    print(line.strip())
