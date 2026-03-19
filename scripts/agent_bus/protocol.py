"""
Agent Bus Protocol — dataclasses и константы протокола.
Используется оркестратором и всеми агентами.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional


class TaskStatus(str, Enum):
    PENDING   = "pending"
    ACTIVE    = "active"
    PAUSED    = "paused"
    DONE      = "done"
    FAILED    = "failed"
    CANCELLED = "cancelled"
    BLOCKED   = "blocked"     # зависимости не выполнены


class AgentStatus(str, Enum):
    IDLE    = "idle"
    WORKING = "working"
    PAUSED  = "paused"
    STOPPED = "stopped"
    ERROR   = "error"
    OFFLINE = "offline"


class CommandType(str, Enum):
    PAUSE           = "pause"
    RESUME          = "resume"
    STOP            = "stop"
    CANCEL_TASK     = "cancel_task"
    PRIORITY_OVERRIDE = "priority_override"
    CONTEXT_SYNC    = "context_sync"


class TaskType(str, Enum):
    IMPLEMENT  = "implement"
    REVIEW     = "review"
    TEST       = "test"
    ANALYZE    = "analyze"
    REFACTOR   = "refactor"
    DOCUMENT   = "document"
    DEPLOY     = "deploy"
    FIX        = "fix"


@dataclass
class TaskCommand:
    type: TaskType
    title: str
    description: str
    acceptance_criteria: List[str] = field(default_factory=list)
    files_scope: List[str] = field(default_factory=list)
    branch: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    blocks: List[str] = field(default_factory=list)
    estimated_minutes: int = 30
    context: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "type": self.type.value if isinstance(self.type, TaskType) else self.type,
            "title": self.title,
            "description": self.description,
            "acceptance_criteria": self.acceptance_criteria,
            "files_scope": self.files_scope,
            "branch": self.branch,
            "constraints": self.constraints,
            "depends_on": self.depends_on,
            "blocks": self.blocks,
            "estimated_minutes": self.estimated_minutes,
            "context": self.context,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "TaskCommand":
        return cls(
            type=d.get("type", TaskType.IMPLEMENT),
            title=d.get("title", ""),
            description=d.get("description", ""),
            acceptance_criteria=d.get("acceptance_criteria", []),
            files_scope=d.get("files_scope", []),
            branch=d.get("branch"),
            constraints=d.get("constraints", []),
            depends_on=d.get("depends_on", []),
            blocks=d.get("blocks", []),
            estimated_minutes=d.get("estimated_minutes", 30),
            context=d.get("context", {}),
        )


@dataclass
class Task:
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    priority: int = 3            # 1=highest, 5=lowest
    direction: str = "general"   # frontend/backend/tests/docs/infra
    assigned_to: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    command: Optional[TaskCommand] = None
    result: Optional[dict] = None
    error: Optional[str] = None
    metrics: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "priority": self.priority,
            "direction": self.direction,
            "assigned_to": self.assigned_to,
            "status": self.status.value if isinstance(self.status, TaskStatus) else self.status,
            "command": self.command.to_dict() if self.command else None,
            "result": self.result,
            "error": self.error,
            "metrics": self.metrics,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Task":
        t = cls(
            task_id=d.get("task_id", str(uuid.uuid4())),
            created_at=d.get("created_at", datetime.utcnow().isoformat() + "Z"),
            updated_at=d.get("updated_at", datetime.utcnow().isoformat() + "Z"),
            priority=d.get("priority", 3),
            direction=d.get("direction", "general"),
            assigned_to=d.get("assigned_to"),
            status=TaskStatus(d.get("status", "pending")),
            result=d.get("result"),
            error=d.get("error"),
            metrics=d.get("metrics", {}),
        )
        if d.get("command"):
            t.command = TaskCommand.from_dict(d["command"])
        return t


@dataclass
class AgentState:
    agent_id: str
    direction: str
    status: AgentStatus = AgentStatus.IDLE
    last_heartbeat: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    current_task_id: Optional[str] = None
    completed_tasks: int = 0
    failed_tasks: int = 0
    capabilities: List[str] = field(default_factory=list)
    context_window_used: float = 0.0
    machine: str = "unknown"
    version: str = "1.0.0"

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "direction": self.direction,
            "status": self.status.value if isinstance(self.status, AgentStatus) else self.status,
            "last_heartbeat": self.last_heartbeat,
            "current_task_id": self.current_task_id,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "capabilities": self.capabilities,
            "context_window_used": self.context_window_used,
            "machine": self.machine,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "AgentState":
        return cls(
            agent_id=d.get("agent_id", ""),
            direction=d.get("direction", "general"),
            status=AgentStatus(d.get("status", "idle")),
            last_heartbeat=d.get("last_heartbeat", datetime.utcnow().isoformat() + "Z"),
            current_task_id=d.get("current_task_id"),
            completed_tasks=d.get("completed_tasks", 0),
            failed_tasks=d.get("failed_tasks", 0),
            capabilities=d.get("capabilities", []),
            context_window_used=d.get("context_window_used", 0.0),
            machine=d.get("machine", "unknown"),
            version=d.get("version", "1.0.0"),
        )


@dataclass
class OrchestratorCommand:
    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    type: CommandType = CommandType.PAUSE
    reason: str = ""
    payload: dict = field(default_factory=dict)
    acknowledged: bool = False

    def to_dict(self) -> dict:
        return {
            "command_id": self.command_id,
            "timestamp": self.timestamp,
            "type": self.type.value if isinstance(self.type, CommandType) else self.type,
            "reason": self.reason,
            "payload": self.payload,
            "acknowledged": self.acknowledged,
        }
