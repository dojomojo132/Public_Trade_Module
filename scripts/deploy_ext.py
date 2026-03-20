# -*- coding: utf-8 -*-
"""
Инструмент для работы с расширениями конфигурации 1С PTM.

Использование:
    python scripts/deploy_ext.py --ext PTM_Analytics --action Full
    python scripts/deploy_ext.py --ext PTM_Analytics --action Dump
    python scripts/deploy_ext.py --ext PTM_Analytics --action Load
    python scripts/deploy_ext.py --ext PTM_Analytics --action Update
    python scripts/deploy_ext.py --ext MCP_Сервер --action Full

Действия:
    Full   — Загрузить из папки + обновить БД (полный цикл деплоя, ~15 сек)
    Dump   — Выгрузить из ИБ в папку (для редактирования)
    Load   — Загрузить из папки в ИБ (только LoadConfigFromFiles)
    Update — Обновить конфигурацию БД расширения (только UpdateDBCfg)
    Check  — Выгрузить из ИБ + показать список файлов (диагностика)

Папки расширений (по умолчанию):
    PTM_Analytics  →  Конфигурация_PTM_Analytics/
    MCP_Сервер     →  MCP_Extension/
    <любое>        →  Конфигурация_<имя>/

Переопределить папку: --dir <путь>

ВАЖНО: Перед первым использованием новое расширение нужно создать
       в Конфигураторе вручную (Конфигурация → Расширения → Создать).
       После этого один раз выполнить --action Dump для инициализации папки.
"""
import argparse
import subprocess
import pathlib
import sys
import time

# ── Константы ─────────────────────────────────────────────────────────────────
IB_PATH   = r"D:\Confiq\Public Trade Module"
PROJ_ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGS_DIR  = PROJ_ROOT / "logs"
USER      = "Админ"

# Маппинг нестандартных папок для известных расширений
_KNOWN_EXT_DIRS: dict[str, str] = {
    "MCP_Сервер": "MCP_Extension",
}


# ── Утилиты ───────────────────────────────────────────────────────────────────

def _find_1cv8() -> str:
    """Находит последнюю версию 1cv8.exe."""
    v8_dir = pathlib.Path(r"C:\Program Files\1cv8")
    if v8_dir.exists():
        versions = sorted(
            [d for d in v8_dir.iterdir() if d.is_dir() and d.name[0].isdigit()],
            key=lambda d: d.name,
            reverse=True,
        )
        for v in versions:
            candidate = v / "bin" / "1cv8.exe"
            if candidate.exists():
                return str(candidate)
    raise FileNotFoundError("1cv8.exe не найден в C:\\Program Files\\1cv8")


def _get_ext_dir(ext_name: str, override: str = None) -> pathlib.Path:
    """Возвращает папку XML-файлов расширения."""
    if override:
        return pathlib.Path(override)
    rel = _KNOWN_EXT_DIRS.get(ext_name, f"Конфигурация_{ext_name}")
    return PROJ_ROOT / rel


def _run_1c(v8exe: str, tag: str, extra_args: list, timeout: int = 60) -> int:
    """Запускает Designer с указанными аргументами, пишет лог, возвращает exit code.
    Таймаут 60 сек: если 1С не завершилась — зависла, надо убить и разбираться."""
    LOGS_DIR.mkdir(exist_ok=True)
    log_file = LOGS_DIR / f"ext-{tag}-{int(time.time())}.log"

    args = [
        v8exe, "DESIGNER",
        "/F", IB_PATH,
        "/N", USER,
        *extra_args,
        "/DisableStartupDialogs",
        "/DisableStartupMessages",
        "/Out", str(log_file),
    ]

    print(f"\n{'─' * 60}")
    print(f"[{tag}]")

    t0 = time.time()
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    elapsed = time.time() - t0

    print(f"Exit code: {result.returncode}  ({elapsed:.1f} сек)")

    if log_file.exists():
        for enc in ("utf-8-sig", "utf-8", "cp1251"):
            try:
                content = log_file.read_text(encoding=enc).strip()
                if content:
                    lines = content.splitlines()
                    for line in lines[:25]:
                        if line.strip():
                            print(f"  {line}")
                    if len(lines) > 25:
                        print(f"  ... ({len(lines)} строк — см. {log_file.name})")
                    break
            except Exception:
                continue

    return result.returncode


