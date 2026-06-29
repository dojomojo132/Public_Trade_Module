"""
Parse VS Code Copilot chat transcript JSONL into structured markdown analysis.

Usage:
    python scripts/parse_session.py --last
    python scripts/parse_session.py --file <path-to-transcript.jsonl>
    python scripts/parse_session.py --session <sessionId>
    python scripts/parse_session.py --last --task "<task name>"
    python scripts/parse_session.py --last --task "<task>" --task-link "Dev/Tasks/Done/2026-05-06_<имя>"

Output (default): <vault>/99-Meta/Sessions/<YYYY-MM-DD_HHMM>__closer__<task>.md
  Vault path читается из config.json -> obsidian_vault_path.
  Папка сессий: config.json -> obsidian_sessions_folder (по умолчанию 99-Meta/Sessions).
Override: --output-dir <path>
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPTS_DIR = Path(
    os.environ.get(
        "VSCODE_TRANSCRIPTS_DIR",
        Path(os.environ["APPDATA"])
        / "Code/User/workspaceStorage/fd1c3207877997ea6f0ed91290588328/GitHub.copilot-chat/transcripts",
    )
)


def _resolve_default_output_dir() -> Path:
    """Default sessions dir = <vault>/<obsidian_sessions_folder> (config.json).
    Fallback to Документация/Анализ_Сессий if config.json missing/invalid."""
    cfg_path = REPO_ROOT / "config.json"
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8-sig"))
        vault = cfg.get("obsidian_vault_path")
        if vault:
            sessions = cfg.get("obsidian_sessions_folder", "99-Meta/Sessions")
            return Path(vault) / sessions
    except Exception:
        pass
    return REPO_ROOT / "Документация" / "Анализ_Сессий"


OUTPUT_DIR = _resolve_default_output_dir()


def find_latest_transcript() -> Path:
    files = sorted(TRANSCRIPTS_DIR.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        sys.exit(f"No transcripts in {TRANSCRIPTS_DIR}")
    return files[0]


def load_events(path: Path) -> list[dict]:
    events: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def short(text: str, limit: int = 200) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def args_summary(args: dict | str | None, limit: int = 160) -> str:
    if args is None:
        return ""
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            return short(args, limit)
    keys_of_interest = ("filePath", "path", "command", "query", "name", "action", "symbol", "url")
    parts = []
    for k in keys_of_interest:
        if isinstance(args, dict) and k in args and args[k]:
            v = args[k]
            if isinstance(v, (list, dict)):
                v = json.dumps(v, ensure_ascii=False)
            parts.append(f"{k}={short(str(v), 80)}")
    if not parts and isinstance(args, dict):
        parts = [f"{k}={short(str(v), 60)}" for k, v in list(args.items())[:3]]
    return ", ".join(parts)[:limit]


# --- Trace block extraction (orchestrator/subagent protocol from copilot-instructions §8) ---

TRACE_HEADER_RE = re.compile(r"^##\s+(?:📊\s+)?Trace\s*$", re.MULTILINE)
TRACE_FIELD_RE = re.compile(r"^-\s*([A-Za-z_]+)\s*:\s*(.+?)$", re.MULTILINE)
TRACE_ACTION_RE = re.compile(
    r"^\s*-\s*\[(\d{2}:\d{2}:\d{2})\]\s*(MCP|EDIT|TERMINAL|DECISION|ERROR|PHASE|SUBAGENT)\s*(.*)$",
    re.MULTILINE,
)


def extract_traces(text: str) -> list[dict]:
    """Find all `## 📊 Trace` blocks in assistant message and parse their actions."""
    traces: list[dict] = []
    if not text:
        return traces
    headers = list(TRACE_HEADER_RE.finditer(text))
    for i, h in enumerate(headers):
        block_start = h.end()
        block_end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        block = text[block_start:block_end]
        # Stop at next ## heading
        nxt = re.search(r"^##\s+\S", block, re.MULTILINE)
        if nxt:
            block = block[: nxt.start()]
        fields = {m.group(1).lower(): m.group(2).strip() for m in TRACE_FIELD_RE.finditer(block)}
        actions = [
            {"time": m.group(1), "kind": m.group(2), "text": m.group(3).strip()}
            for m in TRACE_ACTION_RE.finditer(block)
        ]
        if fields or actions:
            traces.append({"fields": fields, "actions": actions})
    return traces


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars/token for mixed RU/EN."""
    if not text:
        return 0
    return max(1, len(text) // 4)


def scan_github_overhead(repo_root: Path) -> dict:
    """Scan .github/** and classify files by loading mode.

    Returns dict with keys:
      always_loaded: list of (path, tokens) — copilot-instructions.md + instructions/*.md with applyTo: "**"
      conditional: list of (path, tokens, applyTo) — instructions tied to specific file pattern
      on_demand: list of (path, tokens, kind) — skills, agents, prompts
      totals: aggregate dict
    """
    gh = repo_root / ".github"
    always: list[tuple[str, int]] = []
    cond: list[tuple[str, int, str]] = []
    on_demand: list[tuple[str, int, str]] = []

    if not gh.exists():
        return {"always_loaded": [], "conditional": [], "on_demand": [], "totals": {}}

    apply_re = re.compile(r"^applyTo:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)

    def fsize_tokens(p: Path) -> int:
        try:
            return estimate_tokens(p.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            return 0

    # 1. copilot-instructions.md — always loaded
    ci = gh / "copilot-instructions.md"
    if ci.exists():
        always.append((str(ci.relative_to(repo_root)), fsize_tokens(ci)))

    # 2. instructions/*.md
    inst_dir = gh / "instructions"
    if inst_dir.exists():
        for p in sorted(inst_dir.glob("*.md")):
            text = p.read_text(encoding="utf-8", errors="ignore")
            tk = estimate_tokens(text)
            m = apply_re.search(text)
            apply_to = m.group(1).strip() if m else ""
            rel = str(p.relative_to(repo_root))
            if apply_to == "**" or apply_to == "**/*":
                always.append((rel, tk))
            elif apply_to:
                cond.append((rel, tk, apply_to))
            else:
                on_demand.append((rel, tk, "instruction-no-applyTo"))

    # 3. skills/**/SKILL.md
    skills_dir = gh / "skills"
    if skills_dir.exists():
        for p in sorted(skills_dir.rglob("SKILL.md")):
            on_demand.append((str(p.relative_to(repo_root)), fsize_tokens(p), "skill"))

    # 4. agents/*.agent.md
    agents_dir = gh / "agents"
    if agents_dir.exists():
        for p in sorted(agents_dir.glob("*.agent.md")):
            on_demand.append((str(p.relative_to(repo_root)), fsize_tokens(p), "agent"))

    # 5. prompts/*.prompt.md
    prompts_dir = gh / "prompts"
    if prompts_dir.exists():
        for p in sorted(prompts_dir.glob("*.prompt.md")):
            on_demand.append((str(p.relative_to(repo_root)), fsize_tokens(p), "prompt"))

    totals = {
        "always_loaded_tokens": sum(t for _, t in always),
        "conditional_tokens": sum(t for _, t, _ in cond),
        "on_demand_tokens": sum(t for _, t, _ in on_demand),
        "always_loaded_files": len(always),
        "conditional_files": len(cond),
        "on_demand_files": len(on_demand),
    }
    totals["grand_total_tokens"] = (
        totals["always_loaded_tokens"] + totals["conditional_tokens"] + totals["on_demand_tokens"]
    )
    return {"always_loaded": always, "conditional": cond, "on_demand": on_demand, "totals": totals}


def analyse(events: list[dict]) -> dict:
    session_id = ""
    started: datetime | None = None
    ended: datetime | None = None
    user_messages: list[tuple[datetime, str]] = []
    assistant_messages: list[tuple[datetime, str, str]] = []  # (ts, content, reasoning)
    tool_calls_by_id: dict[str, dict] = {}
    tool_order: list[str] = []
    errors: list[dict] = []
    traces: list[dict] = []
    decisions: list[tuple[datetime, str, str]] = []  # (ts, agent, text)
    phase_events: list[tuple[datetime, str, str]] = []  # (ts, agent, text)
    user_chars = 0
    assistant_chars = 0
    reasoning_chars = 0
    tool_arg_chars = 0
    subagent_calls: list[dict] = []

    for ev in events:
        et = ev.get("type", "")
        data = ev.get("data", {}) or {}
        ts = ev.get("timestamp")
        ts_dt = parse_iso(ts) if ts else None
        if ts_dt:
            started = ts_dt if started is None else min(started, ts_dt)
            ended = ts_dt if ended is None else max(ended, ts_dt)

        if et == "session.start":
            session_id = data.get("sessionId", "")
        elif et == "user.message":
            content = data.get("content", "")
            user_messages.append((ts_dt, content))
            user_chars += len(content or "")
        elif et == "assistant.message":
            content = data.get("content", "")
            reasoning = data.get("reasoningText", "") or ""
            assistant_messages.append((ts_dt, content, reasoning))
            assistant_chars += len(content or "")
            reasoning_chars += len(reasoning)
            for tr in extract_traces(content):
                tr["ts"] = ts_dt
                traces.append(tr)
                agent = tr["fields"].get("agent", "?")
                for a in tr["actions"]:
                    if a["kind"] == "DECISION":
                        decisions.append((ts_dt, agent, a["text"]))
                    elif a["kind"] == "PHASE":
                        phase_events.append((ts_dt, agent, a["text"]))
        elif et == "tool.execution_start":
            tid = data.get("toolCallId", "")
            tname = data.get("toolName", "")
            targs = data.get("arguments")
            tool_arg_chars += len(json.dumps(targs, ensure_ascii=False)) if targs else 0
            tool_calls_by_id[tid] = {
                "id": tid,
                "name": tname,
                "args": targs,
                "start": ts_dt,
                "end": None,
                "success": None,
                "error": None,
            }
            tool_order.append(tid)
            if tname == "runSubagent":
                a = targs if isinstance(targs, dict) else {}
                if isinstance(targs, str):
                    try:
                        a = json.loads(targs)
                    except Exception:
                        a = {}
                subagent_calls.append({
                    "ts": ts_dt,
                    "agent": a.get("agentName") or "(default)",
                    "description": a.get("description", ""),
                    "prompt": short(a.get("prompt", ""), 300),
                })
        elif et == "tool.execution_complete":
            tid = data.get("toolCallId", "")
            rec = tool_calls_by_id.get(tid)
            if rec is not None:
                rec["end"] = ts_dt
                rec["success"] = data.get("success")
                if data.get("success") is False:
                    err = {
                        "tool": rec["name"],
                        "args": args_summary(rec["args"]),
                        "ts": ts_dt,
                        "error": data.get("error") or data.get("errorMessage") or "(no error message)",
                    }
                    errors.append(err)
                    rec["error"] = err["error"]

    # Aggregations
    tool_counter = Counter(t["name"] for t in tool_calls_by_id.values())
    duration = (ended - started).total_seconds() if started and ended else 0

    files_edited: set[str] = set()
    files_read: set[str] = set()
    terminal_cmds: list[str] = []
    for t in tool_calls_by_id.values():
        name = t["name"]
        a = t["args"]
        if isinstance(a, str):
            try:
                a = json.loads(a)
            except Exception:
                a = {}
        if not isinstance(a, dict):
            continue
        path = a.get("filePath") or a.get("path") or ""
        if name in {"replace_string_in_file", "create_file", "multi_replace_string_in_file", "edit_notebook_file"}:
            if path:
                files_edited.add(path)
            for r in a.get("replacements", []) or []:
                if isinstance(r, dict) and r.get("filePath"):
                    files_edited.add(r["filePath"])
        elif name in {"read_file", "view_image"}:
            if path:
                files_read.add(path)
        elif name == "run_in_terminal":
            cmd = a.get("command", "")
            if cmd:
                terminal_cmds.append(cmd)

    result = {
        "session_id": session_id,
        "started": started,
        "ended": ended,
        "duration_s": duration,
        "user_messages": user_messages,
        "assistant_messages": assistant_messages,
        "tool_calls_by_id": tool_calls_by_id,
        "tool_order": tool_order,
        "tool_counter": tool_counter,
        "errors": errors,
        "files_edited": sorted(files_edited),
        "files_read": sorted(files_read),
        "terminal_cmds": terminal_cmds,
        "traces": traces,
        "decisions": decisions,
        "phase_events": phase_events,
        "subagent_calls": subagent_calls,
        "tokens_estimate": {
            "user": estimate_tokens("x" * user_chars),
            "assistant": estimate_tokens("x" * assistant_chars),
            "reasoning": estimate_tokens("x" * reasoning_chars),
            "tool_args": estimate_tokens("x" * tool_arg_chars),
            "total": estimate_tokens("x" * (user_chars + assistant_chars + reasoning_chars + tool_arg_chars)),
        },
        "github_overhead": scan_github_overhead(REPO_ROOT),
        "subagents_invoked": sorted({s["agent"] for s in subagent_calls}),
    }
    result["antipatterns"] = detect_antipatterns(result)
    return result


def detect_antipatterns(stats: dict) -> list[dict]:
    """Detect inefficient behavior patterns in the session.

    Returns list of {severity, kind, message, details} dicts.
    severity: 'high' | 'medium' | 'low'
    """
    findings: list[dict] = []
    tool_order = stats["tool_order"]
    calls = stats["tool_calls_by_id"]

    # 1. Consecutive identical tool calls (same name + same args) — full dedup loop
    consecutive: list[tuple[str, int, str]] = []  # (tool_name, count, args_signature)
    prev_sig: tuple[str, str] | None = None
    streak = 1
    for cid in tool_order:
        info = calls.get(cid, {})
        name = info.get("name", "")
        args = info.get("args")
        sig = (name, json.dumps(args, sort_keys=True, ensure_ascii=False)[:200] if args else "")
        if sig == prev_sig:
            streak += 1
        else:
            if prev_sig and streak >= 3:
                consecutive.append((prev_sig[0], streak, prev_sig[1][:120]))
            streak = 1
        prev_sig = sig
    if prev_sig and streak >= 3:
        consecutive.append((prev_sig[0], streak, prev_sig[1][:120]))
    for name, cnt, sig in consecutive:
        findings.append({
            "severity": "high",
            "kind": "consecutive_duplicate_calls",
            "message": f"{cnt}× подряд одинаковый вызов `{name}` — возможное зацикливание",
            "details": sig,
        })

    # 2. Same file read >= 3 times
    read_counter: Counter = Counter()
    for cid in tool_order:
        info = calls.get(cid, {})
        if info.get("name") == "read_file":
            args = info.get("args") or {}
            fp = args.get("filePath") if isinstance(args, dict) else None
            if fp:
                read_counter[fp] += 1
    for fp, cnt in read_counter.items():
        if cnt >= 3:
            findings.append({
                "severity": "medium" if cnt < 5 else "high",
                "kind": "repeated_file_read",
                "message": f"Файл прочитан {cnt}× — стоило прочитать большим диапазоном за раз",
                "details": fp,
            })

    # 3. Errors clustered on same tool (>=3 failures of one tool)
    err_counter: Counter = Counter()
    for e in stats["errors"]:
        err_counter[e.get("tool", "?")] += 1
    for tool, cnt in err_counter.items():
        if cnt >= 3:
            findings.append({
                "severity": "high",
                "kind": "repeated_errors",
                "message": f"{cnt} ошибок инструмента `{tool}` — повторение без смены подхода",
                "details": "",
            })

    # 4. Multiple grep_search calls — possible search-instead-of-read
    grep_args: list[str] = []
    for cid in tool_order:
        info = calls.get(cid, {})
        if info.get("name") == "grep_search":
            args = info.get("args") or {}
            q = args.get("query") if isinstance(args, dict) else None
            if q:
                grep_args.append(q)
    if len(grep_args) >= 5:
        findings.append({
            "severity": "medium",
            "kind": "excessive_search",
            "message": f"{len(grep_args)} вызовов grep_search — много поисков подряд, возможно надо было читать файл целиком",
            "details": "; ".join(grep_args[:5]) + (" ..." if len(grep_args) > 5 else ""),
        })

    # 5. tool_args dominate token cost (>70% of dialog tokens)
    tk = stats["tokens_estimate"]
    if tk["total"] > 0:
        ratio = tk["tool_args"] / tk["total"]
        if ratio > 0.7:
            findings.append({
                "severity": "medium",
                "kind": "tool_args_dominate",
                "message": f"tool_args = {ratio:.0%} от диалога ({tk['tool_args']:,} из {tk['total']:,}) — возможно передаются избыточные аргументы",
                "details": "",
            })

    # 6. No Trace blocks despite subagent calls (regulation violation)
    if stats["subagent_calls"] and not stats["traces"]:
        findings.append({
            "severity": "high",
            "kind": "missing_traces",
            "message": f"Вызвано {len(stats['subagent_calls'])} субагентов, но ни один не вернул блок ## 📊 Trace — нарушение протокола §8",
            "details": "",
        })

    # 7. Replace+read loop (replace failure → read → replace) — heuristic: many alternations
    replace_read_pairs = 0
    last_was_replace_fail = False
    for cid in tool_order:
        info = calls.get(cid, {})
        name = info.get("name", "")
        if name in {"replace_string_in_file", "multi_replace_string_in_file"}:
            last_was_replace_fail = not info.get("success", True)
        elif name == "read_file" and last_was_replace_fail:
            replace_read_pairs += 1
            last_was_replace_fail = False
        else:
            last_was_replace_fail = False
    if replace_read_pairs >= 2:
        findings.append({
            "severity": "medium",
            "kind": "replace_failure_loop",
            "message": f"{replace_read_pairs}× после провала replace_string_in_file → read_file. Стоит сразу читать с большим контекстом перед заменой",
            "details": "",
        })

    return findings


def to_markdown(stats: dict, source: Path, task: str, task_link: str = "") -> str:
    lines: list[str] = []
    started = stats["started"]
    ended = stats["ended"]

    # YAML frontmatter — обязательная связка план↔сессия (см. copilot-instructions.md §8)
    lines.append("---")
    lines.append("type: session")
    lines.append(f"agent: closer")
    lines.append(f"task: {task or '(без названия)'}")
    if task_link:
        # task_link: путь к плану внутри vault, например "Dev/Tasks/Done/2026-05-06_имя"
        lines.append(f"task_link: \"[[{task_link}]]\"")
    lines.append(f"started: {started.isoformat() if started else ''}")
    lines.append(f"ended: {ended.isoformat() if ended else ''}")
    lines.append(f"duration_min: {(stats['duration_s']/60):.1f}" if stats.get('duration_s') else "duration_min: 0")
    lines.append("---")
    lines.append("")

    lines.append(f"# Анализ сессии: {task or '(без названия)'}")
    lines.append("")
    if task_link:
        lines.append(f"> 🔗 **План задачи:** [[{task_link}]]")
        lines.append("")
    lines.append(f"- **Source**: `{source.name}`")
    lines.append(f"- **Session ID**: `{stats['session_id']}`")
    lines.append(f"- **Started**: {started.isoformat() if started else '?'}")
    lines.append(f"- **Ended**: {ended.isoformat() if ended else '?'}")
    lines.append(f"- **Duration**: {stats['duration_s']:.0f} s ({stats['duration_s']/60:.1f} min)")
    lines.append(f"- **User messages**: {len(stats['user_messages'])}")
    lines.append(f"- **Assistant messages**: {len(stats['assistant_messages'])}")
    lines.append(f"- **Tool calls**: {len(stats['tool_calls_by_id'])}")
    lines.append(f"- **Errors**: {len(stats['errors'])}")
    lines.append(f"- **Files edited**: {len(stats['files_edited'])}")
    lines.append(f"- **Files read**: {len(stats['files_read'])}")
    lines.append(f"- **Terminal commands**: {len(stats['terminal_cmds'])}")
    lines.append("")

    # Antipatterns — surface to the top
    aps = stats.get("antipatterns", [])
    if aps:
        sev_emoji = {"high": "🔴", "medium": "🟡", "low": "⚪"}
        lines.append(f"## ⚠️ Обнаруженные антипаттерны ({len(aps)})")
        lines.append("")
        lines.append("| Severity | Паттерн | Описание | Детали |")
        lines.append("|----------|---------|----------|--------|")
        for ap in sorted(aps, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["severity"]]):
            details = ap.get("details", "")
            details_short = (details[:80] + "…") if len(details) > 80 else details
            lines.append(
                f"| {sev_emoji.get(ap['severity'], '')} {ap['severity']} | `{ap['kind']}` | {ap['message']} | `{details_short}` |"
            )
        lines.append("")
    else:
        lines.append("## ✅ Антипаттерны не обнаружены")
        lines.append("")

    tk = stats["tokens_estimate"]
    lines.append("## Оценка токенов (приблизительно, ~4 chars/token)")
    lines.append("")
    lines.append("| Поток | Токены |")
    lines.append("|-------|--------|")
    lines.append(f"| user | {tk['user']:,} |")
    lines.append(f"| assistant (вывод) | {tk['assistant']:,} |")
    lines.append(f"| reasoning (thinking) | {tk['reasoning']:,} |")
    lines.append(f"| tool args | {tk['tool_args']:,} |")
    lines.append(f"| **итого диалог** | **{tk['total']:,}** |")
    lines.append("")

    # GitHub overhead
    gh = stats["github_overhead"]
    if gh.get("totals"):
        t = gh["totals"]
        invoked = set(stats["subagents_invoked"])
        # which on_demand were actually invoked
        invoked_tokens = 0
        invoked_files: list[tuple[str, int, str]] = []
        for path, tk_, kind in gh["on_demand"]:
            name = Path(path).stem.replace(".agent", "").replace("SKILL", Path(path).parent.name)
            base = Path(path).name
            if kind == "agent":
                agent_name = base.replace(".agent.md", "")
                if agent_name in invoked:
                    invoked_tokens += tk_
                    invoked_files.append((path, tk_, kind))

        lines.append("## Накладные расходы .github/** (загрузка инструкций/скиллов/агентов)")
        lines.append("")
        lines.append("| Категория | Файлов | Токены |")
        lines.append("|-----------|-------:|-------:|")
        lines.append(
            f"| Always loaded (copilot-instructions + applyTo='**') | {t['always_loaded_files']} | {t['always_loaded_tokens']:,} |"
        )
        lines.append(
            f"| Conditional (instructions с applyTo) | {t['conditional_files']} | {t['conditional_tokens']:,} |"
        )
        lines.append(
            f"| On-demand (skills + agents + prompts, потенциал) | {t['on_demand_files']} | {t['on_demand_tokens']:,} |"
        )
        lines.append(f"| **Сумма потенциала .github/** | **{t['always_loaded_files'] + t['conditional_files'] + t['on_demand_files']}** | **{t['grand_total_tokens']:,}** |")
        lines.append(f"| Из них фактически загружено в этой сессии (always + invoked agents) | — | **{t['always_loaded_tokens'] + invoked_tokens:,}** |")
        lines.append("")

        lines.append("### Always loaded (грузится в каждой сессии)")
        lines.append("")
        lines.append("| Файл | Токены |")
        lines.append("|------|-------:|")
        for path, tk_ in sorted(gh["always_loaded"], key=lambda x: -x[1]):
            lines.append(f"| `{path}` | {tk_:,} |")
        lines.append("")

        if gh["conditional"]:
            lines.append("### Conditional (загружается при работе с файлом по applyTo)")
            lines.append("")
            lines.append("| Файл | applyTo | Токены |")
            lines.append("|------|---------|-------:|")
            for path, tk_, ap in sorted(gh["conditional"], key=lambda x: -x[1]):
                lines.append(f"| `{path}` | `{ap}` | {tk_:,} |")
            lines.append("")

        # On-demand breakdown
        by_kind: dict[str, list[tuple[str, int]]] = defaultdict(list)
        for path, tk_, kind in gh["on_demand"]:
            by_kind[kind].append((path, tk_))
        for kind in ("agent", "skill", "prompt"):
            items = by_kind.get(kind, [])
            if not items:
                continue
            kind_total = sum(t for _, t in items)
            lines.append(f"### On-demand: {kind}s ({len(items)} файлов, {kind_total:,} токенов потенциал)")
            lines.append("")
            lines.append("| Файл | Токены | Вызывался в этой сессии |")
            lines.append("|------|-------:|:-----------------------:|")
            for path, tk_ in sorted(items, key=lambda x: -x[1]):
                hit = "—"
                if kind == "agent":
                    name = Path(path).name.replace(".agent.md", "")
                    if name in invoked:
                        hit = "✅"
                lines.append(f"| `{path}` | {tk_:,} | {hit} |")
            lines.append("")


    lines.append("## Топ-инструментов")
    lines.append("")
    lines.append("| Tool | Calls |")
    lines.append("|------|-------|")
    for name, cnt in stats["tool_counter"].most_common(20):
        lines.append(f"| `{name}` | {cnt} |")
    lines.append("")

    lines.append("## Сообщения пользователя")
    lines.append("")
    for i, (ts, content) in enumerate(stats["user_messages"], 1):
        ts_s = ts.strftime("%H:%M:%S") if ts else "?"
        lines.append(f"### #{i} [{ts_s}]")
        lines.append("")
        lines.append("```")
        lines.append(short(content, 1200))
        lines.append("```")
        lines.append("")

    lines.append("## Цепочка рассуждений (reasoning)")
    lines.append("")
    rcnt = 0
    for ts, content, reasoning in stats["assistant_messages"]:
        if not reasoning.strip():
            continue
        rcnt += 1
        ts_s = ts.strftime("%H:%M:%S") if ts else "?"
        lines.append(f"- **[{ts_s}]** {short(reasoning, 500)}")
    if rcnt == 0:
        lines.append("_(reasoning не зафиксирован в транскрипте)_")
    lines.append("")

    lines.append("## Хронология вызовов инструментов")
    lines.append("")
    for tid in stats["tool_order"]:
        t = stats["tool_calls_by_id"][tid]
        ts_s = t["start"].strftime("%H:%M:%S") if t["start"] else "?"
        dur = ""
        if t["start"] and t["end"]:
            d = (t["end"] - t["start"]).total_seconds()
            dur = f" ({d:.1f}s)"
        ok = "✅" if t["success"] else ("❌" if t["success"] is False else "…")
        argstr = args_summary(t["args"])
        lines.append(f"- [{ts_s}] {ok} `{t['name']}`{dur} — {argstr}")
    lines.append("")

    if stats["errors"]:
        lines.append("## Ошибки и проблемы")
        lines.append("")
        for e in stats["errors"]:
            ts_s = e["ts"].strftime("%H:%M:%S") if e["ts"] else "?"
            lines.append(f"- **[{ts_s}]** `{e['tool']}` ({e['args']})")
            lines.append(f"  - error: {short(str(e['error']), 300)}")
        lines.append("")

    if stats["files_edited"]:
        lines.append("## Изменённые файлы")
        lines.append("")
        for p in stats["files_edited"]:
            lines.append(f"- `{p}`")
        lines.append("")

    if stats["files_read"]:
        lines.append("## Прочитанные файлы")
        lines.append("")
        for p in stats["files_read"][:50]:
            lines.append(f"- `{p}`")
        if len(stats["files_read"]) > 50:
            lines.append(f"- _... ещё {len(stats['files_read']) - 50}_")
        lines.append("")

    if stats["terminal_cmds"]:
        lines.append("## Терминальные команды")
        lines.append("")
        for c in stats["terminal_cmds"]:
            lines.append(f"- `{short(c, 200)}`")
        lines.append("")

    if stats["subagent_calls"]:
        lines.append("## Вызовы субагентов")
        lines.append("")
        for s in stats["subagent_calls"]:
            ts_s = s["ts"].strftime("%H:%M:%S") if s["ts"] else "?"
            lines.append(f"- **[{ts_s}]** `{s['agent']}` — {s['description']}")
            if s["prompt"]:
                lines.append(f"  - prompt: {s['prompt']}")
        lines.append("")

    if stats["traces"]:
        lines.append("## Trace-блоки субагентов")
        lines.append("")
        for tr in stats["traces"]:
            f = tr["fields"]
            ts_s = tr["ts"].strftime("%H:%M:%S") if tr["ts"] else "?"
            lines.append(f"### [{ts_s}] {f.get('agent', '?')} — {f.get('outcome', '?')}")
            if f.get("task"):
                lines.append(f"- task: {short(f['task'], 200)}")
            for a in tr["actions"]:
                lines.append(f"  - [{a['time']}] **{a['kind']}** {short(a['text'], 200)}")
            lines.append("")

    if stats["decisions"]:
        lines.append("## Ключевые решения (DECISION)")
        lines.append("")
        for ts, agent, text in stats["decisions"]:
            ts_s = ts.strftime("%H:%M:%S") if ts else "?"
            lines.append(f"- **[{ts_s}]** ({agent}) {short(text, 250)}")
        lines.append("")

    if stats["phase_events"]:
        lines.append("## Переходы между фазами (PHASE)")
        lines.append("")
        for ts, agent, text in stats["phase_events"]:
            ts_s = ts.strftime("%H:%M:%S") if ts else "?"
            lines.append(f"- **[{ts_s}]** ({agent}) {short(text, 200)}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("_Сгенерировано `scripts/parse_session.py`_")
    return "\n".join(lines)


def safe_filename(s: str) -> str:
    s = re.sub(r"[^\w\-А-Яа-яЁё]+", "_", s).strip("_")
    return s[:80] or "session"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--file", type=Path, help="Path to JSONL transcript")
    p.add_argument("--last", action="store_true", help="Use latest transcript")
    p.add_argument("--session", help="Session ID (matches filename)")
    p.add_argument("--task", default="", help="Short task name for output filename")
    p.add_argument("--task-link", default="", help="Vault path to plan, e.g. 'Dev/Tasks/Done/2026-05-06_имя' (становится [[wiki-link]])")
    p.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    p.add_argument("--stdout", action="store_true", help="Print to stdout instead of file")
    args = p.parse_args()

    if args.file:
        path = args.file
    elif args.session:
        path = TRANSCRIPTS_DIR / f"{args.session}.jsonl"
    elif args.last:
        path = find_latest_transcript()
    else:
        path = find_latest_transcript()

    if not path.exists():
        sys.exit(f"Transcript not found: {path}")

    events = load_events(path)
    stats = analyse(events)
    md = to_markdown(stats, path, args.task, args.task_link)

    if args.stdout:
        print(md)
        return 0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    started = stats["started"] or datetime.now()
    # Имя файла: YYYY-MM-DD_HHMM__closer__<task>.md (новый регламент §8)
    fname = f"{started.strftime('%Y-%m-%d_%H%M')}__closer__{safe_filename(args.task or path.stem)}.md"
    out = args.output_dir / fname
    out.write_text(md, encoding="utf-8")
    print(f"Written: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
