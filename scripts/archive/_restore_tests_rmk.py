# -*- coding: utf-8 -*-
"""
Восстанавливаем ТестыРМК файлы и обновляем Configuration.xml + CDI,
чтобы подготовиться к полному деплою.
"""
import subprocess, pathlib, shutil

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
PROVERKA = ROOT / "Конфигурация" / "Проверка"

# Шаг 1: Восстанавливаем ТестыРМК файлы из git HEAD
print("== Восстановление ТестыРМК из git HEAD ==")
rmk_files = [
    "Конфигурация/Проверка/DataProcessors/ТестыРМК.xml",
    "Конфигурация/Проверка/DataProcessors/ТестыРМК/Forms/Форма.xml",
    "Конфигурация/Проверка/DataProcessors/ТестыРМК/Forms/Форма/Ext/Form.xml",
    "Конфигурация/Проверка/DataProcessors/ТестыРМК/Forms/Форма/Ext/Form/Module.bsl",
]

for rel_path in rmk_files:
    result = subprocess.run(
        ["git", "show", f"HEAD:{rel_path.replace('\\', '/')}"],
        capture_output=True, cwd=str(ROOT)
    )
    if result.returncode == 0:
        disk_path = ROOT / rel_path.replace("/", "\\")
        disk_path.parent.mkdir(parents=True, exist_ok=True)
        disk_path.write_bytes(result.stdout)
        crlf = result.stdout.count(b'\r\n')
        lf = result.stdout.count(b'\n')
        bom = result.stdout[:3] == b'\xef\xbb\xbf'
        print(f"  [OK] {disk_path.name}: {len(result.stdout)}b BOM={bom} CRLF={crlf} LF={lf}")
    else:
        print(f"  [ERR] {rel_path}: {result.stderr[:100]}")

# Шаг 2: Добавляем ТестыРМК в Configuration.xml (CRLF-версия из git checkout)
print()
print("== Добавляем ТестыРМК в файлы конфигурации ==")

cfg_path = PROVERKA / "Configuration.xml"
cfg_bytes = cfg_path.read_bytes()

TESTS_RMK_LINE = "ТестыРМК".encode("utf-8")
if TESTS_RMK_LINE in cfg_bytes:
    print(f"  [SKIP] ТестыРМК уже есть в Configuration.xml ({len(cfg_bytes)}b)")
else:
    # Вставляем после ТестовоеЗаполнениеДанных
    MARKER = b"<DataProcessor>" + "ТестовоеЗаполнениеДанных".encode("utf-8") + b"</DataProcessor>"
    pos = cfg_bytes.find(MARKER)
    if pos == -1:
        print(f"  [ERR] Маркер не найден в Configuration.xml!")
    else:
        end_pos = pos + len(MARKER)
        # Ищем конец строки (CRLF или LF)
        nl = cfg_bytes.find(b'\n', end_pos)
        if nl == -1: nl = end_pos
        
        # Определяем отступ
        line_start = cfg_bytes.rfind(b'\n', 0, pos) + 1
        indent = bytes()
        for b_ in cfg_bytes[line_start:pos]:
            if b_ in (9, 32): indent += bytes([b_])  # tab/space
            else: break
        
        # Определяем CRLF или LF
        if b'\r\n' in cfg_bytes[:100]:
            eol = b'\r\n'
        else:
            eol = b'\n'
        
        new_entry = eol + indent + b"<DataProcessor>" + TESTS_RMK_LINE + b"</DataProcessor>"
        cfg_new = cfg_bytes[:nl] + new_entry + cfg_bytes[nl:]
        cfg_path.write_bytes(cfg_new)
        print(f"  [OK] Configuration.xml: {len(cfg_bytes)} -> {len(cfg_new)}b")

# Шаг 3: Добавляем ТестыРМК в ConfigDumpInfo.xml
cdi_path = PROVERKA / "ConfigDumpInfo.xml"
cdi_bytes = cdi_path.read_bytes()

TESTS_RMK_UUID = "f7a8b9c0-d1e2-4f3a-5b6c-7d8e9f0a1b2c"
FORM_UUID = "a2b3c4d5-e6f7-4a8b-9c0d-e1f2a3b4c5d6"

if TESTS_RMK_UUID.encode("ascii") in cdi_bytes:
    print(f"  [SKIP] ТестыРМК уже есть в ConfigDumpInfo.xml ({len(cdi_bytes)}b)")
else:
    MARKER_CDI = b"DataProcessor." + "ТестовоеЗаполнениеДанных".encode("utf-8")
    pos2 = cdi_bytes.rfind(MARKER_CDI)
    if pos2 == -1:
        print(f"  [ERR] Маркер CDI не найден!")
    else:
        # Конец текущей записи (/>)
        end2 = cdi_bytes.find(b"/>", pos2)
        nl2 = cdi_bytes.find(b'\n', end2) if end2 != -1 else pos2
        
        line_s2 = cdi_bytes.rfind(b'\n', 0, pos2) + 1
        indent2 = bytes()
        for b_ in cdi_bytes[line_s2:pos2]:
            if b_ in (9, 32): indent2 += bytes([b_])
            else: break
        
        eol2 = b'\r\n' if b'\r\n' in cdi_bytes[:100] else b'\n'
        
        new_entries = (
            eol2 + indent2 +
            b'<Metadata name="DataProcessor.' + "ТестыРМК".encode("utf-8") + b'" id="' + 
            TESTS_RMK_UUID.encode() + b'" configVersion="a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d600000000" />' +
            eol2 + indent2 +
            b'<Metadata name="DataProcessor.' + "ТестыРМК".encode("utf-8") + b'.Form.' + 
            "Форма".encode("utf-8") + b'" id="' + FORM_UUID.encode() + b'" configVersion="b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e700000000" />' +
            eol2 + indent2 +
            b'<Metadata name="DataProcessor.' + "ТестыРМК".encode("utf-8") + b'.Form.' + 
            "Форма".encode("utf-8") + b'.Form" id="' + FORM_UUID.encode() + b'.0" configVersion="c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f800000000" />'
        )
        
        cdi_new = cdi_bytes[:nl2] + new_entries + cdi_bytes[nl2:]
        cdi_path.write_bytes(cdi_new)
        print(f"  [OK] ConfigDumpInfo.xml: {len(cdi_bytes)} -> {len(cdi_new)}b")

# Шаг 4: Копируем в Конфигурация/ (не Проверка)
print()
print("== Синхронизируем Конфигурация/ ==")
for fname in ["Configuration.xml", "ConfigDumpInfo.xml"]:
    src = PROVERKA / fname
    dst = ROOT / "Конфигурация" / fname
    shutil.copy2(str(src), str(dst))
    print(f"  [OK] {fname}")

# Копируем ТестыРМК в Конфигурация/DataProcessors/ тоже
for rel_path in rmk_files:
    src_p = ROOT / rel_path.replace("/", "\\")
    dst_p = ROOT / rel_path.replace("Конфигурация/Проверка/", "Конфигурация/").replace("/", "\\")
    dst_p.parent.mkdir(parents=True, exist_ok=True)
    if src_p.exists():
        shutil.copy2(str(src_p), str(dst_p))
        print(f"  [OK] Синхр: {dst_p.name}")

print()
print("Готово! Запускай деплой.")
