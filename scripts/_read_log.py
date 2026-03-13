"""Read latest deploy log and show relevant lines."""
import os
from pathlib import Path

logs_dir = Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs")
logs = sorted(logs_dir.glob("1c-designer-*"), reverse=True)
if not logs:
    print("No log files found!")
    exit(1)

latest = logs[0]
print(f"Latest log: {latest.name}")
content = latest.read_text(encoding="utf-8-sig", errors="replace")
lines = content.splitlines()
print(f"Total lines: {len(lines)}")

# Show all lines (or filter relevant ones)
for i, line in enumerate(lines):
    if line.strip():
        print(f"[{i+1}] {line}")
