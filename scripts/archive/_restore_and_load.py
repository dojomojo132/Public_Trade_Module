# -*- coding: utf-8 -*-
"""
1. Dump CommonTemplates from current ИБ to a temp folder
2. Restore pre-refactor backup files (without CommonTemplates)
3. Copy full CommonTemplates over
4. Load into ИБ
"""
import subprocess, pathlib, shutil, sys

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
IB_PATH = pathlib.Path(r"D:\Confiq\Public Trade Module")
CFG_DIR = ROOT / "Конфигурация"
CT_DIR = CFG_DIR / "CommonTemplates"
TEMP_CT = ROOT / "_backups" / "_ct_full_dump"
BACKUP_DIR = ROOT / "_backups" / "2026-03-20_224120"
REFERENCE_DIR = ROOT / "_backups" / "_reference"


def find_1cv8():
    v8_dir = pathlib.Path(r"C:\Program Files\1cv8")
    for v in sorted(
        [d for d in v8_dir.iterdir() if d.is_dir() and d.name[0].isdigit()],
        key=lambda d: d.name, reverse=True,
    ):
        exe = v / "bin" / "1cv8.exe"
        if exe.exists():
            return str(exe)
    raise FileNotFoundError("1cv8.exe not found")


def run_1cv8(args_str, label, timeout=300):
    exe = find_1cv8()
    cmd = f'"{exe}" DESIGNER /F "{IB_PATH}" /N "Admin" /DisableStartupDialogs {args_str}'
    print(f"\n=== {label} ===")
    print(f"CMD: {cmd}")
    r = subprocess.run(cmd, shell=True, capture_output=True, timeout=timeout)
    print(f"Exit code: {r.returncode}")
    return r.returncode


def main():
    log = ROOT / "_deploy_direct_output.txt"

    # Step 1: Dump current ИБ to get full CommonTemplates
    print("STEP 1: Dumping current ИБ to get complete CommonTemplates...")
    dump_dir = ROOT / "_backups" / "_full_dump_temp"
    if dump_dir.exists():
        shutil.rmtree(dump_dir)
    dump_dir.mkdir(parents=True)

    rc = run_1cv8(
        f'/DumpConfigToFiles "{dump_dir}" /Out "{log}"',
        "DumpConfigToFiles (full ИБ)",
        timeout=300,
    )
    if log.exists():
        txt = log.read_text(encoding="utf-8-sig", errors="replace")
        print(f"Log ({len(txt)} chars): {txt[:300]}")

    dumped_ct = dump_dir / "CommonTemplates"
    if not dumped_ct.exists():
        print("ERROR: CommonTemplates not found in dump!")
        sys.exit(1)

    ct_files = list(dumped_ct.rglob("*"))
    print(f"Dumped CommonTemplates: {len(ct_files)} files/dirs")

    # Step 2: Save full CommonTemplates to _reference
    print("\nSTEP 2: Updating _reference/CommonTemplates with full dump...")
    ref_ct = REFERENCE_DIR / "CommonTemplates"
    if ref_ct.exists():
        shutil.rmtree(ref_ct)
    shutil.copytree(dumped_ct, ref_ct)
    print(f"Updated _reference/CommonTemplates")

    # Step 3: Restore pre-refactor backup (overwrites Конфигурация/ without CommonTemplates)
    print("\nSTEP 3: Restoring pre-refactor backup files...")
    for src_name in ["Конфигурация", "MCP_Extension"]:
        src = BACKUP_DIR / src_name
        dst = ROOT / src_name
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"  ✓ {src_name}/ restored from backup")

    # Step 4: Copy full CommonTemplates from dump
    print("\nSTEP 4: Copying full CommonTemplates...")
    ct_dst = CFG_DIR / "CommonTemplates"
    if ct_dst.exists():
        shutil.rmtree(ct_dst)
    shutil.copytree(dumped_ct, ct_dst)
    ct_count = len(list(ct_dst.rglob("*.xml")))
    print(f"  ✓ CommonTemplates restored: {ct_count} XML files")

    # Cleanup temp dump
    shutil.rmtree(dump_dir)
    print("  ✓ Temp dump cleaned up")

    # Step 5: Load into ИБ
    print("\nSTEP 5: Loading config into ИБ...")
    rc = run_1cv8(
        f'/LoadConfigFromFiles "{CFG_DIR}" /Out "{log}" -force',
        "LoadConfigFromFiles",
        timeout=300,
    )
    if log.exists():
        txt = log.read_text(encoding="utf-8-sig", errors="replace")
        lines = txt.strip().splitlines()
        err_lines = [l for l in lines if "не существует" in l.lower() or "ошибка" in l.lower()]
        ok_lines = [l for l in lines if "успешно" in l.lower() or "загружен" in l.lower()]
        print(f"Log: {len(lines)} lines, {len(err_lines)} errors")
        for e in err_lines[:5]:
            print(f"  ERR: {e[:120]}")
        for o in ok_lines:
            print(f"  OK: {o[:120]}")

    if rc != 0 and not any("успешно" in l.lower() for l in (txt.strip().splitlines() if log.exists() else [])):
        print("FAIL: LoadConfigFromFiles")
        sys.exit(1)

    # Step 6: UpdateDBCfg
    print("\nSTEP 6: Updating database...")
    rc = run_1cv8(
        f'/UpdateDBCfg /Out "{log}"',
        "UpdateDBCfg",
        timeout=300,
    )
    if log.exists():
        txt = log.read_text(encoding="utf-8-sig", errors="replace")
        print(f"Log: {txt[:500]}")

    print("\n=== DONE ===")


if __name__ == "__main__":
    main()
