# -*- coding: utf-8 -*-
"""Удаление ObjectModule записи для ТестыРМК из ConfigDumpInfo.xml (оба места)."""
import pathlib

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
CONFIGS = [
    ROOT / "Конфигурация",
    ROOT / "Конфигурация" / "Проверка",
]

OLD_LINE = '\t\t<Metadata name="DataProcessor.ТестыРМК.ObjectModule" id="f7a8b9c0-d1e2-4f3a-5b6c-7d8e9f0a1b2c.0" configVersion="d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a900000000" />'

print("=== Удаление ObjectModule из ConfigDumpInfo.xml ===")
for cfg in CONFIGS:
    cdi = cfg / "ConfigDumpInfo.xml"
    data = cdi.read_bytes()
    bom = data[:3] if data[:3] == b"\xef\xbb\xbf" else b""
    text = data[len(bom):].decode("utf-8")

    if OLD_LINE not in text:
        print(f"  SKIP (не найдено): {cdi.relative_to(ROOT)}")
        continue

    new_text = text.replace(OLD_LINE + "\n", "").replace(OLD_LINE, "")
    cdi.write_bytes(bom + new_text.encode("utf-8"))
    print(f"  OK  {cdi.relative_to(ROOT)}")

print()
print("=== ГОТОВО ===")
