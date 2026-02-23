# -*- coding: utf-8 -*-
import subprocess
import os

os.chdir(r"D:\Git\Public_Trade_Module")

# Search for глКэшДрайверовККТ in ALL bsl files
result = subprocess.run(
    ["git", "grep", "-l", "глКэшДрайверовККТ"],
    capture_output=True, encoding="utf-8", errors="replace"
)
print("=== Files referencing глКэшДрайверовККТ ===")
print(result.stdout if result.stdout else "(none found)")

# Also search for ВнешнееСобытие to see old event references
result2 = subprocess.run(
    ["git", "grep", "-n", "ВнешнееСобытие"],
    capture_output=True, encoding="utf-8", errors="replace"
)
print("\n=== References to ВнешнееСобытие ===")
print(result2.stdout[:3000] if result2.stdout else "(none found)")

# Search for ОбработкаОповещения in РМК to see how events are handled
result3 = subprocess.run(
    ["git", "grep", "-n", "ОбработкаОповещения"],
    capture_output=True, encoding="utf-8", errors="replace"
)
print("\n=== ОбработкаОповещения references ===")
print(result3.stdout[:3000] if result3.stdout else "(none found)")

# Check for Сообщить in the original startup to see what messages user might see
result4 = subprocess.run(
    ["git", "grep", "-n", "НапечататьЧек\|ПолучитьДрайверККТ"],
    capture_output=True, encoding="utf-8", errors="replace"
)
print("\n=== ККТ function references ===")
print(result4.stdout[:3000] if result4.stdout else "(none found)")
