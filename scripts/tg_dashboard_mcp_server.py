# -*- coding: utf-8 -*-
"""
tg-dashboard v2 — гибридный MCP-сервер: Obsidian-файл + agent overlay.

Архитектура:
  Фоновый поток (polling каждые 5 сек):
    - Сканирует папки задач vault (05-Планы, 06-Фичи, 07-Баги) на новые .md → авто-создаёт TG
    - Отслеживает mtime файлов → перечитывает - [ ] / - [x] → обновляет TG

  Два источника состояния:
    * Файл плана (Obsidian) — «- [ ]» = pending, «- [x]» = done (ОСНОВНОЙ)
    * Agent overlay (MCP tools) — in_progress / waiting_input / error / ... (ДОПОЛНИТЕЛЬНЫЙ)

  Composite-рендеринг:
    - Файл говорит done → всегда done (файл побеждает)
    - Агент поставил overlay → показывается поверх pending
    - Расхождение → показывает оба + счётчик ⚠️ в подвале

  Tools для агента (минимальный набор):
    tg_status       — health-check, список активных задач
    tg_start_task   — явный старт (если авто-старт не подошёл)
    tg_update_step  — agent overlay: in_progress / error / blocked / skipped
    tg_wait_input   — overlay waiting_input + текст вопроса
    tg_finish_task  — финализировать задачу (вызывает only closer)

Конфигурация (.env приоритет, fallback — config.json → tg_dashboard):
    TG_BOT_TOKEN=...
    TG_CHAT_ID=...
"""

import datetime
import hashlib
import http.server
import io
import json
import logging
import pathlib
import re
import socketserver
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

# === Force UTF-8 on Windows ==================================================
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stdin, "buffer"):
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

# === Paths ===================================================================
PROJ_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJ_ROOT / "scripts"))
from _mcp_protocol import negotiate_protocol_version
LOGS_DIR = PROJ_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOGS_DIR / "tg_dashboard_mcp.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("tg-dashboard")

SERVER_INFO = {"name": "tg-dashboard", "version": "2.0.0"}
CAPABILITIES = {"tools": {}}

POLL_INTERVAL = 5  # seconds

# === Overlay status icons ===================================================
OVERLAY_ICONS: Dict[str, str] = {
    "in_progress":   "🔄",
    "waiting_input": "⏸",
    "error":         "❌",
    "skipped":       "⏭",
    "blocked":       "🚫",
    "done":          "✅",
}
VALID_OVERLAY_STATUSES = set(OVERLAY_ICONS.keys()) | {"pending"}
VALID_FINAL_STATUSES = {"done", "cancelled", "failed"}

# === Global state store (task_id → state dict) =============================
_store: Dict[str, Dict[str, Any]] = {}
_store_lock = threading.Lock()


# ============================================================================
# Config
# ============================================================================

def _load_env() -> Dict[str, str]:
    env_file = PROJ_ROOT / ".env"
    if not env_file.exists():
        return {}
    result: Dict[str, str] = {}
    for line in env_file.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            result[k.strip()] = v.strip()
    return result


def _load_config() -> Dict[str, Any]:
    cfg_file = PROJ_ROOT / "config.json"
    if not cfg_file.exists():
        return {}
    try:
        return json.loads(cfg_file.read_text(encoding="utf-8-sig"))
    except Exception as e:
        logger.exception("config.json read failed: %s", e)
        return {}


def _tg_creds() -> Tuple[str, str]:
    """Returns (bot_token, chat_id). .env overrides config.json."""
    env = _load_env()
    cfg = _load_config().get("tg_dashboard", {}) or {}
    token = env.get("TG_BOT_TOKEN") or cfg.get("bot_token", "")
    chat_id = env.get("TG_CHAT_ID") or cfg.get("chat_id", "")
    return token.strip(), str(chat_id).strip()


def _vault_path() -> Optional[pathlib.Path]:
    raw = _load_config().get("obsidian_vault_path")
    if not raw:
        return None
    p = pathlib.Path(raw)
    return p if p.exists() else None


_DONE_STATUSES = frozenset({
    "завершена", "закрыта", "отменена", "отменён", "cancelled", "done", "closed", "canceled",
})
_FM_STATUS_RE = re.compile(r'^статус:\s*"?([^"\n]+)"?\s*$', re.MULTILINE)
_DEFAULT_TASK_FOLDERS = ("05-Планы", "06-Фичи", "07-Баги")


def _task_folders() -> List[str]:
    folders = _load_config().get("obsidian_task_folders")
    if folders:
        return list(folders)
    return list(_DEFAULT_TASK_FOLDERS)


def _parse_frontmatter_status(path: pathlib.Path) -> Optional[str]:
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    if not raw.startswith("---"):
        return None
    end = raw.find("---", 3)
    if end < 0:
        return None
    match = _FM_STATUS_RE.search(raw[3:end])
    return match.group(1).strip().lower() if match else None


def _is_active_plan(path: pathlib.Path) -> bool:
    status = _parse_frontmatter_status(path)
    return not status or status not in _DONE_STATUSES


