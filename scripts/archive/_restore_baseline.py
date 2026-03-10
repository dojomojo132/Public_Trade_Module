# -*- coding: utf-8 -*-
"""
Полный бинарный сброс Конфигурация/Проверка к состоянию git 09e34c3,
с сохранением файлов ТестыРМК:
1. Получаем список файлов, изменённых между 09e34c3 и HEAD в Конфигурация/Проверка/
2. Восстанавливаем их из git 09e34c3 через "git show ...:.../файл"
3. Затем добавляем ТестыРМК в Configuration.xml и ConfigDumpInfo.xml (в LF)
4. Восстанавливаем то же самое в Конфигурация/ (не Проверка)
"""

import subprocess
import pathlib
import sys

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
PROVERKA = ROOT / "Конфигурация" / "Проверка"
KONF = ROOT / "Конфигурация"

BASELINE = "09e34c3"

def git_show_bytes(commit, rel_path_forward_slash):
    """Получить файл из git. rel_path — относительно корня репозитория, / разделитель."""
    result = subprocess.run(
        ["git", "show", f"{commit}:{rel_path_forward_slash}"],
        capture_output=True,
        cwd=str(ROOT)
    )
    if result.returncode == 0:
        return result.stdout
    return None

def git_diff_names(commit_a, commit_b, path_prefix):
    """Список файлов, изменённых между двумя коммитами в указанной папке."""
    result = subprocess.run(
        ["git", "diff", "--name-only", commit_a, commit_b, "--", path_prefix],
        capture_output=True, text=True, encoding="utf-8",
        cwd=str(ROOT)
    )
    if result.returncode == 0:
        return [l.strip() for l in result.stdout.splitlines() if l.strip()]
    return []

# ============================================================
print(f"=== Шаг 1: Файлы, изменённые между {BASELINE} и HEAD ===")
changed = git_diff_names(BASELINE, "HEAD", "Конфигурация/Проверка")
print(f"Изменено файлов: {len(changed)}")
for f in changed:
    print(f"  {f}")

# ============================================================
print()
print(f"=== Шаг 2: Восстанавливаем файлы из {BASELINE} ===")

SKIP_FOR_RESTORE = {
    # ТестыРМК — новые файлы, их НЕ нужно восстанавливать (их нет в 09e34c3)
}

restored = 0
skipped = 0
errors = 0

for rel_path in changed:
    # Пропускаем ТестыРМК — это новые файлы
    if "ТестыРМК" in rel_path:
        print(f"  [SKIP] {rel_path} (новый файл ТестыРМК)")
        skipped += 1
        continue
    
    # Получаем оригинальный файл из git
    old_bytes = git_show_bytes(BASELINE, rel_path.replace("\\", "/"))
    if old_bytes is None:
        print(f"  [ERROR] Не удалось получить {rel_path}")
        errors += 1
        continue
    
    # Путь на диске
    disk_path = ROOT / rel_path.replace("/", "\\")
    
    if disk_path.exists():
        old_size = disk_path.stat().st_size
    else:
        old_size = 0
    
    disk_path.write_bytes(old_bytes)
    print(f"  [OK] {disk_path.name}: {old_size} -> {len(old_bytes)} байт")
    restored += 1

print(f"\nВосстановлено: {restored}, пропущено: {skipped}, ошибок: {errors}")

# ============================================================
print()
print("=== Шаг 3: Добавляем ТестыРМК в Configuration.xml ===")

cfg_path = PROVERKA / "Configuration.xml"
cfg_bytes = cfg_path.read_bytes()

# Проверяем что ТестыРМК ещё не добавлен
if b"\xd2\xb5\xd1\x81\xd1\x82\xd1\x8b\xd0\xa0\xd0\x9c\xd0\x9a" in cfg_bytes or "ТестыРМК".encode("utf-8") in cfg_bytes:
    print("  [INFO] ТестыРМК уже есть в Configuration.xml")
else:
    # Ищем место вставки: после ТестовоеЗаполнениеДанных
    marker = "ТестовоеЗаполнениеДанных".encode("utf-8")
    # Ищем строку <DataProcessor>ТестовоеЗаполнениеДанных</DataProcessor>
    search = b"<DataProcessor>" + marker + b"</DataProcessor>"
    pos = cfg_bytes.find(search)
    if pos == -1:
        print(f"  [ERR] Маркер не найден в Configuration.xml!")
    else:
        # Вставляем ПОСЛЕ этой строки (после \n)
        end_pos = pos + len(search)
        # Ищем следующий \n после маркера
        nl_pos = cfg_bytes.find(b"\n", end_pos)
        if nl_pos == -1:
            nl_pos = end_pos
        
        # Добавляем новую строку с той же отступом
        # Смотрим какой отступ у текущей строки
        line_start = cfg_bytes.rfind(b"\n", 0, pos)
        indent = b""
        for b_ in cfg_bytes[line_start+1:pos]:
            if b_ in (ord('\t'), ord(' ')):
                indent += bytes([b_])
            else:
                break
        
        new_entry = b"\n" + indent + b"<DataProcessor>" + "ТестыРМК".encode("utf-8") + b"</DataProcessor>"
        cfg_bytes_new = cfg_bytes[:nl_pos] + new_entry + cfg_bytes[nl_pos:]
        cfg_path.write_bytes(cfg_bytes_new)
        print(f"  [OK] Добавлен ТестыРМК в Configuration.xml ({len(cfg_bytes)} -> {len(cfg_bytes_new)} байт)")

