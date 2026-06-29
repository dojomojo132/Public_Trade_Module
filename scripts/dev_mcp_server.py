# -*- coding: utf-8 -*-
"""
dev-mcp — MCP-сервер для рутинных операций разработки 1С.

Назначение: убрать из ежедневного оборота агента вызовы PowerShell/CLI
с кириллическими путями. Вместо `python scripts/_ps_wrapper.py deploy ...`
агент вызывает MCP-tool `dev_deploy(...)` через JSON-RPC stdio.

Tools:
  dev_status            — health-check окружения
  dev_backup            — локальный бэкап Конфигурация/
  dev_dump              — выгрузить ИБ → файлы
  dev_validate          — валидация XML-конфигурации
  dev_deploy            — Load + UpdateDBCfg основной конфигурации
  dev_monitor           — мониторинг журнала ИБ за N минут
  dev_ext               — операции с расширением (Full/Dump/Load/Update)
  dev_sync_obsidian     — синхронизация графа знаний
  dev_sync_bench        — sync боевой проект → песочница ModelBench (только для тестов моделей)

Реализация: тонкий фасад над существующими скриптами.
PowerShell вызывается через -EncodedCommand (UTF-16LE Base64) — единственный
надёжный способ передать кириллицу без зависимости от настроек терминала.
"""

import base64
import datetime
import io
import json
import logging
import pathlib
import subprocess
import sys
from typing import Any, Dict, List, Optional

from _mcp_protocol import negotiate_protocol_version

# === Force UTF-8 on Windows ==================================================
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stdin, "buffer"):
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

