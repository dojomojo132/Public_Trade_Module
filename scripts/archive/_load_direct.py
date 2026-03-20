# -*- coding: utf-8 -*-
"""Direct load config from files into ИБ, bypassing validate-config.ps1."""
import subprocess, pathlib, sys

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
IB_PATH = pathlib.Path(r"D:\Confiq\Public Trade Module")
CFG_DIR = ROOT / "Конфигурация"


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


def run_1cv8(args, label, timeout=300):
    print(f"\n=== {label} ===")
    exe = find_1cv8()
    cmd_str = f'"{exe}" DESIGNER /F "{IB_PATH}" /N "Admin" /DisableStartupDialogs {" ".join(args)}'
    print(f"CMD: {cmd_str}")
    r = subprocess.run(cmd_str, shell=True, capture_output=True, timeout=timeout)
    out = r.stdout.decode("utf-8", errors="replace")
    err = r.stderr.decode("utf-8", errors="replace")
    if out.strip():
        print(f"STDOUT: {out[:500]}")
    if err.strip():
        print(f"STDERR: {err[:500]}")
    print(f"Exit code: {r.returncode}")
    return r.returncode


def main():
    log = ROOT / "_deploy_direct_output.txt"

    # Step 1: LoadConfigFromFiles
    rc = run_1cv8(
        [f'/LoadConfigFromFiles "{CFG_DIR}"', f'/Out "{log}"', "-force"],
        "LoadConfigFromFiles",
        timeout=180,
    )
    if log.exists():
        txt = log.read_text(encoding="utf-8-sig", errors="replace")
        print(f"Log ({len(txt)} chars): {txt[:1000]}")
    if rc != 0:
        print("FAIL: LoadConfigFromFiles")
        sys.exit(1)

    # Step 2: UpdateDBCfg
    rc = run_1cv8(
        [f'/UpdateDBCfg', f'/Out "{log}"'],
        "UpdateDBCfg",
        timeout=180,
    )
    if log.exists():
        txt = log.read_text(encoding="utf-8-sig", errors="replace")
        print(f"Log ({len(txt)} chars): {txt[:1000]}")
    if rc != 0:
        print("FAIL: UpdateDBCfg")
        sys.exit(1)

    print("\n=== SUCCESS: Config loaded and DB updated ===")


if __name__ == "__main__":
    main()
