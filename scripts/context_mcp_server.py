# -*- coding: utf-8 -*-
"""
context-mcp — MCP-сервер для системы разведки контекста (`scripts/get_context.py`).

ИТЕРАЦИЯ 3: pipeline-tools (context_resolve / context_get / context_moc)
            подключены к ядру get_context.py. Остальные tools — скелет.
См. Документация/Спецификации/context-mcp-server.md.

Протокол: JSON-RPC 2.0 через stdin/stdout (MCP stdio transport).
Запуск: python scripts/context_mcp_server.py
"""

import io
import json
import logging
import pathlib
import sys
from typing import Any, Dict, List, Optional

# === Force UTF-8 on Windows ==================================================
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stdin, "buffer"):
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

# === Logging (NOT stdout — occupied by MCP) ==================================
log_path = pathlib.Path(__file__).parent.parent / "logs" / "context_mcp.log"
log_path.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(log_path),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("context-mcp")

# === Core integration ========================================================
# Импорт ядра get_context.py — те же функции, что использует CLI.
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _mcp_protocol import negotiate_protocol_version
try:
    import get_context as core  # type: ignore
    CORE_LOADED = True
    CORE_LOAD_ERROR: Optional[str] = None
except Exception as e:  # noqa: BLE001
    core = None  # type: ignore
    CORE_LOADED = False
    CORE_LOAD_ERROR = f"{type(e).__name__}: {e}"
    logger.exception("Failed to import get_context core")

# ============================================================================
# Constants
# ============================================================================

SERVER_INFO = {
    "name": "context-mcp",
    "version": "0.4.0-session",
}

# === Session storage =========================================================
WORKSPACE_ROOT = pathlib.Path(__file__).parent.parent
SESSIONS_DIR = WORKSPACE_ROOT / "Тесты" / "ContextSandbox" / "sessions"
ACTIVE_SESSION_FILE = WORKSPACE_ROOT / "Тесты" / "ContextSandbox" / ".active_session"


def _read_active_session() -> Optional[pathlib.Path]:
    if not ACTIVE_SESSION_FILE.exists():
        return None
    txt = ACTIVE_SESSION_FILE.read_text(encoding="utf-8").strip()
    if not txt:
        return None
    p = pathlib.Path(txt)
    if not p.is_absolute():
        p = WORKSPACE_ROOT / p
    return p if p.exists() else None


def _write_active_session(path: Optional[pathlib.Path]) -> None:
    ACTIVE_SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    if path is None:
        if ACTIVE_SESSION_FILE.exists():
            ACTIVE_SESSION_FILE.unlink()
        return
    rel = path.relative_to(WORKSPACE_ROOT) if path.is_absolute() and str(path).startswith(str(WORKSPACE_ROOT)) else path
    ACTIVE_SESSION_FILE.write_text(str(rel).replace("\\", "/"), encoding="utf-8")


def _count_tasks(session_path: pathlib.Path) -> int:
    txt = session_path.read_text(encoding="utf-8")
    import re
    return len(re.findall(r"^## Task \d+", txt, flags=re.MULTILINE))


def _next_step_no(session_path: pathlib.Path) -> int:
    """Count STEP entries in the current (last) task block. Returns next index."""
    import re
    txt = session_path.read_text(encoding="utf-8")
    # split by '## Task ' and take the last block
    parts = re.split(r"^## Task \d+", txt, flags=re.MULTILINE)
    last = parts[-1] if parts else txt
    return len(re.findall(r"^#### \[.*?\] STEP ", last, flags=re.MULTILINE)) + 1


def _append_to_session(session_path: pathlib.Path, markdown: str) -> None:
    with session_path.open("a", encoding="utf-8", newline="") as f:
        if not markdown.startswith("\n"):
            f.write("\n")
        f.write(markdown)
        if not markdown.endswith("\n"):
            f.write("\n")

CAPABILITIES = {
    "tools": {},
}

TASK_TYPES = [
    "bugfix", "posting", "form-change", "attribute-change",
    "common-module-change", "review", "report", "query", "integration",
]

DEPTH_VALUES = ["auto", "shallow", "medium", "deep"]

METADATA_TYPES = [
    "Documents", "Catalogs", "DataProcessors", "CommonModules", "Reports",
    "InformationRegisters", "AccumulationRegisters", "Enums", "HTTPServices",
    "Constants", "Subsystems", "Roles", "DocumentJournals", "BusinessProcesses",
    "Tasks", "CommonPictures", "CommonTemplates", "Languages", "Styles",
]

RESULT_VALUES = ["perfect", "enough", "excessive", "insufficient", "wrong"]

APPEND_KINDS = [
    "task_header", "recon_step", "delivered", "coverage",
    "excess", "missing", "decision", "free_markdown",
]

# ============================================================================
# Tool definitions (JSON Schema for tools/list)
# ============================================================================

