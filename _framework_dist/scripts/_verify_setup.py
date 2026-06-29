"""
Скрипт проверки развёртывания Copilot Agent Framework для 1С.
Запускать после копирования фреймворка в новый проект.

Использование:
    python scripts/_verify_setup.py
"""
import pathlib
import sys
import subprocess

PROJ_ROOT = pathlib.Path(__file__).resolve().parent.parent
ERRORS: list[str] = []
WARNINGS: list[str] = []
OK: list[str] = []


def check(condition: bool, ok_msg: str, fail_msg: str, is_warning: bool = False):
    if condition:
        OK.append(f"  ✅ {ok_msg}")
    elif is_warning:
        WARNINGS.append(f"  ⚠️ {fail_msg}")
    else:
        ERRORS.append(f"  ❌ {fail_msg}")


def main():
    print("=" * 60)
    print("  Проверка развёртывания 1С Copilot Agent Framework")
    print("=" * 60)
    print()

    # ── 1. project-config.yml ──────────────────────────────────
    print("1. Конфигурация проекта")
    config_path = PROJ_ROOT / ".github" / "project-config.yml"
    check(config_path.exists(),
          "project-config.yml найден",
          "project-config.yml НЕ НАЙДЕН — создайте .github/project-config.yml")

    cfg = None
    if config_path.exists():
        try:
            sys.path.insert(0, str(PROJ_ROOT / "scripts"))
            from _project_config import load_config, get
            cfg = load_config()
            check(True, "project-config.yml читается без ошибок", "")
        except Exception as e:
            check(False, "", f"Ошибка парсинга project-config.yml: {e}")

    if cfg:
        name = get("project.name", "")
        check(bool(name), f"project.name = '{name}'", "project.name не задан")

        ib = get("paths.infobase", "")
        check(bool(ib), f"paths.infobase = '{ib}'", "paths.infobase не задан")
        if ib:
            ib_path = pathlib.Path(ib)
            check(ib_path.exists(),
                  f"Информационная база найдена: {ib}",
                  f"Путь к ИБ не существует: {ib}",
                  is_warning=True)

        cr = get("paths.config_root", "Конфигурация")
        cr_path = PROJ_ROOT / cr
        check(cr_path.exists(),
              f"Папка конфигурации: {cr}/",
              f"Папка конфигурации НЕ найдена: {cr}/ (сделайте Dump из ИБ)")

    for msg in OK + WARNINGS + ERRORS:
        print(msg)
    OK.clear()
    WARNINGS.clear()
    errors_1 = len(ERRORS)
    ERRORS.clear()
    print()

    # ── 2. Структура .github/ ──────────────────────────────────
    print("2. Структура .github/")
    gh = PROJ_ROOT / ".github"

    required_files = {
        "copilot-instructions.md": "Главная инструкция",
        "project-config.yml": "Конфигурация проекта",
    }
    required_dirs = {
        "agents": "Агенты (5 шт.)",
        "skills": "Скиллы (6 шт.)",
        "instructions": "Инструкции (3 шт.)",
        "prompts": "Промпты",
        "hooks": "Хуки безопасности",
    }

    for fname, desc in required_files.items():
        check((gh / fname).exists(), f"{fname} — {desc}", f"ОТСУТСТВУЕТ: {fname}")

    for dname, desc in required_dirs.items():
        d = gh / dname
        check(d.exists() and d.is_dir(), f"{dname}/ — {desc}", f"ОТСУТСТВУЕТ: {dname}/")

    # Agents
    agents = ["orchestrator", "1c-architect", "1c-coder", "1c-deployer", "1c-form-builder"]
    for a in agents:
        f = gh / "agents" / f"{a}.agent.md"
        check(f.exists(), f"  agent: {a}", f"  ОТСУТСТВУЕТ agent: {a}.agent.md")

    # Skills
    skills = ["1c-bsl-review", "1c-debug", "1c-deploy", "1c-form-generator", "1c-metadata-check", "1c-report"]
    for s in skills:
        f = gh / "skills" / s / "SKILL.md"
        check(f.exists(), f"  skill: {s}", f"  ОТСУТСТВУЕТ skill: {s}/SKILL.md")

    for msg in OK + WARNINGS + ERRORS:
        print(msg)
    OK.clear()
    WARNINGS.clear()
    errors_2 = len(ERRORS)
    ERRORS.clear()
    print()

    # ── 3. Скрипты ─────────────────────────────────────────────
    print("3. Скрипты инфраструктуры")
    scripts_dir = PROJ_ROOT / "scripts"

    required_scripts = [
        "_ps_wrapper.py",
        "_local_backup.py",
        "_project_config.py",
        "_git_commit.py",
        "deploy_ext.py",
    ]
    for s in required_scripts:
        check((scripts_dir / s).exists(), f"scripts/{s}", f"ОТСУТСТВУЕТ: scripts/{s}")

    for msg in OK + WARNINGS + ERRORS:
        print(msg)
    OK.clear()
    WARNINGS.clear()
    errors_3 = len(ERRORS)
    ERRORS.clear()
    print()

    # ── 4. PowerShell скрипты ──────────────────────────────────
    print("4. PowerShell скрипты деплоя")

    val_dir = get("paths.validation", "Документация/Валидация") if cfg else "Документация/Валидация"
    val_path = PROJ_ROOT / val_dir

    ps_scripts = ["deploy-config.ps1", "validate-config.ps1", "monitor-errors.ps1"]
    for s in ps_scripts:
        check((val_path / s).exists(), f"{val_dir}/{s}", f"ОТСУТСТВУЕТ: {val_dir}/{s}")

    for msg in OK + WARNINGS + ERRORS:
        print(msg)
    OK.clear()
    WARNINGS.clear()
    errors_4 = len(ERRORS)
    ERRORS.clear()
    print()

    # ── 5. Конфигурация 1С ─────────────────────────────────────
    print("5. Конфигурация 1С")
    if cfg:
        cr = get("paths.config_root", "Конфигурация")
        cr_path = PROJ_ROOT / cr
        if cr_path.exists():
            config_xml = cr_path / "Configuration.xml"
            dump_info = cr_path / "ConfigDumpInfo.xml"
            check(config_xml.exists(),
                  "Configuration.xml найден",
                  "Configuration.xml НЕ найден — нужен Dump из ИБ")
            check(dump_info.exists(),
                  "ConfigDumpInfo.xml найден",
                  "ConfigDumpInfo.xml НЕ найден — нужен Dump из ИБ")
        else:
            check(False, "", f"Папка {cr}/ не существует — сделайте Dump из ИБ")

    for msg in OK + WARNINGS + ERRORS:
        print(msg)
    OK.clear()
    WARNINGS.clear()
    errors_5 = len(ERRORS)
    ERRORS.clear()
    print()

    # ── 6. Платформа 1С ────────────────────────────────────────
    print("6. Платформа 1С")
    try:
        result = subprocess.run(
            ["where", "1cv8.exe"],
            capture_output=True, text=True, timeout=5,
            encoding="utf-8", errors="replace"
        )
        if result.returncode == 0:
            path_1c = result.stdout.strip().splitlines()[0]
            check(True, f"1cv8.exe найден: {path_1c}", "")
        else:
            check(False, "", "1cv8.exe НЕ найден в PATH", is_warning=True)
    except Exception:
        check(False, "", "Не удалось проверить наличие 1cv8.exe", is_warning=True)

    for msg in OK + WARNINGS + ERRORS:
        print(msg)
    OK.clear()
    WARNINGS.clear()
    errors_6 = len(ERRORS)
    ERRORS.clear()
    print()

    # ── 7. Расширения ──────────────────────────────────────────
    if cfg:
        exts = get("extensions", [])
        if exts:
            print("7. Расширения конфигурации")
            for ext in exts:
                if isinstance(ext, dict):
                    name = ext.get("name", "?")
                    d = ext.get("dir", "")
                    ext_path = PROJ_ROOT / d
                    check(ext_path.exists(),
                          f"Расширение '{name}' → {d}/",
                          f"Папка расширения '{name}' НЕ найдена: {d}/",
                          is_warning=True)
            for msg in OK + WARNINGS + ERRORS:
                print(msg)
            OK.clear()
            WARNINGS.clear()
            ERRORS.clear()
            print()

    # ── Итог ───────────────────────────────────────────────────
    total_errors = errors_1 + errors_2 + errors_3 + errors_4 + errors_5 + errors_6
    print("=" * 60)
    if total_errors == 0:
        print("  ✅ Развёртывание завершено успешно!")
        print()
        print("  Следующий шаг:")
        print("    python scripts/_ps_wrapper.py deploy -Action Dump")
        print()
    else:
        print(f"  ❌ Обнаружено {total_errors} ошибок — исправьте и запустите повторно")
        print()
    print("=" * 60)
    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