def _iter_active_plans() -> List[pathlib.Path]:
    vault = _vault_path()
    if vault is None:
        return []

    result: List[pathlib.Path] = []
    seen: set[str] = set()
    scan_dirs: List[pathlib.Path] = [vault / folder for folder in _task_folders()]
    legacy = vault / "Dev" / "Tasks" / "Active"
    if legacy.is_dir():
        scan_dirs.append(legacy)

    for folder in scan_dirs:
        if not folder.is_dir():
            continue
        for plan_file in sorted(folder.glob("*.md")):
            key = str(plan_file.resolve())
            if key in seen or not _is_active_plan(plan_file):
                continue
            seen.add(key)
            result.append(plan_file)
    return result


# ============================================================================
# State persistence
# ============================================================================

def _state_dir(plan_path: pathlib.Path) -> pathlib.Path:
    d = plan_path.parent / ".tg_state"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _state_file_path(plan_path: pathlib.Path, task_id: str) -> pathlib.Path:
    return _state_dir(plan_path) / f"{task_id}.json"


def _save_state_locked(state: Dict[str, Any]) -> None:
    """Save state JSON. Must be called with _store_lock held OR safe context."""
    path = pathlib.Path(state["_state_file"])
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    try:
        tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)
    except Exception as e:
        logger.error("save_state failed %s: %s", path, e)


def _find_all_state_files() -> List[pathlib.Path]:
    vault = _vault_path()
    if vault is None:
        return []
    return list(vault.rglob(".tg_state/*.json"))


def _load_persisted_states() -> None:
    """Load existing (non-finished) state files into _store at startup."""
    for f in _find_all_state_files():
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            data["_state_file"] = str(f)
            tid = data.get("task_id")
            if tid and not data.get("final_status"):
                with _store_lock:
                    _store[tid] = data
                logger.info("Loaded persisted state: %s", tid)
        except Exception as e:
            logger.warning("load state failed %s: %s", f, e)


# ============================================================================
# Plan parser
# ============================================================================

_CHECKBOX_RE = re.compile(r"^\s*-\s+\[( |x|X)\]\s+(.*)", re.MULTILINE)
_H1_RE = re.compile(r"^#\s+(.+)", re.MULTILINE)


