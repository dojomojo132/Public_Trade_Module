"""
TaskBus — ядро системы агентного взаимодействия.

Транспорт: SQLite (atomic) + файловая система для контекста задач.
Работает: локально, по SMB/NFS (общая папка), или указать путь к базе.

Использование:
    bus = TaskBus(bus_dir="path/to/shared/folder")
    bus.publish_task(task)
    task = bus.claim_next_task(agent_id="agent-1", direction="frontend")
"""
from __future__ import annotations

import json
import logging
import os
import platform
import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from .protocol import (
    AgentState, AgentStatus, OrchestratorCommand, CommandType,
    Task, TaskStatus,
)

log = logging.getLogger("agent_bus.bus")

# ─── Константы ────────────────────────────────────────────────────────────────
DB_FILENAME     = "bus.db"
TASKS_DIR       = "tasks"       # JSON-контексты задач (для агентов)
RESULTS_DIR     = "results"     # JSON-результаты (для оркестратора)
OFFLINE_TIMEOUT = 300           # сек: если heartbeat старше — агент offline
STUCK_MULTIPLIER = 2.0          # во сколько раз дольше estimated → задача зависла


# ─── TaskBus ──────────────────────────────────────────────────────────────────
class TaskBus:
    """
    Центральная шина задач. Потокобезопасна (threading.Lock + SQLite WAL).
    Можно создать несколько экземпляров — они сходятся через одну БД.
    """

    def __init__(self, bus_dir: str | Path = ".agent-bus"):
        self.bus_dir  = Path(bus_dir)
        self.db_path  = self.bus_dir / DB_FILENAME
        self.tasks_dir   = self.bus_dir / TASKS_DIR
        self.results_dir = self.bus_dir / RESULTS_DIR
        self._lock = threading.Lock()

        self._ensure_dirs()
        self._init_db()

    # ── Инициализация ─────────────────────────────────────────────────────────
    def _ensure_dirs(self):
        for d in [self.bus_dir, self.tasks_dir, self.results_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def _init_db(self):
        with self._conn() as conn:
            conn.executescript("""
                PRAGMA journal_mode=WAL;
                PRAGMA synchronous=NORMAL;

                CREATE TABLE IF NOT EXISTS tasks (
                    task_id         TEXT PRIMARY KEY,
                    direction       TEXT NOT NULL DEFAULT 'general',
                    priority        INTEGER NOT NULL DEFAULT 3,
                    status          TEXT NOT NULL DEFAULT 'pending',
                    assigned_to     TEXT,
                    created_at      TEXT,
                    updated_at      TEXT,
                    estimated_minutes INTEGER DEFAULT 30,
                    depends_on      TEXT DEFAULT '[]',
                    blocks          TEXT DEFAULT '[]',
                    retry_count     INTEGER DEFAULT 0,
                    max_retries     INTEGER DEFAULT 2,
                    payload         TEXT DEFAULT '{}'
                );

                CREATE TABLE IF NOT EXISTS agent_states (
                    agent_id        TEXT PRIMARY KEY,
                    direction       TEXT,
                    status          TEXT DEFAULT 'idle',
                    last_heartbeat  TEXT,
                    current_task_id TEXT,
                    completed_tasks INTEGER DEFAULT 0,
                    failed_tasks    INTEGER DEFAULT 0,
                    capabilities    TEXT DEFAULT '[]',
                    context_window_used REAL DEFAULT 0.0,
                    machine         TEXT DEFAULT 'unknown',
                    payload         TEXT DEFAULT '{}'
                );

                CREATE TABLE IF NOT EXISTS inbox (
                    command_id  TEXT PRIMARY KEY,
                    agent_id    TEXT NOT NULL,
                    timestamp   TEXT,
                    type        TEXT,
                    reason      TEXT DEFAULT '',
                    payload     TEXT DEFAULT '{}',
                    acknowledged INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS results (
                    task_id     TEXT PRIMARY KEY,
                    agent_id    TEXT,
                    finished_at TEXT,
                    success     INTEGER DEFAULT 1,
                    payload     TEXT DEFAULT '{}'
                );

                CREATE INDEX IF NOT EXISTS idx_tasks_status    ON tasks(status);
                CREATE INDEX IF NOT EXISTS idx_tasks_direction ON tasks(direction, status);
                CREATE INDEX IF NOT EXISTS idx_inbox_agent     ON inbox(agent_id, acknowledged);
            """)

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(str(self.db_path), timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ── Управление задачами ───────────────────────────────────────────────────
    def publish_task(self, task: Task, max_retries: int = 2) -> str:
        """Оркестратор публикует новую задачу."""
        now = _now()
        depends_on = task.command.depends_on if task.command else []
        blocks     = task.command.blocks if task.command else []
        estimated  = task.command.estimated_minutes if task.command else 30

        # Если есть незавершённые зависимости — сразу BLOCKED
        status = task.status
        if depends_on and self._has_unfinished_deps(depends_on):
            status = TaskStatus.BLOCKED

        with self._lock, self._conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO tasks
                (task_id, direction, priority, status, assigned_to,
                 created_at, updated_at, estimated_minutes, depends_on, blocks,
                 retry_count, max_retries, payload)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                task.task_id,
                task.direction,
                task.priority,
                status.value,
                task.assigned_to,
                task.created_at or now,
                now,
                estimated,
                json.dumps(depends_on),
                json.dumps(blocks),
                0,          # retry_count
                max_retries,
                json.dumps(task.to_dict()),
            ))

        # Сохранить полный контекст задачи в файл (для агента)
        task_file = self.tasks_dir / f"{task.task_id}.json"
        task_file.write_text(json.dumps(task.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        log.info("Published task %s [%s] → %s", task.task_id, task.direction, status.value)
        return task.task_id

    def claim_next_task(self, agent_id: str, direction: str) -> Optional[Task]:
        """
        Агент атомарно берёт первую доступную задачу своего направления.
        Возвращает Task или None если очередь пуста.
        """
        with self._lock, self._conn() as conn:
            row = conn.execute("""
                SELECT task_id, payload FROM tasks
                WHERE direction = ? AND status = 'pending'
                ORDER BY priority ASC, created_at ASC
                LIMIT 1
            """, (direction,)).fetchone()

            if not row:
                return None

            task_id = row["task_id"]
            conn.execute("""
                UPDATE tasks SET status='active', assigned_to=?, updated_at=?
                WHERE task_id=? AND status='pending'
            """, (agent_id, _now(), task_id))

        task_data = json.loads(row["payload"])
        task_data["status"]      = TaskStatus.ACTIVE.value
        task_data["assigned_to"] = agent_id
        log.info("Agent %s claimed task %s", agent_id, task_id)
        return Task.from_dict(task_data)

    def complete_task(self, task_id: str, agent_id: str, result: dict) -> None:
        """Агент сообщает успешное завершение."""
        now = _now()
        with self._lock, self._conn() as conn:
            conn.execute("""
                UPDATE tasks SET status='done', updated_at=? WHERE task_id=?
            """, (now, task_id))
            conn.execute("""
                INSERT OR REPLACE INTO results (task_id, agent_id, finished_at, success, payload)
                VALUES (?,?,?,1,?)
            """, (task_id, agent_id, now, json.dumps(result)))
            conn.execute("""
                UPDATE agent_states SET status='idle', current_task_id=NULL,
                completed_tasks=completed_tasks+1, last_heartbeat=?
                WHERE agent_id=?
            """, (now, agent_id))

        # Сохранить результат в файл
        result_file = self.results_dir / f"{task_id}.json"
        result_file.write_text(json.dumps({
            "task_id": task_id, "agent_id": agent_id,
            "finished_at": now, "success": True, "result": result,
        }, ensure_ascii=False, indent=2), encoding="utf-8")

        # Разблокировать зависимые задачи
        self._unblock_dependents(task_id)
        log.info("Task %s completed by %s", task_id, agent_id)

    def fail_task(self, task_id: str, agent_id: str, error: str) -> None:
        """Агент сообщает об ошибке. Автоматический ретрай если не исчерпаны попытки."""
        now = _now()
        with self._lock, self._conn() as conn:
            row = conn.execute(
                "SELECT retry_count, max_retries FROM tasks WHERE task_id=?", (task_id,)
            ).fetchone()
            retry_count = (row["retry_count"] if row else 0) + 1
            max_retries = row["max_retries"] if row else 2

            if retry_count <= max_retries:
                # Ещё есть попытки — вернуть в pending
                conn.execute("""
                    UPDATE tasks SET status='pending', assigned_to=NULL,
                    updated_at=?, retry_count=?
                    WHERE task_id=?
                """, (now, retry_count, task_id))
                log.warning("Task %s FAILED (attempt %d/%d) — retry in pending",
                            task_id, retry_count, max_retries + 1)
            else:
                # Попытки исчерпаны — окончательно failed
                conn.execute("""
                    UPDATE tasks SET status='failed', updated_at=? WHERE task_id=?
                """, (now, task_id))
                conn.execute("""
                    INSERT OR REPLACE INTO results (task_id, agent_id, finished_at, success, payload)
                    VALUES (?,?,?,0,?)
                """, (task_id, agent_id, now, json.dumps({"error": error, "attempts": retry_count})))
                log.error("Task %s PERMANENTLY FAILED after %d attempts: %s",
                          task_id, retry_count, error[:200])

            conn.execute("""
                UPDATE agent_states SET status='idle', current_task_id=NULL,
                failed_tasks=failed_tasks+1, last_heartbeat=?
                WHERE agent_id=?
            """, (now, agent_id))

    def reset_task_to_pending(self, task_id: str) -> None:
        """Вернуть задачу в очередь (при падении агента)."""
        with self._lock, self._conn() as conn:
            conn.execute("""
                UPDATE tasks SET status='pending', assigned_to=NULL, updated_at=?
                WHERE task_id=?
            """, (_now(), task_id))
        log.info("Task %s reset to pending", task_id)

    def cancel_task(self, task_id: str) -> None:
        """Оркестратор отменяет задачу."""
        with self._lock, self._conn() as conn:
            conn.execute("""
                UPDATE tasks SET status='cancelled', updated_at=? WHERE task_id=?
            """, (_now(), task_id))

    # ── Состояние агентов ─────────────────────────────────────────────────────
    def register_agent(self, agent: AgentState) -> None:
        """Агент регистрируется при старте."""
        with self._lock, self._conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO agent_states
                (agent_id, direction, status, last_heartbeat, current_task_id,
                 completed_tasks, failed_tasks, capabilities, context_window_used, machine, payload)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (
                agent.agent_id, agent.direction, agent.status.value,
                _now(), None, 0, 0,
                json.dumps(agent.capabilities), agent.context_window_used,
                agent.machine or platform.node(),
                json.dumps(agent.to_dict()),
            ))

    def heartbeat(self, agent_id: str, status: AgentStatus = AgentStatus.IDLE,
                  current_task_id: Optional[str] = None,
                  context_window_used: float = 0.0) -> None:
        """Агент отправляет heartbeat каждые N секунд."""
        with self._lock, self._conn() as conn:
            conn.execute("""
                UPDATE agent_states
                SET last_heartbeat=?, status=?, current_task_id=?, context_window_used=?
                WHERE agent_id=?
            """, (_now(), status.value, current_task_id, context_window_used, agent_id))

    def get_all_agents(self) -> List[AgentState]:
        with self._conn() as conn:
            rows = conn.execute("SELECT payload, last_heartbeat, status FROM agent_states").fetchall()
        agents = []
        for row in rows:
            a = AgentState.from_dict(json.loads(row["payload"]))
            a.last_heartbeat = row["last_heartbeat"]
            a.status = AgentStatus(row["status"])
            agents.append(a)
        return agents

    def get_agent(self, agent_id: str) -> Optional[AgentState]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT payload, last_heartbeat, status, current_task_id FROM agent_states WHERE agent_id=?",
                (agent_id,)
            ).fetchone()
        if not row:
            return None
        a = AgentState.from_dict(json.loads(row["payload"]))
        a.last_heartbeat = row["last_heartbeat"]
        a.status = AgentStatus(row["status"])
        a.current_task_id = row["current_task_id"]
        return a

    # ── Inbox (команды оркестратора → агентам) ────────────────────────────────
    def send_command(self, agent_id: str, cmd: OrchestratorCommand) -> None:
        """Оркестратор отправляет команду агенту."""
        with self._lock, self._conn() as conn:
            conn.execute("""
                INSERT INTO inbox (command_id, agent_id, timestamp, type, reason, payload, acknowledged)
                VALUES (?,?,?,?,?,?,0)
            """, (
                cmd.command_id, agent_id, cmd.timestamp,
                cmd.type.value if isinstance(cmd.type, CommandType) else cmd.type,
                cmd.reason, json.dumps(cmd.payload),
            ))
        log.info("Command %s → agent %s", cmd.type, agent_id)

    def read_inbox(self, agent_id: str) -> List[OrchestratorCommand]:
        """Агент читает непрочитанные команды. Автоматически помечает как acknowledged."""
        with self._lock, self._conn() as conn:
            rows = conn.execute("""
                SELECT command_id, timestamp, type, reason, payload
                FROM inbox WHERE agent_id=? AND acknowledged=0
                ORDER BY timestamp ASC
            """, (agent_id,)).fetchall()
            if rows:
                ids = [r["command_id"] for r in rows]
                conn.execute(
                    f"UPDATE inbox SET acknowledged=1 WHERE command_id IN ({','.join('?'*len(ids))})",
                    ids
                )
        cmds = []
        for r in rows:
            cmds.append(OrchestratorCommand(
                command_id=r["command_id"],
                timestamp=r["timestamp"],
                type=CommandType(r["type"]),
                reason=r["reason"],
                payload=json.loads(r["payload"]),
                acknowledged=True,
            ))
        return cmds

    # ── Запросы оркестратора ──────────────────────────────────────────────────
    def get_pending_tasks(self, direction: Optional[str] = None) -> List[dict]:
        query = "SELECT * FROM tasks WHERE status='pending'"
        params = ()
        if direction:
            query += " AND direction=?"
            params = (direction,)
        query += " ORDER BY priority ASC, created_at ASC"
        with self._conn() as conn:
            return [dict(r) for r in conn.execute(query, params).fetchall()]

    def get_active_tasks(self) -> List[dict]:
        with self._conn() as conn:
            return [dict(r) for r in conn.execute(
                "SELECT * FROM tasks WHERE status='active'"
            ).fetchall()]

    def get_done_tasks(self, since: Optional[str] = None) -> List[dict]:
        if since:
            with self._conn() as conn:
                return [dict(r) for r in conn.execute(
                    "SELECT * FROM tasks WHERE status='done' AND updated_at>=?", (since,)
                ).fetchall()]
        with self._conn() as conn:
            return [dict(r) for r in conn.execute(
                "SELECT * FROM tasks WHERE status='done'"
            ).fetchall()]

    def get_stuck_tasks(self) -> List[dict]:
        """Задачи, которые активны дольше estimated_minutes * STUCK_MULTIPLIER."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE status='active'"
            ).fetchall()
        stuck = []
        for row in rows:
            row = dict(row)
            updated = datetime.fromisoformat(row["updated_at"].rstrip("Z"))
            limit   = timedelta(minutes=row["estimated_minutes"] * STUCK_MULTIPLIER)
            if datetime.utcnow() - updated > limit:
                stuck.append(row)
        return stuck

    def get_offline_agents(self) -> List[AgentState]:
        agents = self.get_all_agents()
        offline = []
        for a in agents:
            try:
                hb = datetime.fromisoformat(a.last_heartbeat.rstrip("Z"))
                if datetime.utcnow() - hb > timedelta(seconds=OFFLINE_TIMEOUT):
                    offline.append(a)
            except (ValueError, AttributeError):
                offline.append(a)
        return offline

    def get_project_snapshot(self) -> dict:
        """Полный снапшот состояния проекта для оркестратора."""
        with self._conn() as conn:
            task_rows  = [dict(r) for r in conn.execute("SELECT * FROM tasks").fetchall()]
            agent_rows = [dict(r) for r in conn.execute("SELECT * FROM agent_states").fetchall()]
        return {
            "timestamp": _now(),
            "tasks": {
                "total":     len(task_rows),
                "pending":   sum(1 for t in task_rows if t["status"] == "pending"),
                "active":    sum(1 for t in task_rows if t["status"] == "active"),
                "done":      sum(1 for t in task_rows if t["status"] == "done"),
                "failed":    sum(1 for t in task_rows if t["status"] == "failed"),
                "blocked":   sum(1 for t in task_rows if t["status"] == "blocked"),
                "cancelled": sum(1 for t in task_rows if t["status"] == "cancelled"),
            },
            "agents": {
                a["agent_id"]: {
                    "direction":       a["direction"],
                    "status":          a["status"],
                    "current_task_id": a["current_task_id"],
                    "completed":       a["completed_tasks"],
                    "failed":          a["failed_tasks"],
                }
                for a in agent_rows
            },
            "task_list": task_rows,
        }

    # ── Внутренние методы ─────────────────────────────────────────────────────
    def _has_unfinished_deps(self, depends_on: List[str]) -> bool:
        if not depends_on:
            return False
        with self._conn() as conn:
            rows = conn.execute(
                f"SELECT status FROM tasks WHERE task_id IN ({','.join('?'*len(depends_on))})",
                depends_on
            ).fetchall()
        return any(r["status"] != "done" for r in rows)

    def _unblock_dependents(self, done_task_id: str) -> None:
        """После завершения задачи разблокировать те, что ждали её."""
        with self._conn() as conn:
            # Найти все blocked задачи
            blocked_rows = conn.execute(
                "SELECT task_id, depends_on FROM tasks WHERE status='blocked'"
            ).fetchall()

            # Получить все done task_id одним запросом (без вложенных соединений)
            done_ids = {r["task_id"] for r in conn.execute(
                "SELECT task_id FROM tasks WHERE status='done'"
            ).fetchall()}
            done_ids.add(done_task_id)  # только что завершённая

            for row in blocked_rows:
                deps = json.loads(row["depends_on"] or "[]")
                if done_task_id in deps:
                    # Все зависимости выполнены?
                    if all(d in done_ids for d in deps):
                        conn.execute("""
                            UPDATE tasks SET status='pending', updated_at=? WHERE task_id=?
                        """, (_now(), row["task_id"]))
                        log.info("Task %s unblocked (dep %s done)", row["task_id"], done_task_id)


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"
