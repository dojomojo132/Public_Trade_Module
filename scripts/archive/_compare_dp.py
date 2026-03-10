# -*- coding: utf-8 -*-
"""Сравниваем файлы ТестыРМК с работающим УправлениеНастройками байт-в-байт."""
import pathlib

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")

pairs = [
    (ROOT / "DataProcessors" / "УправлениеНастройками.xml",
     ROOT / "DataProcessors" / "ТестыРМК.xml"),
    (ROOT / "DataProcessors" / "УправлениеНастройками" / "Forms" / "Форма.xml",
     ROOT / "DataProcessors" / "ТестыРМК" / "Forms" / "Форма.xml"),
]

for ref_p, new_p in pairs:
    print(f"=== Сравнение: {ref_p.name} ===")
    ref = ref_p.read_bytes()
    new = new_p.read_bytes()
    ref_text = ref[3:].decode("utf-8") if ref[:3] == b"\xef\xbb\xbf" else ref.decode("utf-8")
    new_text = new[3:].decode("utf-8") if new[:3] == b"\xef\xbb\xbf" else new.decode("utf-8")

    ref_lines = ref_text.splitlines()
    new_lines = new_text.splitlines()

    print(f"  REF: {len(ref_lines)} строк, NEW: {len(new_lines)} строк")
    # Показать строки REF, которых нет в NEW (по структуре)
    for i, (r, n) in enumerate(zip(ref_lines, new_lines), 1):
        if r.strip() and n.strip():
            # Normalize names
            rn = r.replace("УправлениеНастройками", "ТестыРМК") \
                  .replace("Управление настройками", "Тесты РМК") \
                  .replace("d59106e1-c5fa-4129-973a-8ff05a6d4cc5", "a2b3c4d5-e6f7-4a8b-9c0d-e1f2a3b4c5d6") \
                  .replace("b7c8d9e0-f1a2-3b4c-5d6e-7f8a9b0c1d2e", "f7a8b9c0-d1e2-4f3a-5b6c-7d8e9f0a1b2c")
            if rn.rstrip() != n.rstrip():
                print(f"  DIFF line {i}:")
                print(f"    REF: {r!r}")
                print(f"    NEW: {n!r}")
    if len(ref_lines) != len(new_lines):
        print(f"  РАЗНОЕ ЧИСЛО СТРОК!")
        for i in range(min(len(ref_lines), len(new_lines)), max(len(ref_lines), len(new_lines))):
            if i < len(ref_lines):
                print(f"  + REF [{i}]: {ref_lines[i]!r}")
            else:
                print(f"  + NEW [{i}]: {new_lines[i]!r}")
    print()