# ============================================================
print()
print("=== Шаг 4: Добавляем ТестыРМК в ConfigDumpInfo.xml ===")

cdi_path = PROVERKA / "ConfigDumpInfo.xml"
cdi_bytes = cdi_path.read_bytes()

TESTS_RMK_UUID = "f7a8b9c0-d1e2-4f3a-5b6c-7d8e9f0a1b2c"
FORM_UUID = "a2b3c4d5-e6f7-4a8b-9c0d-e1f2a3b4c5d6"

if TESTS_RMK_UUID.encode("ascii") in cdi_bytes:
    print("  [INFO] ТестыРМК уже есть в ConfigDumpInfo.xml")
else:
    # Ищем место вставки: после ТестовоеЗаполнениеДанных entries
    marker_cdi = ("DataProcessor.ТестовоеЗаполнениеДанных").encode("utf-8")
    pos2 = cdi_bytes.rfind(marker_cdi)
    if pos2 == -1:
        print("  [ERR] Маркер ТестовоеЗаполнениеДанных не найден в CDI!")
    else:
        # Ищем конец этой записи (закрывающий тег />  или >)
        end_tag = cdi_bytes.find(b"/>", pos2)
        nl_pos2 = cdi_bytes.find(b"\n", end_tag)
        if nl_pos2 == -1:
            nl_pos2 = end_tag + 2
        
        # Определяем отступ
        line_start2 = cdi_bytes.rfind(b"\n", 0, pos2)
        indent2 = b""
        for b_ in cdi_bytes[line_start2+1:pos2]:
            if b_ in (ord('\t'), ord(' ')):
                indent2 += bytes([b_])
            else:
                break
        
        new_entries = (
            b"\n" + indent2 + 
            b'<Metadata name="DataProcessor.' + "ТестыРМК".encode("utf-8") + b'" id="' + TESTS_RMK_UUID.encode("ascii") + b'" configVersion="a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d600000000" />' +
            b"\n" + indent2 + 
            b'<Metadata name="DataProcessor.' + "ТестыРМК".encode("utf-8") + b'.Form.' + "Форма".encode("utf-8") + b'" id="' + FORM_UUID.encode("ascii") + b'" configVersion="b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e700000000" />' +
            b"\n" + indent2 + 
            b'<Metadata name="DataProcessor.' + "ТестыРМК".encode("utf-8") + b'.Form.' + "Форма".encode("utf-8") + b'.Form" id="' + FORM_UUID.encode("ascii") + b'.0" configVersion="c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f800000000" />'
        )
        
        cdi_bytes_new = cdi_bytes[:nl_pos2] + new_entries + cdi_bytes[nl_pos2:]
        cdi_path.write_bytes(cdi_bytes_new)
        print(f"  [OK] Добавлен ТестыРМК в ConfigDumpInfo.xml ({len(cdi_bytes)} -> {len(cdi_bytes_new)} байт)")

# ============================================================
print()
print("=== Шаг 5: Синхронизируем с Конфигурация/ (не Проверка) ===")

import shutil

# Синхронизируем только Configuration.xml и ConfigDumpInfo.xml
for fname in ["Configuration.xml", "ConfigDumpInfo.xml"]:
    src = PROVERKA / fname
    dst = KONF / fname
    if src.exists():
        shutil.copy2(str(src), str(dst))
        print(f"  [OK] {fname} скопирован из Проверка/ в Конфигурация/")
    else:
        print(f"  [!] {fname} не найден в Проверка/")

# ============================================================
print()
print("=== Итоговая проверка ===")
for fname in ["Configuration.xml", "ConfigDumpInfo.xml"]:
    for p in [PROVERKA / fname, KONF / fname]:
        b = p.read_bytes()
        crlf = b.count(b'\r\n')
        bom = "BOM✓" if b[:3] == b'\xef\xbb\xbf' else "BOM✗"
        rmk = "ТестыРМК✓" if "ТестыРМК".encode("utf-8") in b else "ТестыРМК✗"
        print(f"  {p.relative_to(ROOT)}: {bom} CRLF={crlf} {rmk} {len(b)}b")

print("\nГотово!")
