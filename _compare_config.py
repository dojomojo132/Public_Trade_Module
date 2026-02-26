# -*- coding: utf-8 -*-
"""Compare Configuration.xml between Конфигурация/ and Проверка/"""
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")

main = base / "Configuration.xml"
check = base / "Проверка" / "Configuration.xml"

main_lines = main.read_text(encoding='utf-8-sig').splitlines()
check_lines = check.read_text(encoding='utf-8-sig').splitlines()

print(f"Main: {len(main_lines)} lines, {main.stat().st_size} bytes")
print(f"Check: {len(check_lines)} lines, {check.stat().st_size} bytes")

# Find differences
diffs = []
max_lines = max(len(main_lines), len(check_lines))
for i in range(max_lines):
    m = main_lines[i] if i < len(main_lines) else "[EOF]"
    c = check_lines[i] if i < len(check_lines) else "[EOF]"
    if m != c:
        diffs.append((i+1, m.strip(), c.strip()))

if not diffs:
    print("IDENTICAL")
else:
    print(f"\nDifferences: {len(diffs)}")
    for line_no, m, c in diffs[:20]:
        print(f"  Line {line_no}:")
        print(f"    Main:  {m[:120]}")
        print(f"    Check: {c[:120]}")