# === Paths ===================================================================
PROJ_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJ_ROOT / "scripts"
PS_DIR = PROJ_ROOT / "Документация" / "Валидация"
LOGS_DIR = PROJ_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# === Logging (NOT stdout — занят MCP) =======================================
logging.basicConfig(
    filename=str(LOGS_DIR / "dev_mcp.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("dev-mcp")

# === Allow imports of sibling scripts =======================================
sys.path.insert(0, str(SCRIPTS_DIR))

SERVER_INFO = {"name": "dev-mcp", "version": "0.1.0"}
CAPABILITIES = {"tools": {}}

# Truncate captured stdout/stderr returned to the agent
MAX_OUTPUT_BYTES = 16_000

# ============================================================================
# Helpers
# ============================================================================


def _truncate(text: str, limit: int = MAX_OUTPUT_BYTES) -> str:
    if len(text) <= limit:
        return text
    half = limit // 2
    return text[:half] + f"\n\n... [TRUNCATED {len(text) - limit} chars] ...\n\n" + text[-half:]


def _run_subprocess(args: List[str], cwd: pathlib.Path = PROJ_ROOT, timeout: int = 600) -> Dict[str, Any]:
    """Запуск процесса с UTF-8 захватом stdout/stderr."""
    try:
        result = subprocess.run(
            args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return {
            "exit_code": result.returncode,
            "stdout": _truncate(result.stdout or ""),
            "stderr": _truncate(result.stderr or ""),
            "ok": result.returncode == 0,
        }
    except subprocess.TimeoutExpired as e:
        return {
            "exit_code": -1,
            "stdout": _truncate(e.stdout or "" if isinstance(e.stdout, str) else ""),
            "stderr": f"TIMEOUT after {timeout}s",
            "ok": False,
            "timeout": True,
        }
    except Exception as e:  # noqa: BLE001
        logger.exception("subprocess failed")
        return {"exit_code": -1, "stdout": "", "stderr": f"{type(e).__name__}: {e}", "ok": False}


def _run_powershell(script_path: pathlib.Path, ps_args: List[str], timeout: int = 600) -> Dict[str, Any]:
    """Запуск .ps1 через -EncodedCommand (UTF-16LE Base64)."""
    if not script_path.exists():
        return {"ok": False, "exit_code": 1, "stdout": "", "stderr": f"Script not found: {script_path}"}

    def quote(arg: str) -> str:
        if arg.startswith("-"):
            return arg
        if " " in arg or any(ord(c) > 127 for c in arg):
            return f"'{arg}'"
        return arg

    args_str = " ".join(quote(a) for a in ps_args)
    ps_command = (
        '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; '
        '[Console]::InputEncoding  = [System.Text.Encoding]::UTF8; '
        '$OutputEncoding = [System.Text.Encoding]::UTF8; '
        f'& "{script_path}" {args_str}; '
        'exit $LASTEXITCODE'
    )
    encoded = base64.b64encode(ps_command.encode("utf-16-le")).decode("ascii")
    return _run_subprocess(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-EncodedCommand", encoded,
        ],
        timeout=timeout,
    )


def _python_exe() -> str:
    venv_py = PROJ_ROOT / ".venv" / "Scripts" / "python.exe"
    return str(venv_py) if venv_py.exists() else sys.executable


def _read_env_credentials() -> Dict[str, str]:
    env_file = PROJ_ROOT / ".env"
    if not env_file.exists():
        return {}
    creds = {}
    for line in env_file.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            creds[k.strip()] = v.strip()
    return creds


def _infobase_path() -> Optional[str]:
    try:
        from _project_config import infobase_path  # type: ignore
        return infobase_path()
    except Exception:
        return None


def _backup_prefix() -> str:
    try:
        from _project_config import get  # type: ignore
        return get("monitoring.backup_prefix", "backup") or "backup"
    except Exception:
        return "backup"


def _bench_enabled() -> bool:
    try:
        from _project_config import get  # type: ignore
        return bool(get("mcp.bench.enabled", False))
    except Exception:
        return False


def _bench_root() -> Optional[str]:
    try:
        from _project_config import get  # type: ignore
        root = (get("mcp.bench.root") or "").strip()
        return root or None
    except Exception:
        return None


def _dt_backup_exists_today() -> bool:
    today = datetime.date.today().strftime("%Y%m%d")
    pattern = PS_DIR / "backups" / f"{_backup_prefix()}-{today}*.dt"
    import glob
    return bool(glob.glob(str(pattern)))


# ============================================================================
# Tool definitions
# ============================================================================

TOOLS: List[Dict[str, Any]] = [
    {
        "name": "dev_status",
        "description": "Health-check: проверяет наличие venv, ИБ, vault Obsidian, "
                       "PS-скриптов, последний бэкап, последний DT-бэкап.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "dev_backup",
        "description": "Локальный бэкап папки Конфигурация/ → _backups/<timestamp>/. "
                       "Без обращения к ИБ. Быстро (~1-3 сек).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "description": {"type": "string", "description": "Короткое описание для info.txt"},
            },
            "required": ["description"],
        },
    },
    {
        "name": "dev_dump",
        "description": "Выгрузка конфигурации из ИБ в Конфигурация/ (DumpConfigToFiles). "
                       "Перезаписывает рабочую копию. Использовать ПЕРЕД ручным анализом или правками.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "dev_validate",
        "description": "Валидация XML-структуры в Конфигурация/ без обращения к ИБ. "
                       "Быстро. Запускать ПЕРЕД dev_deploy.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "dev_deploy",
        "description": "Деплой основной конфигурации: LoadConfigFromFiles + UpdateDBCfg. "
                       "Долго (~100 сек). DT-бэкап создаётся автоматически 1 раз в день.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "skip_check": {
                    "type": "boolean",
                    "default": True,
                    "description": "Пропустить CheckConfig (ускоряет деплой)",
                },
                "force_dt_backup": {
                    "type": "boolean",
                    "default": False,
                    "description": "Принудительно создать DT-бэкап даже если он есть за сегодня",
                },
            },
        },
    },
    {
        "name": "dev_monitor",
        "description": "Проверить журнал регистрации ИБ за последние N минут. "
                       "Возвращает ошибки и предупреждения.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "last_minutes": {"type": "integer", "default": 5, "minimum": 1, "maximum": 1440},
            },
        },
    },
    {
        "name": "dev_ext",
        "description": "Операции с расширением конфигурации: Full (Load+Update), Dump, Load, Update. "
                       "Быстро (~15 сек). Таймаут 30 сек — если дольше, расширение зависло.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Имя расширения (например, PTM_Analytics)"},
                "action": {"type": "string", "enum": ["Full", "Dump", "Load", "Update", "Check"]},
                "dir": {"type": "string", "description": "Опционально: путь к папке расширения"},
            },
            "required": ["name", "action"],
        },
    },
    {
        "name": "dev_sync_obsidian",
        "description": "Синхронизация Конфигурация/ → Obsidian vault (граф знаний). "
                       "Запускать ПОСЛЕ изменений метаданных.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]

_BENCH_TOOL: Dict[str, Any] = {
    "name": "dev_sync_bench",
    "description": "Однонаправленный sync боевой проект → песочница ModelBench. "
                   "Включено только при mcp.bench.enabled: true в project-config.yml. "
                   "Копирует .github/, Конфигурация/, Документация/, scripts/ и др. "
                   "по списку из <bench_root>/bench/sync_manifest.json.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "bench_root": {
                "type": "string",
                "description": "Путь к песочнице (default: mcp.bench.root из project-config.yml)",
            },
            "dry_run": {
                "type": "boolean",
                "default": False,
                "description": "Показать план копирования без записи файлов",
            },
        },
    },
}


