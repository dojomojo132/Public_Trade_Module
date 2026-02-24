# -*- coding: utf-8 -*-
import pathlib

p = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Спецификации\ТЕХНИЧЕСКАЯ СПЕЦИФИКАЦИЯ КОНФИГУРАЦИИ PTM (Public Trade Module).xml")
text = p.read_text(encoding="utf-8")
lines = text.split("\n")

# Find MCP section
for i, line in enumerate(lines):
    if "mcp_MCPСервер" in line or "mcp_Инструмент" in line:
        print(f"Line {i+1}: {line.strip()[:120]}")

# Last 30 lines
print("\n=== ПОСЛЕДНИЕ 30 строк ===")
total = len(lines)
start = max(0, total - 30)
for i in range(start, total):
    print(f"Line {i+1}: {lines[i].rstrip()[:120]}")
