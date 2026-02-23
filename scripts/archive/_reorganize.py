# -*- coding: utf-8 -*-
"""
Реорганизация корня проекта: сортировка файлов по папкам.
Структура:
  scripts/         - активные вспомогательные утилиты
  scripts/archive/ - архивные одноразовые скрипты
  logs/            - лог файлы
"""
import pathlib
import shutil

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")

# === АКТИВНЫЕ СКРИПТЫ (перемещаем в scripts/) ===
ACTIVE_SCRIPTS = [
    "_deploy_full.py",
    "_git_backup.py",
    "_run_deploy.py",
    "_run_monitor.py",
    "_rollback_config.py",
    "_recovery.py",
    "_recreate_ib.py",
    "_reset_and_copy.bat",
]

# === ЛОГ ФАЙЛЫ (перемещаем в logs/) ===
LOG_FILES = [
    "_deploy_log.txt",
    "_dump_log.txt",
    "_ib_log.txt",
    "_load_log.txt",
    "_restore_log.txt",
    "_rmk_analysis.txt",
    "_bpo_diff_files.txt",
    "_metadata_output.txt",
]

# === ФАЙЛЫ КОТОРЫЕ ОСТАЮТСЯ В КОРНЕ ===
KEEP_IN_ROOT = {
    "_ptm_analyze.py",  # используется в тестировании (абсолютный путь в инструкциях)
}

def main():
    # Создаём папки
    scripts_dir = ROOT / "scripts"
    archive_dir = ROOT / "scripts" / "archive"
    logs_dir = ROOT / "logs"

    for d in [scripts_dir, archive_dir, logs_dir]:
        d.mkdir(exist_ok=True)
        print(f"  Папка: {d.relative_to(ROOT)}/")

    print()

    # 1. Переместить активные скрипты
    print("=== Активные скрипты → scripts/ ===")
    for name in ACTIVE_SCRIPTS:
        src = ROOT / name
        if src.exists():
            dst = scripts_dir / name
            shutil.move(str(src), str(dst))
            print(f"  ✓ {name} → scripts/")
        else:
            print(f"  - {name} (не найден)")

    print()

    # 2. Переместить лог файлы
    print("=== Лог файлы → logs/ ===")
    for name in LOG_FILES:
        src = ROOT / name
        if src.exists():
            dst = logs_dir / name
            shutil.move(str(src), str(dst))
            print(f"  ✓ {name} → logs/")
        else:
            print(f"  - {name} (не найден)")

    print()

    # 3. Переместить все остальные _*.py в archive
    print("=== Архивные скрипты → scripts/archive/ ===")
    active_set = set(ACTIVE_SCRIPTS) | KEEP_IN_ROOT

    archived_count = 0
    for f in sorted(ROOT.glob("_*.py")):
        if f.name not in active_set:
            dst = archive_dir / f.name
            shutil.move(str(f), str(dst))
            print(f"  ✓ {f.name} → scripts/archive/")
            archived_count += 1

    # Также переместить _*.bat если не в ACTIVE_SCRIPTS
    for f in sorted(ROOT.glob("_*.bat")):
        if f.name not in active_set:
            dst = archive_dir / f.name
            shutil.move(str(f), str(dst))
            print(f"  ✓ {f.name} → scripts/archive/")
            archived_count += 1

    print(f"\n  Заархивировано: {archived_count} файлов")

    print()
    print("=== Итог ===")
    print(f"  scripts/:         {len(list(scripts_dir.glob('_*.py')))} скриптов")
    print(f"  scripts/archive/: {len(list(archive_dir.glob('*')))} скриптов")
    print(f"  logs/:            {len(list(logs_dir.glob('_*.txt')))} файлов")
    print(f"  Корень:           _ptm_analyze.py (оставлен)")
    print()
    print("Готово!")

if __name__ == "__main__":
    main()
