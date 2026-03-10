# -*- coding: utf-8 -*-
"""Deploy MCP Extension to 1C database."""
import subprocess
import sys
import pathlib
import datetime
import time

V8EXE = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
BASE_PATH = r"D:\Confiq\Public Trade Module"
EXT_PATH = r"D:\Git\Public_Trade_Module\MCP_Extension"
LOG_DIR = pathlib.Path(r"D:\Git\Public_Trade_Module\logs")
USER = "Admin"
EXTENSION_NAME = "MCP_\u0421\u0435\u0440\u0432\u0435\u0440"  # MCP_Сервер
TIMEOUT = 120

def run_1c(step_name, extra_args):
    """Run 1cv8.exe with given args and return (exit_code, log_content)."""
    LOG_DIR.mkdir(exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = LOG_DIR / f"1c-ext-{step_name}-{ts}.log"

    args = [
        V8EXE, "DESIGNER",
        "/F", BASE_PATH,
        "/N", USER,
    ] + extra_args + [
        "/DisableStartupDialogs",
        "/DisableStartupMessages",
        "/Out", str(log_file),
    ]

    print(f"\n{'='*60}")
    print(f"[{step_name}] Starting...")
    print(f"Command: {' '.join(args[:6])} ...")
    print(f"Timeout: {TIMEOUT}s")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            args,
            capture_output=True,
            timeout=TIMEOUT,
            text=True,
            encoding="cp1251",
            errors="replace",
        )
        exit_code = result.returncode
        stdout = result.stdout or ""
        stderr = result.stderr or ""
    except subprocess.TimeoutExpired:
        print(f"[{step_name}] TIMEOUT after {TIMEOUT}s!")
        return -2, "TIMEOUT"
    except Exception as e:
        print(f"[{step_name}] ERROR: {e}")
        return -1, str(e)

    # Read log file
    log_content = ""
    if log_file.exists():
        try:
            log_content = log_file.read_text(encoding="utf-8-sig", errors="replace")
        except Exception:
            try:
                log_content = log_file.read_text(encoding="cp1251", errors="replace")
            except Exception:
                log_content = "(could not read log)"

    print(f"\n[{step_name}] Exit code: {exit_code}")
    if stdout.strip():
        print(f"[{step_name}] STDOUT: {stdout.strip()[:500]}")
    if stderr.strip():
        print(f"[{step_name}] STDERR: {stderr.strip()[:500]}")
    if log_content.strip():
        print(f"[{step_name}] LOG ({log_file.name}):")
        print(log_content[:2000])
    else:
        print(f"[{step_name}] LOG: (empty)")

    return exit_code, log_content


def main():
    print("=" * 60)
    print("  DEPLOY MCP EXTENSION: MCP_\u0421\u0435\u0440\u0432\u0435\u0440")
    print("=" * 60)

    # Step 1: Load extension from files
    print("\n\u0428\u0430\u0433 1: \u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430 \u0440\u0430\u0441\u0448\u0438\u0440\u0435\u043d\u0438\u044f \u0438\u0437 \u0444\u0430\u0439\u043b\u043e\u0432 (LoadConfigFromFiles)...")
    exit_code, log = run_1c("load", [
        "/LoadConfigFromFiles", EXT_PATH,
        "-Extension", EXTENSION_NAME,
    ])

    if exit_code != 0:
        print(f"\n\u041e\u0428\u0418\u0411\u041a\u0410 \u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0438! Exit code: {exit_code}")
        print("\u041f\u0440\u043e\u0432\u0435\u0440\u044c\u0442\u0435:")
        print("  1. \u041a\u043e\u043d\u0444\u0438\u0433\u0443\u0440\u0430\u0442\u043e\u0440 \u0437\u0430\u043a\u0440\u044b\u0442")
        print("  2. MCP-\u0441\u0435\u0440\u0432\u0435\u0440 \u043d\u0435 \u0431\u043b\u043e\u043a\u0438\u0440\u0443\u0435\u0442 \u0418\u0411")
        print("  3. XML-\u0444\u0430\u0439\u043b\u044b \u043a\u043e\u0440\u0440\u0435\u043a\u0442\u043d\u044b")
        sys.exit(1)

    print("\n\u2705 \u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430 \u0443\u0441\u043f\u0435\u0448\u043d\u0430!")

    # Brief pause
    time.sleep(2)

    # Step 2: Update database configuration for extension
    print("\n\u0428\u0430\u0433 2: \u041e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u0435 \u0411\u0414 \u0440\u0430\u0441\u0448\u0438\u0440\u0435\u043d\u0438\u044f (UpdateDBCfg)...")
    exit_code, log = run_1c("update", [
        "/UpdateDBCfg",
        "-Extension", EXTENSION_NAME,
    ])

    if exit_code != 0:
        print(f"\n\u041e\u0428\u0418\u0411\u041a\u0410 \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u044f \u0411\u0414! Exit code: {exit_code}")
        sys.exit(2)

    print("\n\u2705 \u041e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u0435 \u0411\u0414 \u0443\u0441\u043f\u0435\u0448\u043d\u043e!")
    print("\n" + "=" * 60)
    print("  \u0414\u0415\u041f\u041b\u041e\u0419 \u0420\u0410\u0421\u0428\u0418\u0420\u0415\u041d\u0418\u042f \u0417\u0410\u0412\u0415\u0420\u0428\u0401\u041d \u0423\u0421\u041f\u0415\u0428\u041d\u041e!")
    print("=" * 60)
    print("\n\u041f\u0435\u0440\u0435\u0437\u0430\u043f\u0443\u0441\u0442\u0438\u0442\u0435 MCP-\u0441\u0435\u0440\u0432\u0435\u0440 \u0434\u043b\u044f \u043f\u043e\u044f\u0432\u043b\u0435\u043d\u0438\u044f \u043d\u043e\u0432\u043e\u0433\u043e \u0438\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442\u0430 generate_form.")


if __name__ == "__main__":
    main()
