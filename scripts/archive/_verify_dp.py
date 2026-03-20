# -*- coding: utf-8 -*-
"""Verify DataProcessor references in config files."""
import pathlib

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Analytics")

# Configuration.xml
cfg = ROOT / "Configuration.xml"
text = cfg.read_text(encoding="utf-8-sig")
lines = text.split('\n')
for i, line in enumerate(lines):
    if 'DataProcessor' in line or 'МассоваяУстановка' in line:
        print(f"Configuration.xml L{i+1}: {line.rstrip()}")

# ConfigDumpInfo.xml
cdi = ROOT / "ConfigDumpInfo.xml"
text2 = cdi.read_text(encoding="utf-8-sig")
for i, line in enumerate(text2.split('\n')):
    if 'МассоваяУстановка' in line:
        print(f"ConfigDumpInfo.xml L{i+1}: {line.rstrip()}")

# Subsystem
sub = ROOT / "Subsystems" / "Анл_Аналитика.xml"
text3 = sub.read_text(encoding="utf-8-sig")
for i, line in enumerate(text3.split('\n')):
    if 'МассоваяУстановка' in line:
        print(f"Subsystem L{i+1}: {line.rstrip()}")

print("\n=== DataProcessor entries in Configuration.xml ===")
for i, line in enumerate(lines):
    if '<DataProcessor>' in line:
        print(f"L{i+1}: {line.strip()}")

print("\nDone")