def _strip_md(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # [label](url) → label
    text = re.sub(r"[*_~`]", "", text)
    return text.strip()


def parse_plan(path: pathlib.Path) -> Dict[str, Any]:
    """Extract title (first H1) and checklist steps from a plan .md file."""
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        logger.warning("parse_plan failed %s: %s", path, e)
        return {"title": path.stem, "steps": []}

    title = path.stem
    m = _H1_RE.search(raw)
    if m:
        title = _strip_md(m.group(1))

    steps: List[Dict[str, Any]] = []
    for match in _CHECKBOX_RE.finditer(raw):
        checked = match.group(1).lower() == "x"
        text = _strip_md(match.group(2))
        if text:
            steps.append({
                "text": text[:120],
                "file_status": "done" if checked else "pending",
            })

    return {"title": title, "steps": steps}


# ============================================================================
# Telegram client
# ============================================================================

class TelegramError(Exception):
    pass


def _tg_request(method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    token, _ = _tg_creds()
    if not token:
        raise TelegramError("bot_token not configured")
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise TelegramError(f"HTTP {e.code}: {body}") from e
    except urllib.error.URLError as e:
        raise TelegramError(f"Network: {e}") from e

    result = json.loads(body)
    if not result.get("ok"):
        raise TelegramError(f"API error: {result}")
    return result.get("result", {})


def _tg_send(text: str, chat_id: str) -> int:
    res = _tg_request("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    })
    return int(res["message_id"])


def _tg_edit(message_id: int, text: str, chat_id: str) -> None:
    try:
        _tg_request("editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        })
    except TelegramError as e:
        if "message is not modified" in str(e).lower():
            return
        raise


# ============================================================================
# Renderer (HTML)
# ============================================================================

def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _now_hhmm() -> str:
    return datetime.datetime.now().strftime("%H:%M")


def _composite(
    file_status: str,
    overlay: Optional[Dict[str, Any]],
) -> Tuple[str, str, bool]:
    """
    Returns (icon, effective_status, is_desync).
    Desync = file and overlay meaningfully contradict each other.
    """
    ov_status = (overlay or {}).get("status")

    if file_status == "done":
        desync = bool(ov_status and ov_status not in ("done", "pending", None))
        return "✅", "done", desync

    # file_status == "pending"
    if not ov_status or ov_status == "pending":
        return "⬜", "pending", False
    if ov_status == "done":
        # Agent says done but file not [x] yet
        return "✅", "done", True
    return OVERLAY_ICONS.get(ov_status, "⬜"), ov_status, False


def render_message(state: Dict[str, Any]) -> str:
    steps: List[Dict[str, Any]] = state.get("steps", [])
    overlays: Dict[str, Any] = state.get("agent_overlays", {})
    final = state.get("final_status")

    lines: List[str] = []

    # Header
    if final:
        head = {"done": "🎉", "cancelled": "🚫", "failed": "💥"}.get(final, "🏁")
        lines.append(f"{head} <b>{_esc(state['task_name'])}</b>  <i>({final})</i>")
    else:
        lines.append(f"🚀 <b>{_esc(state['task_name'])}</b>")

    if state.get("agent"):
        lines.append(f"👤 <code>{_esc(state['agent'])}</code>")

    plan_path = state.get("plan_path", "")
    if plan_path:
        enc = urllib.parse.quote(plan_path, safe="")
        lines.append(f'📋 <a href="obsidian://open?path={enc}">Открыть план</a>')

    if state.get("notes"):
        lines.append(f"📝 <i>{_esc(state['notes'])}</i>")

    lines.append("")

    # Steps
    desync_count = 0
    done_file = 0
    done_ov = 0
    in_prog = 0
    waiting = 0
    err_count = 0

    for i, step in enumerate(steps, start=1):
        overlay = overlays.get(str(i))
        icon, eff, is_desync = _composite(step.get("file_status", "pending"), overlay)

        if is_desync:
            desync_count += 1
        if step.get("file_status") == "done":
            done_file += 1
        if eff == "done" and step.get("file_status") != "done":
            done_ov += 1
        if eff == "in_progress":
            in_prog += 1
        if eff == "waiting_input":
            waiting += 1
        if eff == "error":
            err_count += 1

        text = _esc(step["text"])

        # Interactive suffix from overlay
        suffix = ""
        if overlay:
            if overlay.get("status") == "waiting_input" and overlay.get("question"):
                suffix = f"  ← ❓ <i>{_esc(overlay['question'])}</i>"
            elif overlay.get("note"):
                suffix = f"  <i>({_esc(overlay['note'])})</i>"

        # Desync annotation
        if is_desync:
            if step.get("file_status", "pending") == "pending":
                suffix += "  ⚠️ <i>нет [x]</i>"
            else:
                suffix += f"  ⚠️ <i>агент:{(overlay or {}).get('status','?')}</i>"

        # Line format
        if eff == "done":
            lines.append(f"{icon} <s>{i}. {text}</s>{suffix}")
        elif eff == "in_progress":
            lines.append(f"{icon} <b>{i}. {text}</b>{suffix}")
        else:
            lines.append(f"{icon} {i}. {text}{suffix}")

    # Footer
    total = len(steps)
    lines.append("")

    prog: List[str] = [f"{done_file}/{total} ✅"]
    if done_ov:
        prog.append(f"+{done_ov}✅")
    if in_prog:
        prog.append(f"{in_prog} 🔄")
    if waiting:
        prog.append(f"{waiting} ⏸")
    if err_count:
        prog.append(f"{err_count} ❌")

    src = "🗂" if state.get("_auto_started") else "🤖"
    lines.append(f"⏱ {_now_hhmm()}  {src}  📊 {' · '.join(prog)}")

    if desync_count:
        lines.append(
            f"⚠️ <i>Рассинхронизация {desync_count} шаг(а) "
            f"— файл ↔ агент расходятся</i>"
        )

    if final and state.get("summary"):
        lines.append(f"\n💬 <i>{_esc(state['summary'])}</i>")

    return "\n".join(lines)


def _render_hash(state: Dict[str, Any]) -> str:
    return hashlib.md5(render_message(state).encode()).hexdigest()[:8]


# ============================================================================
# State factory
# ============================================================================

def _make_state(
    task_id: str,
    plan_path: pathlib.Path,
    plan_info: Dict[str, Any],
    agent: str = "",
    notes: str = "",
    auto_started: bool = False,
) -> Dict[str, Any]:
    _, chat_id = _tg_creds()
    sf = _state_file_path(plan_path, task_id)
    return {
        "task_id": task_id,
        "task_name": plan_info["title"],
        "plan_path": str(plan_path),
        "plan_mtime": plan_path.stat().st_mtime if plan_path.exists() else 0.0,
        "agent": agent,
        "notes": notes,
        "steps": plan_info["steps"],
        "agent_overlays": {},
        "message_id": None,
        "chat_id": chat_id,
        "started_iso": datetime.datetime.now().isoformat(timespec="seconds"),
        "started_hhmm": _now_hhmm(),
        "final_status": None,
        "summary": "",
        "last_rendered_hash": "",
        "last_agent_ts": None,  # timestamp of last agent MCP call (for health indicator)
        "_auto_started": auto_started,
        "_state_file": str(sf),
    }


# ============================================================================
# TG push with hash-based dedup
# ============================================================================

def _push_to_tg(state: Dict[str, Any]) -> None:
    """Re-render, skip if unchanged, edit/send TG. Call with _store_lock held."""
    new_hash = _render_hash(state)
    if new_hash == state.get("last_rendered_hash"):
        return

    text = render_message(state)
    chat_id = state.get("chat_id") or _tg_creds()[1]
    msg_id = state.get("message_id")

    try:
        if msg_id:
            _tg_edit(int(msg_id), text, chat_id)
        else:
            mid = _tg_send(text, chat_id)
            state["message_id"] = mid
        state["last_rendered_hash"] = new_hash
    except TelegramError as e:
        logger.error("TG push [%s]: %s", state["task_id"], e)

    _save_state_locked(state)


# ============================================================================
# Background polling thread
# ============================================================================

def _task_id_from_file(path: pathlib.Path) -> str:
    vault = _vault_path()
    if vault:
        try:
            rel = path.relative_to(vault)
            return str(rel.with_suffix("")).replace("\\", "/").replace("/", "__")
        except ValueError:
            pass
    return path.stem


def _merge_steps(
    old: List[Dict[str, Any]],
    new: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    if len(old) != len(new):
        return new
    return [
        {"text": new[i]["text"] or old[i]["text"], "file_status": new[i]["file_status"]}
        for i in range(len(new))
    ]


def _poll_once() -> None:
    token, chat_id = _tg_creds()
    if not token or not chat_id:
        return

    active_plans = _iter_active_plans()
    if not active_plans:
        return

    # 1. Discover new plan files
    for plan_file in active_plans:
        task_id = _task_id_from_file(plan_file)
        with _store_lock:
            if task_id in _store:
                continue

        plan_info = parse_plan(plan_file)
        if not plan_info["steps"]:
            continue  # checklist not written yet

        # Check if another process already created a state file for this task
        sf = _state_file_path(plan_file, task_id)
        if sf.exists():
            try:
                persisted = json.loads(sf.read_text(encoding="utf-8"))
                if persisted.get("message_id"):
                    # Another process already sent the TG message — load it
                    persisted["_state_file"] = str(sf)
                    with _store_lock:
                        if task_id not in _store:
                            _store[task_id] = persisted
                    continue
            except Exception:
                pass  # corrupted state file — proceed with fresh create

        state = _make_state(task_id, plan_file, plan_info, auto_started=True)
        with _store_lock:
            if task_id not in _store:
                _store[task_id] = state
                _push_to_tg(state)
                logger.info("Auto-started: %s (%d steps)", task_id, len(plan_info["steps"]))

    # 2. Check for file changes in tracked tasks
    with _store_lock:
        snapshot = [(tid, s["plan_path"], s.get("plan_mtime", 0), s.get("final_status"))
                    for tid, s in _store.items()]

    for task_id, plan_path_str, prev_mtime, final in snapshot:
        if final:
            continue
        plan_path = pathlib.Path(plan_path_str)
        if not plan_path.exists():
            continue
        try:
            cur_mtime = plan_path.stat().st_mtime
        except OSError:
            continue
        if cur_mtime <= prev_mtime:
            continue

        # File changed — re-parse and update TG
        plan_info = parse_plan(plan_path)
        with _store_lock:
            s = _store.get(task_id)
            if not s:
                continue
            s["steps"] = _merge_steps(s.get("steps", []), plan_info["steps"])
            s["plan_mtime"] = cur_mtime
            if plan_info["title"] and plan_info["title"] != s.get("task_name"):
                s["task_name"] = plan_info["title"]
            s["last_rendered_hash"] = ""  # force re-render (time changed anyway)
            _push_to_tg(s)
        logger.info("File update → TG: %s", task_id)


def _poll_loop() -> None:
    logger.info("Poller started (interval=%ds)", POLL_INTERVAL)
    while True:
        try:
            _poll_once()
        except Exception as e:
            logger.exception("Poll error: %s", e)
        time.sleep(POLL_INTERVAL)


# ============================================================================
# Tool definitions
# ============================================================================

TOOLS: List[Dict[str, Any]] = [
    {
        "name": "tg_status",
        "description": (
            "Health-check: настроен ли бот, активные задачи, task_id для overlay-вызовов."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "tg_start_task",
        "description": (
            "Явный старт задачи. Если watcher уже создал задачу по этому файлу — обновит "
            "agent/notes. Вызывать только если авто-старт не подошёл."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "plan_path": {
                    "type": "string",
                    "description": "Абсолютный путь к .md файлу плана в vault.",
                },
                "task_name": {
                    "type": "string",
                    "description": "Переопределить заголовок (иначе берётся из H1). Опц.",
                },
                "agent": {"type": "string"},
                "notes": {"type": "string"},
            },
            "required": ["plan_path"],
        },
    },
    {
        "name": "tg_update_step",
        "description": (
            "Agent overlay для шага — интерактивная информация поверх состояния файла. "
            "Использовать для: in_progress, error, blocked, skipped. "
            "НЕ заменяет [x] в файле — файл остаётся источником истины."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "index": {"type": "integer", "minimum": 1},
                "status": {
                    "type": "string",
                    "enum": ["in_progress", "done", "error", "skipped", "blocked", "pending"],
                },
                "note": {"type": "string"},
            },
            "required": ["task_id", "index", "status"],
        },
    },
    {
        "name": "tg_wait_input",
        "description": (
            "Пометить шаг как «жду ответа» (⏸) с текстом вопроса. "
            "Вызывать ПЕРЕД vscode_askQuestions."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "index": {"type": "integer", "minimum": 1},
                "question": {"type": "string"},
            },
            "required": ["task_id", "index", "question"],
        },
    },
    {
        "name": "tg_finish_task",
        "description": "Финализировать задачу. Вызывает только closer.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "status": {"type": "string", "enum": ["done", "cancelled", "failed"]},
                "summary": {"type": "string"},
            },
            "required": ["task_id", "status"],
        },
    },
]


# ============================================================================
# Tool handlers
# ============================================================================

def tool_tg_status(_: Dict[str, Any]) -> Dict[str, Any]:
    token, chat_id = _tg_creds()
    vault = _vault_path()
    active_plans = _iter_active_plans()

    with _store_lock:
        tasks = [
            {
                "task_id": s["task_id"],
                "task_name": s["task_name"],
                "agent": s.get("agent", ""),
                "steps_total": len(s.get("steps", [])),
                "steps_done_file": sum(
                    1 for st in s.get("steps", []) if st.get("file_status") == "done"
                ),
                "started": s.get("started_hhmm"),
                "auto_started": s.get("_auto_started", False),
            }
            for s in _store.values()
            if not s.get("final_status")
        ]

    return {
        "ok": bool(token and chat_id),
        "bot_token_configured": bool(token),
        "chat_id_configured": bool(chat_id),
        "vault": str(vault) if vault else None,
        "task_folders": _task_folders(),
        "active_plans_found": len(active_plans),
        "poll_interval_sec": POLL_INTERVAL,
        "local_dashboard": f"http://127.0.0.1:{_http_port}/" if _http_port else None,
        "active_tasks": tasks,
        "active_count": len(tasks),
    }


def tool_tg_start_task(args: Dict[str, Any]) -> Dict[str, Any]:
    plan_path_raw = (args.get("plan_path") or "").strip()
    if not plan_path_raw:
        return {"ok": False, "error": "plan_path is required"}

    plan_path = pathlib.Path(plan_path_raw)
    if not plan_path.is_absolute():
        vault = _vault_path()
        if vault:
            plan_path = vault / plan_path_raw
    if not plan_path.exists():
        return {"ok": False, "error": f"plan file not found: {plan_path}"}

    task_id = _task_id_from_file(plan_path)
    plan_info = parse_plan(plan_path)

    override_name = (args.get("task_name") or "").strip()
    if override_name:
        plan_info["title"] = override_name

    agent = (args.get("agent") or "").strip()
    notes = (args.get("notes") or "").strip()

    with _store_lock:
        existing = _store.get(task_id)
        if existing and not existing.get("final_status"):
            existing["agent"] = agent or existing.get("agent", "")
            existing["notes"] = notes or existing.get("notes", "")
            existing["last_rendered_hash"] = ""
            _push_to_tg(existing)
            return {
                "ok": True,
                "task_id": task_id,
                "message_id": existing.get("message_id"),
                "action": "updated",
            }

        state = _make_state(task_id, plan_path, plan_info, agent=agent, notes=notes)
        _store[task_id] = state
        _push_to_tg(state)
        return {
            "ok": True,
            "task_id": task_id,
            "message_id": state.get("message_id"),
            "steps_count": len(plan_info["steps"]),
            "action": "created",
        }


def tool_tg_update_step(args: Dict[str, Any]) -> Dict[str, Any]:
    task_id = (args.get("task_id") or "").strip()
    index = args.get("index")
    status = (args.get("status") or "").strip()
    note = (args.get("note") or "").strip()

    if not task_id:
        return {"ok": False, "error": "task_id is required"}
    if not isinstance(index, int) or index < 1:
        return {"ok": False, "error": "index must be integer >= 1"}
    if status not in VALID_OVERLAY_STATUSES:
        return {"ok": False, "error": f"status must be one of {sorted(VALID_OVERLAY_STATUSES)}"}

    with _store_lock:
        s = _store.get(task_id)
        if not s:
            return {"ok": False, "error": f"task_id not found: {task_id}"}
        if s.get("final_status"):
            return {"ok": False, "error": f"task finished ({s['final_status']})"}
        if index > len(s.get("steps", [])):
            return {"ok": False, "error": f"index {index} out of range ({len(s['steps'])} steps)"}

        s["last_agent_ts"] = time.time()
        if status == "pending":
            s["agent_overlays"].pop(str(index), None)
        else:
            s["agent_overlays"][str(index)] = {"status": status, "note": note, "question": ""}
        _push_to_tg(s)

    return {"ok": True, "task_id": task_id, "index": index, "status": status}


def tool_tg_wait_input(args: Dict[str, Any]) -> Dict[str, Any]:
    task_id = (args.get("task_id") or "").strip()
    index = args.get("index")
    question = (args.get("question") or "").strip()

    if not task_id:
        return {"ok": False, "error": "task_id is required"}
    if not isinstance(index, int) or index < 1:
        return {"ok": False, "error": "index must be integer >= 1"}
    if not question:
        return {"ok": False, "error": "question is required"}

    with _store_lock:
        s = _store.get(task_id)
        if not s:
            return {"ok": False, "error": f"task_id not found: {task_id}"}
        if s.get("final_status"):
            return {"ok": False, "error": f"task finished ({s['final_status']})"}
        if index > len(s.get("steps", [])):
            return {"ok": False, "error": f"index {index} out of range"}
        s["last_agent_ts"] = time.time()
        s["agent_overlays"][str(index)] = {
            "status": "waiting_input",
            "note": "",
            "question": question,
        }
        _push_to_tg(s)

    return {"ok": True, "task_id": task_id, "index": index}


def tool_tg_finish_task(args: Dict[str, Any]) -> Dict[str, Any]:
    task_id = (args.get("task_id") or "").strip()
    status = (args.get("status") or "").strip()
    summary = (args.get("summary") or "").strip()

    if not task_id:
        return {"ok": False, "error": "task_id is required"}
    if status not in VALID_FINAL_STATUSES:
        return {"ok": False, "error": f"status must be one of {sorted(VALID_FINAL_STATUSES)}"}

    with _store_lock:
        s = _store.get(task_id)
        if not s:
            return {"ok": False, "error": f"task_id not found: {task_id}"}
        if s.get("final_status"):
            return {"ok": False, "error": f"already finished ({s['final_status']})"}
        s["final_status"] = status
        s["summary"] = summary
        s["finished_iso"] = datetime.datetime.now().isoformat(timespec="seconds")
        s["last_rendered_hash"] = ""  # force final render
        _push_to_tg(s)

    return {"ok": True, "task_id": task_id, "final_status": status}


TOOL_HANDLERS: Dict[str, Any] = {
    "tg_status":      tool_tg_status,
    "tg_start_task":  tool_tg_start_task,
    "tg_update_step": tool_tg_update_step,
    "tg_wait_input":  tool_tg_wait_input,
    "tg_finish_task": tool_tg_finish_task,
}


def handle_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    handler = TOOL_HANDLERS.get(name)
    if not handler:
        return {"error": {"code": "UnknownTool", "message": f"Unknown tool: {name}"}}
    try:
        return handler(arguments or {})
    except Exception as e:
        logger.exception("Tool %s failed", name)
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
        return make_response(req_id, {"tools": TOOLS})
    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {}) or {}
        result = handle_tool(tool_name, arguments)
        is_error = isinstance(result, dict) and "error" in result
        return make_response(req_id, {
            "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
            "isError": is_error,
        })
    if req_id is not None:
        return make_error(req_id, -32601, f"Method not found: {method}")
    return None