def _active_tools() -> List[Dict[str, Any]]:
    tools = list(TOOLS)
    if _bench_enabled() and (PROJ_ROOT / "scripts" / "sync_to_bench.py").exists():
        tools.append(_BENCH_TOOL)
    return tools

# ============================================================================
# Tool handlers
# ============================================================================


def tool_dev_status(_: Dict[str, Any]) -> Dict[str, Any]:
    venv = PROJ_ROOT / ".venv" / "Scripts" / "python.exe"
    vault = None
    try:
        cfg = json.loads((PROJ_ROOT / "config.json").read_text(encoding="utf-8-sig"))
        vault = cfg.get("obsidian_vault_path")
    except Exception:
        pass

    ib = _infobase_path()

    # Last local backup
    backups = sorted([p for p in (PROJ_ROOT / "_backups").glob("20*") if p.is_dir()], reverse=True)
    last_backup = backups[0].name if backups else None

    # Last DT backup
    import glob
    prefix = _backup_prefix()
    dt_files = sorted(glob.glob(str(PS_DIR / "backups" / f"{prefix}-*.dt")), reverse=True)
    last_dt = pathlib.Path(dt_files[0]).name if dt_files else None

    return {
        "ok": True,
        "venv": {"path": str(venv), "exists": venv.exists()},
        "infobase": {"path": ib, "exists": bool(ib and pathlib.Path(ib).exists())},
        "obsidian_vault": {"path": vault, "exists": bool(vault and pathlib.Path(vault).exists())},
        "ps_scripts": {
            "deploy": (PS_DIR / "deploy-config.ps1").exists(),
            "validate": (PS_DIR / "validate-config.ps1").exists(),
            "monitor": (PS_DIR / "monitor-errors.ps1").exists(),
        },
        "last_local_backup": last_backup,
        "last_dt_backup": last_dt,
        "dt_backup_today": _dt_backup_exists_today(),
    }


def tool_dev_backup(args: Dict[str, Any]) -> Dict[str, Any]:
    description = args.get("description", "").strip()
    if not description:
        return {"ok": False, "error": "description is required"}
    try:
        from _local_backup import make_backup  # type: ignore
        path = make_backup(description)
        return {"ok": True, "backup_path": str(path), "stamp": path.name}
    except Exception as e:  # noqa: BLE001
        logger.exception("backup failed")
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def _build_deploy_args(action: str, skip_check: bool, force_dt_backup: bool) -> List[str]:
    extra: List[str] = ["-Action", action]
    ib = _infobase_path()
    if ib:
        extra += ["-BasePath", ib]

    creds = _read_env_credentials()
    user = creds.get("PTM_1C_USER", "")
    password = creds.get("PTM_1C_PASSWORD", "")
    if user:
        extra += ["-User", user]
        if password:
            extra += ["-Password", password]

    if skip_check:
        extra.append("-SkipCheck")

    # DT-бэкап логика
    if action == "Full":
        if not force_dt_backup and _dt_backup_exists_today():
            extra.append("-SkipDtBackup")
    return extra


def tool_dev_dump(_: Dict[str, Any]) -> Dict[str, Any]:
    args = _build_deploy_args("Dump", skip_check=True, force_dt_backup=False)
    res = _run_powershell(PS_DIR / "deploy-config.ps1", args, timeout=600)
    return res


def tool_dev_validate(_: Dict[str, Any]) -> Dict[str, Any]:
    return _run_powershell(PS_DIR / "validate-config.ps1", [], timeout=120)


def tool_dev_deploy(args: Dict[str, Any]) -> Dict[str, Any]:
    skip_check = bool(args.get("skip_check", True))
    force_dt = bool(args.get("force_dt_backup", False))
    ps_args = _build_deploy_args("Full", skip_check=skip_check, force_dt_backup=force_dt)
    return _run_powershell(PS_DIR / "deploy-config.ps1", ps_args, timeout=600)