TOOLS: List[Dict[str, Any]] = [
    # ── pipeline ────────────────────────────────────────────────────────────
    {
        "name": "context_resolve",
        "description": "Резолвит свободную строку запроса в кандидатов метаданных 1С. "
                       "Возвращает status + список кандидатов с object_id и score.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Свободная формулировка задачи или название объекта"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "context_get",
        "description": "Собирает контекст под выбранного кандидата. Указывайте либо select (object_id), "
                       "либо candidate (номер из context_resolve).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "task": {"type": "string", "enum": TASK_TYPES},
                "select": {"type": "string", "description": "Точный object_id (приоритет над candidate)"},
                "candidate": {"type": "integer", "description": "Номер кандидата из context_resolve"},
                "depth": {"type": "string", "enum": DEPTH_VALUES, "default": "auto"},
                "stage": {"type": "string", "description": "Явный stage из STAGE_CATALOG"},
                "budget_tokens": {"type": "integer", "description": "Override бюджета токенов"},
            },
            "required": ["query", "task"],
        },
    },
    {
        "name": "context_moc",
        "description": "Список объектов метаданных одного типа с фильтром. "
                       "Используется когда context_resolve вернул ambiguous/not_found.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": METADATA_TYPES},
                "filter": {"type": "string", "description": "Подстрока для фильтрации имён"},
            },
            "required": ["type"],
        },
    },
    # ── feedback ────────────────────────────────────────────────────────────
    {
        "name": "context_feedback",
        "description": "Запись обратной связи по context_id (использовалось ли, что лишнее, чего не хватило).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "context_id": {"type": "string"},
                "result": {"type": "string", "enum": RESULT_VALUES},
                "rating": {"type": "integer", "minimum": 1, "maximum": 5},
                "sections": {
                    "type": "object",
                    "description": "Map: section_name -> 'used'|'partial'|'unused'",
                    "additionalProperties": {"type": "string", "enum": ["used", "partial", "unused"]},
                },
                "extras": {
                    "type": "object",
                    "properties": {
                        "files_read": {"type": "integer"},
                        "searches": {"type": "integer"},
                        "mcp_calls": {"type": "integer"},
                    },
                },
                "missing": {"type": "string"},
                "excess": {"type": "string"},
                "notes": {"type": "string"},
            },
            "required": ["context_id", "result", "rating"],
        },
    },
    # ── analytics ───────────────────────────────────────────────────────────
    {
        "name": "context_stages",
        "description": "Текущий каталог stages из STAGE_CATALOG + статистика проблемных stages.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "context_report",
        "description": "Агрегаты по feedback: problem_stages, trim_candidates, wrong_resolves, общая статистика.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    # ── session (для context-tester) ───────────────────────────────────────
    {
        "name": "context_session_start",
        "description": "Открыть новую аудит-сессию: создать "
                       "Тесты/ContextSandbox/sessions/<YYYY-MM-DD_HHMM>__session.md "
                       "и пометить активной.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Опциональное название сессии"},
            },
        },
    },
    {
        "name": "context_session_append",
        "description": "Дописать структурированный блок в активную сессию (kind задаёт шаблон форматирования).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "kind": {"type": "string", "enum": APPEND_KINDS},
                "payload": {"type": "object", "description": "Структура соответствует kind, см. спецификацию §4"},
            },
            "required": ["kind", "payload"],
        },
    },
    {
        "name": "context_session_close",
        "description": "Закрыть активную сессию (футер + снять отметку активной).",
        "inputSchema": {"type": "object", "properties": {}},
    },
]

# ============================================================================
# Tool handlers (SKELETON — echo only, no core logic yet)
# ============================================================================