# ── Действия ──────────────────────────────────────────────────────────────────

def do_dump(v8exe: str, ext_name: str, ext_path: pathlib.Path) -> bool:
    """Выгружает расширение из ИБ в папку на диске."""
    ext_path.mkdir(parents=True, exist_ok=True)
    print(f"Выгрузка расширения '{ext_name}' → {ext_path}")

    code = _run_1c(v8exe, "dump", [
        "/DumpConfigToFiles", str(ext_path),
        "-Extension", ext_name,
    ], timeout=30)

    # exit code 1 — может быть предупреждением, не ошибкой
    if code not in (0, 1):
        print(f"\n❌ ОШИБКА выгрузки (exit {code})")
        return False

    xml_files = list(ext_path.rglob("*.xml"))
    print(f"\n✓ Выгружено {len(xml_files)} XML-файлов в {ext_path.name}/")
    for f in sorted(xml_files)[:12]:
        print(f"  {f.relative_to(ext_path)}")
    if len(xml_files) > 12:
        print(f"  ... ещё {len(xml_files) - 12} файлов")
    return True


def do_load(v8exe: str, ext_name: str, ext_path: pathlib.Path) -> bool:
    """Загружает расширение из папки в ИБ."""
    if not ext_path.exists():
        print(f"❌ Папка не найдена: {ext_path}")
        print(f"   Сначала: --action Dump  (или создайте расширение в Конфигураторе)")
        return False

    xml_count = len(list(ext_path.rglob("*.xml")))
    print(f"Загрузка расширения '{ext_name}' ← {ext_path}  ({xml_count} XML-файлов)")

    code = _run_1c(v8exe, "load", [
        "/LoadConfigFromFiles", str(ext_path),
        "-Extension", ext_name,
    ], timeout=60)

    if code not in (0, 1):
        print(f"\n❌ ОШИБКА загрузки (exit {code})")
        return False

    print(f"\n✓ Расширение '{ext_name}' загружено в ИБ")
    return True


def do_update(v8exe: str, ext_name: str) -> bool:
    """Обновляет конфигурацию БД для расширения."""
    print(f"Обновление БД расширения '{ext_name}'")

    code = _run_1c(v8exe, "update", [
        "/UpdateDBCfg",
        "-Extension", ext_name,
    ], timeout=30)

    if code not in (0, 1):
        print(f"\n❌ ОШИБКА обновления БД (exit {code})")
        return False

    print(f"\n✓ БД расширения '{ext_name}' обновлена")
    return True


# ── Точка входа ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Управление расширениями конфигурации 1С PTM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--ext", required=True,
        help="Имя расширения (например: PTM_Analytics, MCP_Сервер)",
    )
    parser.add_argument(
        "--action", required=True,
        choices=["Full", "Dump", "Load", "Update", "Check"],
        help="Full=Load+Update | Dump=выгрузить | Load=загрузить | Update=UpdateDBCfg | Check=Dump+список",
    )
    parser.add_argument(
        "--dir", default=None,
        help="Папка с XML-файлами (по умолчанию: Конфигурация_<ExtName>/)",
    )
    args = parser.parse_args()

    try:
        v8exe = _find_1cv8()
        print(f"1cv8.exe: {v8exe}")
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)

    ext_name = args.ext
    ext_path = _get_ext_dir(ext_name, args.dir)

    print(f"\n{'═' * 60}")
    print(f"PTM Extension Tool")
    print(f"  Расширение : {ext_name}")
    print(f"  Действие   : {args.action}")
    print(f"  Папка      : {ext_path}")
    print(f"{'═' * 60}")

    action = args.action

    if action in ("Dump", "Check"):
        ok = do_dump(v8exe, ext_name, ext_path)

    elif action == "Load":
        ok = do_load(v8exe, ext_name, ext_path)

    elif action == "Update":
        ok = do_update(v8exe, ext_name)

    elif action == "Full":
        print("\nПолный цикл: Load → Update")
        ok = do_load(v8exe, ext_name, ext_path)
        if ok:
            ok = do_update(v8exe, ext_name)
        if ok:
            print(f"\n{'═' * 60}")
            print(f"✓ Деплой '{ext_name}' ВЫПОЛНЕН ({time.strftime('%H:%M:%S')})")
            print(f"{'═' * 60}")

    else:
        ok = False

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