def tool_dev_monitor(args: Dict[str, Any]) -> Dict[str, Any]:
    minutes = int(args.get("last_minutes", 5))
    ps_args = ["-Action", "Check", "-LastMinutes", str(minutes)]
    return _run_powershell(PS_DIR / "monitor-errors.ps1", ps_args, timeout=120)


def tool_dev_ext(args: Dict[str, Any]) -> Dict[str, Any]:
    name = args.get("name", "").strip()
    action = args.get("action", "").strip()
    if not name or not action:
        return {"ok": False, "error": "name and action are required"}
    cmd = [_python_exe(), str(SCRIPTS_DIR / "deploy_ext.py"), "--ext", name, "--action", action]
    if args.get("dir"):
        cmd += ["--dir", args["dir"]]
    return _run_subprocess(cmd, timeout=60)


def tool_dev_sync_obsidian(_: Dict[str, Any]) -> Dict[str, Any]:
    sync_script = PROJ_ROOT / "sync_1c_obsidian.py"
    if not sync_script.exists():
        return {"ok": False, "error": f"Not found: {sync_script}"}
    return _run_subprocess([_python_exe(), str(sync_script)], timeout=300)


def tool_dev_sync_bench(args: Dict[str, Any]) -> Dict[str, Any]:
    if not _bench_enabled():
        return {
            "ok": False,
            "error": "dev_sync_bench отключён: задай mcp.bench.enabled: true и mcp.bench.root в project-config.yml",
        }
    default_root = _bench_root()
    if not default_root and not args.get("bench_root"):
        return {"ok": False, "error": "mcp.bench.root не задан в project-config.yml"}
    bench_root_str = args.get("bench_root") or default_root
    dry_run = bool(args.get("dry_run", False))
    bench_root = pathlib.Path(bench_root_str)
    try:
        from sync_to_bench import sync_to_bench  # type: ignore
    except ImportError as e:
        return {"ok": False, "error": f"Не удалось импортировать sync_to_bench: {e}"}
    try:
        return sync_to_bench(bench_root, dry_run=dry_run)
    except Exception as e:  # noqa: BLE001
        logger.exception("sync_to_bench failed")
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


TOOL_HANDLERS = {
    "dev_status": tool_dev_status,
    "dev_backup": tool_dev_backup,
    "dev_dump": tool_dev_dump,
    "dev_validate": tool_dev_validate,
    "dev_deploy": tool_dev_deploy,
    "dev_monitor": tool_dev_monitor,
    "dev_ext": tool_dev_ext,
    "dev_sync_obsidian": tool_dev_sync_obsidian,
    "dev_sync_bench": tool_dev_sync_bench,
}


def handle_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    handler = TOOL_HANDLERS.get(name)
    if not handler:
        return {"error": {"code": "UnknownTool", "message": f"Unknown tool: {name}"}}
    try:
        return handler(arguments or {})
    except Exception as e:  # noqa: BLE001
        logger.exception(f"Tool {name} failed")
        return {"error": {"code": "InternalError", "message": f"{type(e).__name__}: {e}"}}


# ============================================================================
# MCP Protocol (JSON-RPC 2.0 via stdio)
# ============================================================================


def make_response(req_id: Any, result: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def make_error(req_id: Any, code: int, message: str) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def handle_request(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    method = request.get("method", "")
    params = request.get("params", {}) or {}
    req_id = request.get("id")

    logger.info(f"Request: {method} (id={req_id})")

    if method == "initialize":
        return make_response(req_id, {
            "protocolVersion": negotiate_protocol_version(params),
            "capabilities": CAPABILITIES,
            "serverInfo": SERVER_INFO,
        })

    if method == "notifications/initialized":
        return None

    if method == "ping":
        return make_response(req_id, {})

    if method == "tools/list":
        return make_response(req_id, {"tools": _active_tools()})

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {}) or {}
        result = handle_tool(tool_name, arguments)
        is_error = isinstance(result, dict) and "error" in result
        content_text = json.dumps(result, ensure_ascii=False, indent=2)
        return make_response(req_id, {
            "content": [{"type": "text", "text": content_text}],
            "isError": is_error,
        })

    if req_id is not None:
        return make_error(req_id, -32601, f"Method not found: {method}")
    return None


def run_stdio() -> None:
    logger.info("dev-mcp server starting (stdio)")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as e:
            resp = make_error(None, -32700, f"Parse error: {e}")
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
            continue
        response = handle_request(request)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_stdio()