def _not_implemented(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Заглушка: подтверждает приём параметров, но возвращает not_implemented."""
    return {
        "error": {
            "code": "NotImplemented",
            "message": f"Tool '{tool_name}' is a skeleton. "
                       f"Use CLI fallback: python scripts/get_context.py ...",
        },
        "echo": {"tool": tool_name, "received_arguments": arguments},
        "skeleton": True,
    }


def _core_required() -> Optional[Dict[str, Any]]:
    if not CORE_LOADED:
        return {
            "error": {
                "code": "CoreUnavailable",
                "message": f"get_context core failed to import: {CORE_LOAD_ERROR}",
            }
        }
    return None


def _validate_required(arguments: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
    missing = [k for k in required if k not in arguments or arguments[k] in (None, "")]
    if missing:
        return {
            "error": {
                "code": "MissingParameter",
                "message": f"Missing required parameters: {', '.join(missing)}",
            }
        }
    return None


def _validate_enum(arguments: Dict[str, Any], field: str, allowed: List[str]) -> Optional[Dict[str, Any]]:
    if field in arguments and arguments[field] not in allowed:
        return {
            "error": {
                "code": "InvalidEnum",
                "message": f"Parameter '{field}'='{arguments[field]}' is not in {allowed}",
            }
        }
    return None


def tool_context_resolve(args: Dict[str, Any]) -> Dict[str, Any]:
    err = _validate_required(args, ["query"]) or _core_required()
    if err:
        return err
    try:
        result = core.resolve_query(args["query"], int(args.get("limit", 5)))  # type: ignore[union-attr]
    except Exception as e:  # noqa: BLE001
        logger.exception("context_resolve failed")
        return {"error": {"code": "CoreError", "message": str(e)}}
    return {
        "status": result.get("status"),
        "selected": result.get("selected"),
        "candidates": result.get("candidates", []),
    }


def tool_context_get(args: Dict[str, Any]) -> Dict[str, Any]:
    err = (
        _validate_required(args, ["query", "task"])
        or _validate_enum(args, "task", TASK_TYPES)
        or _validate_enum(args, "depth", DEPTH_VALUES)
        or _core_required()
    )
    if err:
        return err
    if "select" not in args and "candidate" not in args:
        # Run resolve first; if not_found — return synthetic no-target context so feedback can still be recorded.
        try:
            preview_resolve = core.resolve_query(args["query"], 5)  # type: ignore[union-attr]
        except Exception as e:  # noqa: BLE001
            logger.exception("context_resolve (preview) failed")
            return {"error": {"code": "CoreError", "message": str(e)}}
        # Treat as no-target if: not_found, no candidates, OR top candidate score is too weak
        # to be a meaningful match (typical garbage matches sit at score ~0.07).
        _cands = preview_resolve.get("candidates") or []
        _top_score = (_cands[0].get("score", 0.0) if _cands else 0.0)
        _no_target = (
            preview_resolve.get("status") == "not_found"
            or not _cands
            or _top_score < 0.20
        )
        if _no_target:
            from datetime import datetime
            now = datetime.now()
            no_target_id = "ctx-no-target-" + now.strftime("%Y%m%d-%H%M%S")
            budget = int(args.get("budget_tokens", 3000))
            resolve_meta = {
                "query": args["query"],
                "status": preview_resolve.get("status"),
                "selected": None,
                "candidates": preview_resolve.get("candidates", []),
                "top_score": _top_score,
                "candidate_count": len(_cands),
                "needed_user_clarification": True,
            }
            core.append_jsonl("context_requests.jsonl", {  # type: ignore[union-attr]
                "id": no_target_id,
                "datetime": now.isoformat(timespec="seconds"),
                "task_type": args["task"],
                "target": None,
                "depth": 0,
                "budget_tokens": budget,
                "actual_tokens": 0,
                "over_budget": False,
                "included": {},
                "sections": [],
                "graph_generated_at": None,
                "resolve": resolve_meta,
                "no_target": True,
            })
            return {
                "context_id": no_target_id,
                "selected": None,
                "task": args["task"],
                "sections": [],
                "tokens": {"actual": 0, "budget": budget, "over_budget": False},
                "tokens_actual": 0,
                "tokens_budget": budget,
                "over_budget": False,
                "context_text": "",
                "resolve": resolve_meta,
                "no_target": True,
                "hint": "No reliable target. Record feedback with this context_id.",
            }
        return {
            "error": {
                "code": "MissingParameter",
                "message": "Provide either 'select' (object_id) or 'candidate' (int from context_resolve).",
                "resolve": preview_resolve,
            }
        }
    query = args["query"]
    task = args["task"]
    try:
        resolve_result = core.resolve_query(query, 5)  # type: ignore[union-attr]
        selected = args.get("select") or resolve_result.get("selected")
        if not selected and args.get("candidate"):
            idx = int(args["candidate"]) - 1
            cands = resolve_result.get("candidates", [])
            if 0 <= idx < len(cands):
                selected = cands[idx]["object_id"]
        if not selected:
            return {
                "error": {
                    "code": "AmbiguousTarget",
                    "message": "Could not determine target. Use 'select' with explicit object_id.",
                    "resolve": resolve_result,
                }
            }

        depth_str = args.get("depth", "auto")
        stage = (args.get("stage") or "").strip() or None
        profile = core.profile_for(task, stage)  # type: ignore[union-attr]
        resolved_depth = core.resolve_depth(task, depth_str, profile)  # type: ignore[union-attr]
        budget = int(args.get("budget_tokens", 3000))
        context_text, metadata = core.build_context(  # type: ignore[union-attr]
            selected, task, resolved_depth, budget, stage=stage
        )

        metadata["resolve"] = {
            "query": query,
            "status": resolve_result.get("status"),
            "selected": selected,
            "candidates": resolve_result.get("candidates", []),
            "top_score": (resolve_result.get("candidates", [{}]) or [{}])[0].get("score", 0.0),
            "candidate_count": len(resolve_result.get("candidates", [])),
            "needed_user_clarification": resolve_result.get("status") != "resolved",
        }
        metadata["intent"] = (args.get("intent") or "").strip() or None
        stage_in_catalog = metadata.get("stage_in_catalog")
        core.append_jsonl("context_requests.jsonl", metadata)  # type: ignore[union-attr]
        if stage:
            core.append_jsonl("stages.jsonl", {  # type: ignore[union-attr]
                "datetime": metadata["datetime"],
                "context_id": metadata["id"],
                "task_type": task,
                "target": selected,
                "stage": stage,
                "intent": metadata["intent"],
                "in_catalog": stage_in_catalog,
            })
        if args.get("select") or args.get("candidate"):
            core.remember_alias(query, selected, task)  # type: ignore[union-attr]
    except Exception as e:  # noqa: BLE001
        logger.exception("context_get failed")
        return {"error": {"code": "CoreError", "message": str(e)}}

    return {
        "context_id": metadata.get("id"),
        "selected": selected,
        "stage": metadata.get("stage"),
        "stage_in_catalog": metadata.get("stage_in_catalog"),
        "stage_profile_applied": metadata.get("stage_profile_applied"),
        "tokens": {
            "actual": metadata.get("actual_tokens"),
            "budget": metadata.get("budget_tokens"),
            "over_budget": metadata.get("over_budget", False),
        },
        "sections": [
            {"name": s["name"], "kind": s["kind"], "tokens": s["tokens"], "items_count": len(s.get("items", []))}
            for s in metadata.get("sections", [])
        ],
        "resolve": metadata.get("resolve"),
        "no_target": False,
        "context": context_text,
    }


def tool_context_moc(args: Dict[str, Any]) -> Dict[str, Any]:
    err = _validate_required(args, ["type"]) or _validate_enum(args, "type", METADATA_TYPES) or _core_required()
    if err:
        return err
    try:
        rows = core.moc_rows(args["type"], args.get("filter"), int(args.get("limit", 50)))  # type: ignore[union-attr]
    except Exception as e:  # noqa: BLE001
        logger.exception("context_moc failed")
        return {"error": {"code": "CoreError", "message": str(e)}}
    return {"type": args["type"], "filter": args.get("filter"), "rows": rows}


def tool_context_feedback(args: Dict[str, Any]) -> Dict[str, Any]:
    err = _validate_required(args, ["context_id", "result", "rating"]) \
        or _validate_enum(args, "result", RESULT_VALUES) \
        or _core_required()
    if err:
        return err
    rating = args.get("rating")
    if not isinstance(rating, int) or not (1 <= rating <= 5):
        return {"error": {"code": "InvalidRange", "message": "rating must be int in 1..5"}}

    sections_map = args.get("sections") or {}
    if not isinstance(sections_map, dict):
        return {"error": {"code": "InvalidType", "message": "sections must be object {name: 'used'|'partial'|'unused'}"}}
    section_usage = []
    for name, level in sections_map.items():
        lvl = str(level).lower()
        if lvl not in {"used", "partial", "unused"}:
            return {"error": {"code": "InvalidEnum", "message": f"section '{name}' usage='{level}' invalid"}}
        section_usage.append({"name": str(name), "usage": lvl})

    extras = args.get("extras") or {}
    if not isinstance(extras, dict):
        return {"error": {"code": "InvalidType", "message": "extras must be object"}}

    context_id = args["context_id"]
    try:
        metadata = core.lookup_context_metadata(context_id)  # type: ignore[union-attr]

        section_stats = {
            "used": 0, "partial": 0, "unused": 0,
            "wasted_tokens": 0, "used_tokens": 0, "total_tokens": 0,
            "unmarked": [],
        }
        if metadata:
            usage_map = {item["name"]: item["usage"] for item in section_usage}
            for section in metadata.get("sections", []):
                tokens = section.get("tokens", 0)
                section_stats["total_tokens"] += tokens
                usage = usage_map.get(section["name"])
                if usage is None:
                    section_stats["unmarked"].append(section["name"])
                    continue
                section_stats[usage] = section_stats.get(usage, 0) + 1
                if usage == "unused":
                    section_stats["wasted_tokens"] += tokens
                elif usage == "used":
                    section_stats["used_tokens"] += tokens
                else:  # partial
                    section_stats["used_tokens"] += tokens // 2
                    section_stats["wasted_tokens"] += tokens - tokens // 2
            section_stats["waste_ratio"] = (
                round(section_stats["wasted_tokens"] / section_stats["total_tokens"], 3)
                if section_stats["total_tokens"] else 0.0
            )
        else:
            section_stats["context_metadata_missing"] = True

        from datetime import datetime
        result_value = args["result"]
        resolve_meta = metadata.get("resolve", {}) if metadata else {}
        no_target = bool(metadata.get("no_target")) if metadata else context_id.startswith("ctx-no-target-")
        row = {
            "datetime": datetime.now().isoformat(timespec="seconds"),
            "context_id": context_id,
            "task_type": metadata.get("task_type") if metadata else None,
            "target": metadata.get("target") if metadata else None,
            "stage": metadata.get("stage") if metadata else None,
            "intent": metadata.get("intent") if metadata else None,
            "actual_tokens": metadata.get("actual_tokens") if metadata else None,
            "no_target": no_target,
            "resolve_status": resolve_meta.get("status"),
            "resolve_top_score": resolve_meta.get("top_score"),
            "resolve_candidate_count": resolve_meta.get("candidate_count"),
            "needed_user_clarification": resolve_meta.get("needed_user_clarification"),
            "result": result_value,
            "rating": rating,
            "was_excessive": result_value == "excessive",
            "was_insufficient": result_value == "insufficient",
            "was_wrong": result_value == "wrong",
            "missing": [args["missing"]] if args.get("missing") else [],
            "excess": [args["excess"]] if args.get("excess") else [],
            "section_usage": section_usage,
            "section_stats": section_stats,
            "extra_searches": int(extras.get("searches", 0) or 0),
            "extra_files_read": int(extras.get("files_read", 0) or 0),
            "extra_mcp_calls": int(extras.get("mcp_calls", 0) or 0),
            "lost_time_minutes": None,
            "notes": args.get("notes") or "",
        }
        core.append_jsonl("context_feedback.jsonl", row)  # type: ignore[union-attr]
    except Exception as e:  # noqa: BLE001
        logger.exception("context_feedback failed")
        return {"error": {"code": "CoreError", "message": str(e)}}

    return {
        "stored": True,
        "context_id": context_id,
        "section_stats": section_stats,
        "metadata_found": metadata is not None,
    }


def tool_context_stages(args: Dict[str, Any]) -> Dict[str, Any]:
    err = _core_required()
    if err:
        return err
    return {
        "catalog": dict(core.STAGE_CATALOG),  # type: ignore[union-attr]
        "count": len(core.STAGE_CATALOG),  # type: ignore[union-attr]
    }


def tool_context_report(args: Dict[str, Any]) -> Dict[str, Any]:
    err = _core_required()
    if err:
        return err
    try:
        feedback_path = core.copilot_dir() / "context_feedback.jsonl"  # type: ignore[union-attr]
        if not feedback_path.exists():
            return {"feedback_count": 0, "message": "context_feedback.jsonl is empty"}

        rows: List[Dict[str, Any]] = []
        for line in feedback_path.read_text(encoding="utf-8-sig").splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        if not rows:
            return {"feedback_count": 0, "message": "context_feedback.jsonl is empty"}

        by_result: Dict[str, int] = {}
        by_task: Dict[str, Dict[str, int]] = {}
        waste_ratios: List[float] = []
        total_wasted = total_used = total_tokens = 0
        section_kind_stats: Dict[str, Dict[str, Any]] = {}
        by_stage: Dict[str, Dict[str, Any]] = {}
        rating_counts: Dict[str, int] = {}
        ratings: List[int] = []
        resolve_status_counts: Dict[str, int] = {}
        metadata_missing_feedback = 0
        no_target_feedback = 0
        feedback_with_unmarked_sections = 0
        unmarked_sections_total = 0
        needed_user_clarification = 0
        low_confidence_feedback = 0
        extra_searches_total = 0
        extra_files_total = 0
        extra_mcp_total = 0

        for row in rows:
            result = row.get("result", "?")
            by_result[result] = by_result.get(result, 0) + 1
            task = row.get("task_type") or "?"
            by_task.setdefault(task, {})
            by_task[task][result] = by_task[task].get(result, 0) + 1

            rating = row.get("rating")
            if isinstance(rating, int):
                ratings.append(rating)
                rating_counts[str(rating)] = rating_counts.get(str(rating), 0) + 1

            if row.get("no_target") or str(row.get("context_id", "")).startswith("ctx-no-target-"):
                no_target_feedback += 1
            if row.get("needed_user_clarification"):
                needed_user_clarification += 1
            resolve_status = row.get("resolve_status") or "?"
            resolve_status_counts[resolve_status] = resolve_status_counts.get(resolve_status, 0) + 1
            top_score = row.get("resolve_top_score")
            if isinstance(top_score, (int, float)) and top_score < 0.20:
                low_confidence_feedback += 1

            extra_searches_total += row.get("extra_searches", 0) or 0
            extra_files_total += row.get("extra_files_read", 0) or 0
            extra_mcp_total += row.get("extra_mcp_calls", 0) or 0

            stats = row.get("section_stats") or {}
            if stats.get("context_metadata_missing"):
                metadata_missing_feedback += 1
            unmarked = stats.get("unmarked") or []
            if unmarked:
                feedback_with_unmarked_sections += 1
                unmarked_sections_total += len(unmarked)
            if "waste_ratio" in stats:
                waste_ratios.append(stats["waste_ratio"])
                total_wasted += stats.get("wasted_tokens", 0)
                total_used += stats.get("used_tokens", 0)
                total_tokens += stats.get("total_tokens", 0)

            for usage_row in row.get("section_usage", []):
                kind = usage_row["name"].split(":", 1)[0]
                bucket = section_kind_stats.setdefault(
                    kind, {"used": 0, "partial": 0, "unused": 0, "total": 0}
                )
                bucket["total"] += 1
                bucket[usage_row["usage"]] = bucket.get(usage_row["usage"], 0) + 1

            stage = row.get("stage")
            if stage:
                sb = by_stage.setdefault(stage, {
                    "count": 0, "ratings": [], "waste_ratios": [],
                    "extra_searches": 0, "extra_files_read": 0, "extra_mcp_calls": 0,
                    "results": {}, "task_types": {}, "tokens_total": 0,
                })
                sb["count"] += 1
                if isinstance(row.get("rating"), int):
                    sb["ratings"].append(row["rating"])
                if "waste_ratio" in stats:
                    sb["waste_ratios"].append(stats["waste_ratio"])
                    sb["tokens_total"] += stats.get("total_tokens", 0)
                sb["extra_searches"] += row.get("extra_searches", 0) or 0
                sb["extra_files_read"] += row.get("extra_files_read", 0) or 0
                sb["extra_mcp_calls"] += row.get("extra_mcp_calls", 0) or 0
                sb["results"][result] = sb["results"].get(result, 0) + 1
                sb["task_types"][task] = sb["task_types"].get(task, 0) + 1

        section_kinds = {
            kind: {
                **stats,
                "unused_ratio": round(stats["unused"] / stats["total"], 3) if stats["total"] else 0.0,
            }
            for kind, stats in sorted(section_kind_stats.items())
        }
        trim_candidates = sorted(
            [{"kind": k, **v} for k, v in section_kinds.items() if v["total"] >= 3 and v["unused_ratio"] >= 0.5],
            key=lambda x: x["unused_ratio"], reverse=True,
        )

        stages_summary = {}
        for stage_name, b in by_stage.items():
            ratings = b["ratings"]
            wastes = b["waste_ratios"]
            stages_summary[stage_name] = {
                "count": b["count"],
                "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
                "avg_waste_ratio": round(sum(wastes) / len(wastes), 3) if wastes else None,
                "tokens_total": b["tokens_total"],
                "extra_searches": b["extra_searches"],
                "extra_files_read": b["extra_files_read"],
                "extra_mcp_calls": b["extra_mcp_calls"],
                "results": b["results"],
                "task_types": b["task_types"],
            }
        problem_stages = []
        for stage_name, info in stages_summary.items():
            if info["count"] < 2:
                continue
            signals = []
            if info["avg_rating"] is not None and info["avg_rating"] < 3:
                signals.append(f"rating={info['avg_rating']}")
            if info["avg_waste_ratio"] is not None and info["avg_waste_ratio"] >= 0.4:
                signals.append(f"waste={info['avg_waste_ratio']}")
            per_call = (info["extra_searches"] + info["extra_files_read"] + info["extra_mcp_calls"]) / info["count"]
            if per_call >= 2:
                signals.append(f"extra/call={round(per_call, 1)}")
            if signals:
                problem_stages.append({"stage": stage_name, "count": info["count"], "signals": signals})
    except Exception as e:  # noqa: BLE001
        logger.exception("context_report failed")
        return {"error": {"code": "CoreError", "message": str(e)}}

    return {
        "feedback_count": len(rows),
        "by_result": by_result,
        "result_rates": {
            key: round(value / len(rows), 3) if rows else 0.0
            for key, value in sorted(by_result.items())
        },
        "by_task_type": by_task,
        "ratings": {
            "avg": round(sum(ratings) / len(ratings), 2) if ratings else None,
            "distribution": rating_counts,
        },
        "tokens": {
            "total": total_tokens,
            "used": total_used,
            "wasted": total_wasted,
            "used_ratio": round(total_used / total_tokens, 3) if total_tokens else None,
            "wasted_ratio": round(total_wasted / total_tokens, 3) if total_tokens else None,
            "waste_ratio_avg": round(sum(waste_ratios) / len(waste_ratios), 3) if waste_ratios else None,
        },
        "quality": {
            "metadata_missing_feedback": metadata_missing_feedback,
            "no_target_feedback": no_target_feedback,
            "feedback_with_unmarked_sections": feedback_with_unmarked_sections,
            "unmarked_sections_total": unmarked_sections_total,
            "needed_user_clarification": needed_user_clarification,
            "low_confidence_feedback": low_confidence_feedback,
            "extra_actions_total": extra_searches_total + extra_files_total + extra_mcp_total,
            "extra_actions_avg": round((extra_searches_total + extra_files_total + extra_mcp_total) / len(rows), 2) if rows else 0.0,
            "extra_searches": extra_searches_total,
            "extra_files_read": extra_files_total,
            "extra_mcp_calls": extra_mcp_total,
        },
        "resolve": {
            "by_status": resolve_status_counts,
            "low_confidence_threshold": 0.20,
        },
        "section_kinds": section_kinds,
        "trim_candidates": trim_candidates,
        "stages": dict(sorted(stages_summary.items(), key=lambda kv: kv[1]["count"], reverse=True)),
        "problem_stages": sorted(problem_stages, key=lambda x: x["count"], reverse=True),
    }


def tool_context_session_start(args: Dict[str, Any]) -> Dict[str, Any]:
    if _read_active_session() is not None:
        return {
            "error": {
                "code": "SessionAlreadyOpen",
                "message": f"Active session exists: {_read_active_session()}. "
                           f"Close it first via context_session_close.",
            }
        }
    from datetime import datetime
    now = datetime.now()
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    fname = now.strftime("%Y-%m-%d_%H%M") + "__session.md"
    path = SESSIONS_DIR / fname
    title = (args.get("title") or "").strip()
    header = (
        f"# Context Audit Session\n\n"
        f"- **Started:** {now.strftime('%Y-%m-%d %H:%M')}\n"
        f"- **Agent:** context-tester\n"
        f"- **Title:** {title}\n"
        f"- **Tasks:** 0\n"
    )
    path.write_text(header, encoding="utf-8")
    _write_active_session(path)
    return {
        "session_path": str(path.relative_to(WORKSPACE_ROOT)).replace("\\", "/"),
        "started_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "title": title,
    }


def _format_recon_step(p: Dict[str, Any]) -> str:
    step_no = p.get('step_no')
    if step_no in (None, '', '?'):
        step_no = p.get('_auto_step_no', '?')
    return (
        f"\n#### [{p.get('time', '')}] STEP {step_no} — {p.get('name', '')}\n"
        f"- **action:** {p.get('action', '')}\n"
        f"- **target:** {p.get('target', '')}\n"
        f"- **decision_reason:** {p.get('decision_reason', '')}\n"
        f"- **source:** {p.get('source', '')}\n"
        f"- **result:** {p.get('result', '')}\n"
        f"- **counts_as:** {p.get('counts_as', '')}\n"
        f"- **gap_probe:** {p.get('gap_probe', False)}\n"
    )


def _format_task_header(p: Dict[str, Any], task_no: int, time_str: str) -> str:
    qs = p.get("questions") or []
    qs_md = "\n".join(f"  {i+1}. {q}" for i, q in enumerate(qs))
    return (
        f"\n## Task {task_no} — {p.get('slug', p.get('task_type', 'task'))}\n\n"
        f"- **Started:** {time_str}\n"
        f"- **Task:** {p.get('task', '')}\n"
        f"- **Task type:** {p.get('task_type', '')}\n"
        f"- **Questions for executor:**\n{qs_md}\n\n"
        f"### Recon Log\n"
    )


def _format_delivered(p: Dict[str, Any]) -> str:
    secs = p.get("sections") or []
    rows = "\n".join(
        f"| {s.get('name','')} | {s.get('kind','')} | {s.get('tokens','')} |"
        for s in secs
    )
    return (
        f"\n### Delivered by `get_context.py`\n\n"
        f"- **context_id:** {p.get('context_id', '')}\n"
        f"- **stage:** {p.get('stage', '')}\n"
        f"- **tokens:** {p.get('tokens_actual','?')}/{p.get('tokens_budget','?')}\n\n"
        f"| section | kind | tokens |\n|---|---|---|\n{rows}\n"
    )


def _format_coverage(p: Dict[str, Any]) -> str:
    rows = p.get("rows") or []
    formatted = []
    for idx, r in enumerate(rows, start=1):
        cb = r.get("covered_by")
        if cb is None:
            cb_md = "—"
        elif isinstance(cb, str):
            cb_md = cb if cb.strip() else "—"
        elif isinstance(cb, (list, tuple)):
            cb_md = ", ".join(str(x) for x in cb if x) or "—"
        else:
            cb_md = str(cb)
        no = r.get("no") or idx
        formatted.append(
            f"| {no} | {r.get('question','')} | {cb_md} | {r.get('gap') or '—'} | {r.get('gap_resolution') or '—'} |"
        )
    rows_md = "\n".join(formatted)
    return (
        f"\n### Покрытие вопросов исполнителя\n\n"
        f"| # | вопрос | covered_by | gap | как закрыт |\n|---|---|---|---|---|\n{rows_md}\n"
    )


def _filter_topic_items(items: Any) -> List[Dict[str, Any]]:
    """Drop empty {topic, comment} entries to avoid `**** — ` lines."""
    out: List[Dict[str, Any]] = []
    for i in items or []:
        if not isinstance(i, dict):
            continue
        topic = (i.get("topic") or "").strip()
        comment = (i.get("comment") or "").strip()
        if not topic and not comment:
            continue
        out.append({"topic": topic, "comment": comment})
    return out


def _format_excess(p: Dict[str, Any]) -> str:
    items = _filter_topic_items(p.get("items"))
    if not items:
        body = "_(агент не зафиксировал избыточных секций)_"
    else:
        body = "\n".join(f"- **{i['topic']}** — {i['comment']}" for i in items)
    return f"\n### 🟡 ИЗБЫТОЧНО (что было лишним)\n\n{body}\n"


def _format_missing(p: Dict[str, Any]) -> str:
    items = _filter_topic_items(p.get("items"))
    if not items:
        body = "_(агент не зафиксировал недостающих данных)_"
    else:
        body = "\n".join(f"- **{i['topic']}** — {i['comment']}" for i in items)
    return f"\n### 🔴 НЕДОСТАТОЧНО (чего не хватило)\n\n{body}\n"


def _format_decision(p: Dict[str, Any]) -> str:
    return (
        f"\n### Решение по задаче\n\n"
        f"- **result:** {p.get('result', '')}\n"
        f"- **rating:** {p.get('rating', '')}\n"
        f"- **feedback_executed:** {p.get('feedback_executed', False)}\n"
        f"- **Ended:** {p.get('ended_at', '')}\n"
    )


def tool_context_session_append(args: Dict[str, Any]) -> Dict[str, Any]:
    err = _validate_required(args, ["kind", "payload"]) or _validate_enum(args, "kind", APPEND_KINDS)
    if err:
        return err
    if not isinstance(args.get("payload"), dict):
        return {"error": {"code": "InvalidType", "message": "payload must be an object"}}
    session = _read_active_session()
    if session is None:
        return {"error": {"code": "NoActiveSession", "message": "Open a session via context_session_start first."}}

    from datetime import datetime
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    payload = args["payload"]
    kind = args["kind"]

    if kind == "task_header":
        task_no = _count_tasks(session) + 1
        md = _format_task_header(payload, task_no, time_str)
        # bump Tasks counter in header
        txt = session.read_text(encoding="utf-8")
        import re
        new_txt, n = re.subn(r"^- \*\*Tasks:\*\* \d+", f"- **Tasks:** {task_no}", txt, count=1, flags=re.MULTILINE)
        if n:
            session.write_text(new_txt, encoding="utf-8")
        _append_to_session(session, md)
        return {"appended_at": time_str, "task_no": task_no, "kind": kind}
    elif kind == "recon_step":
        payload.setdefault("time", time_str)
        # Auto-number STEP within current task block if step_no not provided
        if payload.get("step_no") in (None, "", "?"):
            payload["_auto_step_no"] = _next_step_no(session)
        _append_to_session(session, _format_recon_step(payload))
    elif kind == "delivered":
        _append_to_session(session, _format_delivered(payload))
    elif kind == "coverage":
        _append_to_session(session, _format_coverage(payload))
    elif kind == "excess":
        _append_to_session(session, _format_excess(payload))
    elif kind == "missing":
        _append_to_session(session, _format_missing(payload))
    elif kind == "decision":
        payload.setdefault("ended_at", time_str)
        _append_to_session(session, _format_decision(payload))
    elif kind == "free_markdown":
        md = payload.get("markdown", "")
        if not isinstance(md, str):
            return {"error": {"code": "InvalidType", "message": "payload.markdown must be string"}}
        _append_to_session(session, md)
    return {"appended_at": time_str, "task_no": _count_tasks(session), "kind": kind}


def tool_context_session_close(args: Dict[str, Any]) -> Dict[str, Any]:
    session = _read_active_session()
    if session is None:
        return {"error": {"code": "NoActiveSession", "message": "No active session to close."}}
    from datetime import datetime
    now = datetime.now()
    total = _count_tasks(session)
    footer = f"\n---\n**Closed:** {now.strftime('%Y-%m-%d %H:%M')}\n**Total tasks:** {total}\n"
    _append_to_session(session, footer)
    rel = str(session.relative_to(WORKSPACE_ROOT)).replace("\\", "/")
    _write_active_session(None)
    return {"closed_at": now.strftime("%Y-%m-%d %H:%M:%S"), "session_path": rel, "total_tasks": total}


TOOL_HANDLERS = {
    "context_resolve": tool_context_resolve,
    "context_get": tool_context_get,
    "context_moc": tool_context_moc,
    "context_feedback": tool_context_feedback,
    "context_stages": tool_context_stages,
    "context_report": tool_context_report,
    "context_session_start": tool_context_session_start,
    "context_session_append": tool_context_session_append,
    "context_session_close": tool_context_session_close,
}


def handle_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    handler = TOOL_HANDLERS.get(name)
    if not handler:
        return {"error": {"code": "UnknownTool", "message": f"Unknown tool: {name}"}}
    try:
        return handler(arguments or {})
    except Exception as e:
        logger.exception(f"Tool {name} failed")
        return {"error": {"code": "InternalError", "message": str(e)}}


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
        return make_response(req_id, {"tools": TOOLS})

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
    """Main loop: read JSON-RPC from stdin, write to stdout."""
    logger.info("context-mcp server starting (stdio, skeleton)")

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

    logger.info("context-mcp server stopped")


if __name__ == "__main__":
    run_stdio()