# ============================================================================
# Local HTTP dashboard (localhost web UI)
# ============================================================================

_http_port: int = 0  # actual port after bind, 0 = not running

_DASHBOARD_HTML = """\
<!DOCTYPE html><html lang="ru"><head>
<meta charset="UTF-8">
<title>TG Dashboard</title>
<style>
*{box-sizing:border-box}
body{background:#0d1117;color:#c9d1d9;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",monospace;margin:0;padding:12px 16px}
h1{color:#58a6ff;margin:0 0 4px;font-size:1.2em}
.subtitle{color:#484f58;font-size:.78em;margin-bottom:14px}
/* Card */
.card{background:#161b22;border:1px solid #30363d;border-radius:10px;margin-bottom:8px;overflow:hidden;transition:border-color .2s}
.card:hover{border-color:#58a6ff44}
.card.final-done{border-color:#238636;opacity:.7}
.card.final-failed{border-color:#da3633;opacity:.7}
.card.final-cancelled{border-color:#6e7681;opacity:.6}
/* State colors */
.card.state-active{border-color:#1f6feb;background:#0d1f38}
.card.state-started{border-color:#9e6a03;background:#1c1700}
/* Group headers */
.group-label{font-size:.72em;font-weight:700;text-transform:uppercase;letter-spacing:.08em;padding:6px 4px 4px;margin-top:10px;border-bottom:1px solid #21262d;margin-bottom:6px}
.group-active .group-label{color:#58a6ff}
.group-started .group-label{color:#d29922}
.group-pending .group-label{color:#484f58}
/* Card header — always visible, clickable */
.card-header{display:flex;align-items:center;gap:10px;padding:10px 14px;cursor:pointer;user-select:none}
.card-header:hover{background:#1c2128}
.card-chevron{color:#484f58;font-size:.9em;transition:transform .2s;flex-shrink:0}
.card.open .card-chevron{transform:rotate(90deg)}
.card-title{font-weight:600;font-size:.95em;color:#c9d1d9;flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.card.final-done .card-title{color:#3fb950}
.card.final-failed .card-title{color:#f85149}
.badge{font-size:.72em;padding:2px 7px;border-radius:10px;font-weight:600;white-space:nowrap;flex-shrink:0}
.badge-wait{background:#3d1f6b;color:#d2a8ff}
.badge-inprog{background:#0c2d6b;color:#79c0ff}
.badge-err{background:#4d0f0c;color:#f85149}
.badge-done{background:#0d2d18;color:#3fb950}
.badge-pct{background:#21262d;color:#8b949e}
/* Progress bar */
.pbar-wrap{height:3px;background:#21262d;flex-shrink:0;width:60px;border-radius:2px}
.pbar{height:3px;background:#238636;border-radius:2px;transition:width .4s}
/* Card body — hidden by default */
.card-body{display:none;padding:0 14px 12px;border-top:1px solid #21262d}
.card.open .card-body{display:block}
.meta{font-size:.78em;color:#484f58;margin:8px 0 6px;display:flex;gap:12px;flex-wrap:wrap}
.health-ok{color:#3fb950} .health-warn{color:#d29922} .health-dead{color:#f85149}
/* Steps */
.steps{display:flex;flex-direction:column;gap:1px}
.step{padding:3px 0;font-size:.85em;display:flex;align-items:flex-start;gap:6px}
.step-icon{flex-shrink:0;width:1.2em;text-align:center}
.step-text{flex:1}
.step-done .step-text{color:#484f58;text-decoration:line-through}
.step-inprog .step-text{color:#79c0ff;font-weight:600}
.step-wait{background:#1a1035;border-left:2px solid #8b5cf6;padding:4px 8px 4px 10px;border-radius:4px;margin:2px 0}
.step-err .step-text{color:#f85149}
.step-skip .step-text{color:#484f58;text-decoration:line-through}
.note{color:#6e7681;font-size:.82em;margin-left:4px}
.q-text{color:#a371f7;font-size:.82em;margin-left:4px;font-style:italic}
.desync{color:#d29922;font-size:.75em;margin-left:4px}
/* Current step highlight */
.cur-step{color:#8b949e;font-size:.78em;margin-top:6px;border-top:1px solid #21262d;padding-top:6px}
.summary-line{color:#e3b341;font-size:.82em;margin-top:8px}
footer{color:#333;font-size:.72em;margin-top:16px;display:flex;justify-content:space-between}
#tick{color:#58a6ff}
</style></head><body>
<h1>&#128338; TG Dashboard v2</h1>
<div class="subtitle">Авто-обновление каждые 5 сек &nbsp;|&nbsp; <a href="/api/state" style="color:#333">JSON</a></div>
<div id="tasks"><div style="color:#484f58">Загрузка...</div></div>
<footer><span id="ts"></span><span id="tick"></span></footer>
<script>
const ICONS={pending:"&#9633;",in_progress:"&#128260;",done:"&#9989;",waiting_input:"&#9208;&#65039;",
             error:"&#10060;",skipped:"&#9197;&#65039;",blocked:"&#128683;"};
// Track which cards are open (by task_id)
const openCards=new Set();
function esc(t){if(!t)return"";return String(t).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
function health(ts){
  if(!ts)return'<span class="health-warn">&#128993; нет данных</span>';
  const min=(Date.now()/1000-ts)/60;
  if(min<5)return'<span class="health-ok">&#128994; активен</span>';
  if(min<15)return'<span class="health-warn">&#128993; '+Math.floor(min)+'м</span>';
  return'<span class="health-dead">&#128308; '+Math.floor(min)+'м без ответа</span>';
}
function renderTask(s,stateClass){
  const steps=s.steps||[];
  const ovs=s.agent_overlays||{};
  const done=steps.filter(x=>(x.file_status||"pending")==="done").length;
  const total=steps.length;
  const pct=total?Math.round(done/total*100):0;
  let curStepText="";
  let mainBadge="";
  const waitOvs=Object.values(ovs).filter(o=>o.status==="waiting_input");
  const inprogOvs=Object.entries(ovs).filter(([,o])=>o.status==="in_progress");
  const errOvs=Object.values(ovs).filter(o=>o.status==="error");
  if(s.final_status){
    const fi={done:"&#127881;",cancelled:"&#128683;",failed:"&#128165;"}[s.final_status]||"&#127984;";
    mainBadge=`<span class="badge badge-done">${fi} ${s.final_status}</span>`;
  } else if(waitOvs.length){
    mainBadge='<span class="badge badge-wait">&#9208;&#65039; ждёт</span>';
    curStepText=waitOvs[0].question||"";
  } else if(errOvs.length){
    mainBadge='<span class="badge badge-err">&#10060; ошибка</span>';
  } else if(inprogOvs.length){
    const idx=inprogOvs[0][0];
    const st=steps[parseInt(idx)-1];
    mainBadge='<span class="badge badge-inprog">&#128260; в работе</span>';
    curStepText=st?st.text:"";
  } else {
    mainBadge=`<span class="badge badge-pct">${pct}%</span>`;
  }
  const isOpen=openCards.has(s.task_id);
  let cardCls="card";
  if(stateClass) cardCls+=" "+stateClass;
  if(s.final_status) cardCls+=" final-"+s.final_status;
  if(isOpen) cardCls+=" open";
  const pbarHtml=`<div class="pbar-wrap"><div class="pbar" style="width:${pct}%"></div></div>`;
  let html=`<div class="${cardCls}" data-id="${esc(s.task_id)}">`;
  html+=`<div class="card-header" onclick="toggle('${esc(s.task_id)}')">`;
  html+=`<span class="card-chevron">&#9654;</span>`;
  html+=`<span class="card-title">${esc(s.task_name||s.task_id)}</span>`;
  html+=pbarHtml;
  html+=`<span style="color:#484f58;font-size:.78em;white-space:nowrap">${done}/${total}</span>`;
  html+=mainBadge;
  html+='</div>';
  html+='<div class="card-body">';
  html+=`<div class="meta"><span>&#128100; ${esc(s.agent||"агент не указан")}</span><span>${health(s.last_agent_ts)}</span><span>&#9201; ${esc(s.started_hhmm||"")}</span></div>`;
  if(curStepText) html+=`<div class="cur-step">&#128073; ${esc(curStepText)}</div>`;
  html+='<div class="steps">';
  steps.forEach((step,i)=>{
    const ov=ovs[String(i+1)];
    const fs=step.file_status||"pending";
    const eff=fs==="done"?"done":(ov?ov.status:"pending");
    const icon=ICONS[eff]||"&#9633;";
    let cls="step";
    if(eff==="done")cls+=" step-done";
    else if(eff==="in_progress")cls+=" step-inprog";
    else if(eff==="waiting_input")cls+=" step-wait";
    else if(eff==="error")cls+=" step-err";
    else if(eff==="skipped")cls+=" step-skip";
    let extra="";
    if(ov&&ov.status==="waiting_input"&&ov.question)extra+=`<span class="q-text">&#10067; ${esc(ov.question)}</span>`;
    else if(ov&&ov.note)extra+=`<span class="note">(${esc(ov.note)})</span>`;
    const desync=(fs==="done"&&ov&&ov.status!=="done"&&ov.status!=="pending")||(fs==="pending"&&ov&&ov.status==="done");
    if(desync)extra+=`<span class="desync">&#9888;</span>`;
    html+=`<div class="${cls}"><span class="step-icon">${icon}</span><span class="step-text">${i+1}. ${esc(step.text)}${extra}</span></div>`;
  });
  html+='</div>';
  if(s.summary) html+=`<div class="summary-line">&#128172; ${esc(s.summary)}</div>`;
  html+='</div></div>';
  return html;
}
function getTaskState(s){
  const ovs=Object.values(s.agent_overlays||{});
  if(ovs.some(o=>["in_progress","waiting_input","error"].includes(o.status))) return "active";
  const done=(s.steps||[]).filter(x=>(x.file_status||"pending")==="done").length;
  if(done>0) return "started";
  return "pending";
}
function renderGroup(label,tasks,cls,icon){
  if(!tasks.length) return "";
  let html=`<div class="group-${cls}"><div class="group-label">${icon} ${label} (${tasks.length})</div>`;
  const sc=cls==="active"?"state-active":cls==="started"?"state-started":"";
  tasks.forEach(s=>{ html+=renderTask(s,sc); });
  html+='</div>';
  return html;
}
function toggle(id){
  if(openCards.has(id))openCards.delete(id);else openCards.add(id);
  const el=document.querySelector(`.card[data-id="${id}"]`);
  if(el){el.classList.toggle("open");}
}
let _lastData=null;
function refresh(){
  fetch('/api/state').then(r=>r.json()).then(data=>{
    _lastData=data;
    const el=document.getElementById('tasks');
    if(!data.tasks||!data.tasks.length){el.innerHTML='<div style="color:#484f58">Нет активных задач</div>';return;}
    document.querySelectorAll('.card.open').forEach(c=>openCards.add(c.dataset.id));
    const live=data.tasks.filter(s=>!s.final_status);
    const finals=data.tasks.filter(s=>s.final_status);
    const active=live.filter(s=>getTaskState(s)==="active");
    const started=live.filter(s=>getTaskState(s)==="started");
    const pending=live.filter(s=>getTaskState(s)==="pending");
    let html="";
    html+=renderGroup("Активные",active,"active","&#128994;");
    html+=renderGroup("Начатые",started,"started","&#128993;");
    html+=renderGroup("Не начаты",pending,"pending","&#9711;");
    if(finals.length) html+=renderGroup("Завершённые",finals,"pending","&#127881;");
    el.innerHTML=html;
    document.getElementById('ts').textContent='Обновлено: '+new Date().toLocaleTimeString('ru');
  }).catch(()=>{});
}
let dot=0;
setInterval(()=>{document.getElementById('tick').textContent=['·','··','···','··','·'][dot%5];dot++;},1000);
refresh();setInterval(refresh,5000);
</script></body></html>
"""


