# -*- coding: utf-8 -*-
"""
Проверка работоспособности фреймворка после развёртывания.
Запуск: python scripts/verify_setup.py
"""
import pathlib
import sys
import subprocess

PROJ_ROOT = pathlib.Path(__file__).resolve().parent.parent
OK = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
WARN = "\033[93m⚠\033[0m"
errors = 0


def check(label: str, ok: bool, detail: str = ""):
    global errors
    if ok:
        print(f"  {OK} {label}")
    else:
        print(f"  {FAIL} {label}" + (f" — {detail}" if detail else ""))
        errors += 1


def warn(label: str, detail: str = ""):
    print(f"  {WARN} {label}" + (f" — {detail}" if detail else ""))


print("=" * 60)
print("Проверка 1С Copilot Agent Framework")
print("=" * 60)

# ── 1. Конфиг ─────────────────────────────────────────────
print("\n[1] Конфигурация проекта")
config_path = PROJ_ROOT / ".github" / "project-config.yml"
check("project-config.yml существует", config_path.exists())

cfg = None
if config_path.exists():
    sys.path.insert(0, str(PROJ_ROOT / "scripts"))
    try:
        import _project_config as pc
        cfg = pc.load_config()
        check("YAML парсится успешно", True)
        name = pc.get("project.name", "")
        check(f"project.name = '{name}'", bool(name), "не задано")
        ib = pc.infobase_path()
        check(f"paths.infobase = '{ib}'", bool(ib), "не задано")
        ib_exists = pathlib.Path(ib).exists() if ib else False
        if ib_exists:
            check("Информационная база существует", True)
        else:
            warn("Информационная база не найдена", f"путь: {ib}")
    except Exception as e:
        check("YAML парсится успешно", False, str(e))

# ── 2. Файловая структура ─────────────────────────────────
print("\n[2] Файловая структура")
required_files = {
    ".github/copilot-instructions.md": "Главные инструкции Copilot",
    ".github/agents/orchestrator.agent.md": "Оркестратор",
    ".github/agents/1c-coder.agent.md": "BSL-разработчик",
    ".github/agents/1c-deployer.agent.md": "Деплоер",
    ".github/skills/1c-deploy/SKILL.md": "Скилл деплоя",
    ".github/skills/1c-metadata-check/SKILL.md": "Скилл MCP-проверок",
    ".github/instructions/bsl.instructions.md": "BSL-инструкция",
    ".github/instructions/xml-1c.instructions.md": "XML-инструкция",
    "scripts/_project_config.py": "Читатель конфига",
    "scripts/_ps_wrapper.py": "PowerShell-обёртка",
    "scripts/_local_backup.py": "Локальный бэкап",
}
for rel, desc in required_files.items():
    check(f"{desc} ({rel})", (PROJ_ROOT / rel).exists())

# ── 3. Конфигурация 1С ────────────────────────────────────
print("\n[3] Конфигурация 1С")
if cfg:
    cr = pc.config_root()
    check(f"Папка выгрузки существует ({cr.name}/)", cr.exists())
    if cr.exists():
        conf_xml = cr / "Configuration.xml"
        check("Configuration.xml найден", conf_xml.exists())
        cdi = cr / "ConfigDumpInfo.xml"
        check("ConfigDumpInfo.xml найден", cdi.exists())
        if not conf_xml.exists():
            warn("Нужно выполнить Dump: python scripts/_ps_wrapper.py deploy -Action Dump")

# ── 4. PowerShell скрипты ──────────────────────────────────
print("\n[4] PowerShell-скрипты деплоя")
if cfg:
    val_dir = PROJ_ROOT / pc.get("paths.validation", "Документация/Валидация")
    for ps1 in ["deploy-config.ps1", "validate-config.ps1", "monitor-errors.ps1"]:
        check(f"{ps1}", (val_dir / ps1).exists())

# ── 5. Документация ────────────────────────────────────────
print("\n[5] Документация")
if cfg:
    docs = PROJ_ROOT / pc.get("paths.docs", "Документация")
    check("КРИТИЧЕСКИЕ_ОШИБКИ.md", (docs / "КРИТИЧЕСКИЕ_ОШИБКИ.md").exists())
    check("ЖУРНАЛ_ПРОИЗВОДИТЕЛЬНОСТИ.md", (docs / "ЖУРНАЛ_ПРОИЗВОДИТЕЛЬНОСТИ.md").exists())
    tpl = PROJ_ROOT / pc.get("paths.templates", "Документация/Шаблоны")
    if tpl.exists():
        tpl_count = len(list(tpl.glob("*.xml")))
        check(f"XML-шаблоны ({tpl_count} шт)", tpl_count > 0, "папка пуста")
    else:
        warn("Папка шаблонов не найдена", str(tpl))

# ── 6. MCP (опционально) ──────────────────────────────────
print("\n[6] MCP-серверы (опционально)")
if cfg:
    prefix = pc.get("mcp.onec.prefix", "")
    check(f"MCP 1С префикс задан: '{prefix}'", bool(prefix))
    obs_enabled = pc.get("mcp.obsidian.enabled", False)
    if obs_enabled:
        check("Obsidian MCP включён", True)
    else:
        warn("Obsidian MCP отключён — Knowledge Graph не будет обновляться")
    dbg_enabled = pc.get("mcp.debug.enabled", False)
    if dbg_enabled:
        check("Debug MCP включён", True)
    else:
        warn("Debug MCP отключён — отладка недоступна")

# ── 7. Git ─────────────────────────────────────────────────
print("\n[7] Git")
git_dir = PROJ_ROOT / ".git"
check("Git-репозиторий инициализирован", git_dir.exists())
gitignore = PROJ_ROOT / ".gitignore"
check(".gitignore существует", gitignore.exists())
if gitignore.exists():
    content = gitignore.read_text(encoding="utf-8", errors="ignore")
    check("_backups/ в .gitignore", "_backups" in content, "добавь _backups/ в .gitignore")

# ── Итого ──────────────────────────────────────────────────
print("\n" + "=" * 60)
if errors == 0:
    print(f"{OK} Все проверки пройдены! Фреймворк готов к работе.")
    print(f"\nСледующий шаг:")
    print(f"  1. Выгрузить конфигурацию: python scripts/_ps_wrapper.py deploy -Action Dump")
    print(f"  2. Открыть VS Code Chat → /1c-new-task")
else:
    print(f"{FAIL} Обнаружено ошибок: {errors}")
    print(f"\nИсправь ошибки выше и запусти проверку повторно:")
    print(f"  python scripts/verify_setup.py")

print("=" * 60)
sys.exit(errors)