class _DashboardHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:  # silence default access log
        pass

    def do_GET(self) -> None:
        if self.path in ("/", "/dashboard"):
            body = _DASHBOARD_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/state":
            now = time.time()
            with _store_lock:
                tasks = [
                    {
                        "task_id": s["task_id"],
                        "task_name": s["task_name"],
                        "agent": s.get("agent", ""),
                        "steps": s.get("steps", []),
                        "agent_overlays": s.get("agent_overlays", {}),
                        "started_hhmm": s.get("started_hhmm", ""),
                        "final_status": s.get("final_status"),
                        "summary": s.get("summary", ""),
                        "last_agent_ts": s.get("last_agent_ts"),
                    }
                    for s in _store.values()
                ]
            body = json.dumps(
                {"tasks": tasks, "server_time": now, "count": len(tasks)},
                ensure_ascii=False,
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)


def _start_http_server(start_port: int = 4567) -> int:
    """Start dashboard HTTP server. Returns actual port (0 on failure)."""
    global _http_port
    for port in range(start_port, start_port + 10):
        try:
            server = socketserver.TCPServer(("127.0.0.1", port), _DashboardHandler)
            server.allow_reuse_address = True
            t = threading.Thread(
                target=server.serve_forever, daemon=True, name=f"tg-http-{port}"
            )
            t.start()
            _http_port = port
            logger.info("Dashboard: http://127.0.0.1:%d/", port)
            return port
        except OSError:
            continue
    logger.warning("Could not bind HTTP dashboard on ports %d-%d", start_port, start_port + 9)
    return 0


def run_stdio() -> None:
    _load_persisted_states()

    t = threading.Thread(target=_poll_loop, daemon=True, name="tg-poller")
    t.start()

    # Start local web dashboard
    cfg = _load_config().get("tg_dashboard", {}) or {}
    http_port = int(cfg.get("local_port", 4567))
    actual_port = _start_http_server(http_port)
    if actual_port:
        logger.info("tg-dashboard v2 started (poller + HTTP :%d)", actual_port)
    else:
        logger.info("tg-dashboard v2 started (poller only, no HTTP)")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as e:
            sys.stdout.write(json.dumps(make_error(None, -32700, f"Parse error: {e}")) + "\n")
            sys.stdout.flush()
            continue
        response = handle_request(request)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_stdio()
