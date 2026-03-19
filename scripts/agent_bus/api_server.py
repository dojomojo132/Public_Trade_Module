"""
API Server — REST-шина для кросс-интернет сценария (Уровень 3).

Требует: pip install fastapi uvicorn

Запуск (на машине оркестратора):
    python -m scripts.agent_bus.api_server --bus-dir .agent-bus --port 8765

Агенты на удалённых PC подключаются через URL:
    python -m scripts.agent_bus.agent_worker \
        --agent-id agent-2 \
        --direction backend \
        --bus-url http://192.168.1.100:8765   # или через Tailscale/ngrok

Для безопасности в продакшне:
    - Добавить Bearer токен (API_KEY в env)
    - Поставить за nginx с TLS
    - Или использовать Tailscale (без публичного IP)
"""
from __future__ import annotations

import argparse
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from fastapi import FastAPI, HTTPException, Depends, Header
    from fastapi.responses import JSONResponse
    import uvicorn
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

from .bus import TaskBus
from .protocol import (
    AgentState, AgentStatus, CommandType,
    OrchestratorCommand, Task, TaskStatus,
)

log = logging.getLogger("agent_bus.api")

# ── Простая API-ключевая аутентификация ───────────────────────────────────────
API_KEY = os.environ.get("AGENT_BUS_API_KEY", "")   # пустая строка = без auth


def _check_auth(x_api_key: Optional[str] = Header(default=None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


# ── Создание приложения ───────────────────────────────────────────────────────
def create_app(bus_dir: str | Path = ".agent-bus") -> "FastAPI":
    if not HAS_FASTAPI:
        raise ImportError("fastapi and uvicorn required: pip install fastapi uvicorn")

    app  = FastAPI(title="Agent Bus API", version="1.0.0")
    bus  = TaskBus(bus_dir)
    auth = Depends(_check_auth)

    # ── Tasks ─────────────────────────────────────────────────────────────────
    @app.get("/api/tasks/next", dependencies=[auth])
    def get_next_task(agent_id: str, direction: str):
        """Агент запрашивает следующую задачу (atomic claim)."""
        task = bus.claim_next_task(agent_id=agent_id, direction=direction)
        if not task:
            return JSONResponse(content={"task": None}, status_code=200)
        return {"task": task.to_dict()}

    @app.post("/api/tasks/{task_id}/done", dependencies=[auth])
    def task_done(task_id: str, agent_id: str, result: dict):
        """Агент сообщает об успешном завершении."""
        bus.complete_task(task_id, agent_id, result)
        return {"ok": True}

    @app.post("/api/tasks/{task_id}/failed", dependencies=[auth])
    def task_failed(task_id: str, agent_id: str, error: str):
        """Агент сообщает об ошибке."""
        bus.fail_task(task_id, agent_id, error)
        return {"ok": True}

    @app.post("/api/tasks/publish", dependencies=[auth])
    def publish_task(task_data: dict):
        """Оркестратор публикует задачу."""
        task = Task.from_dict(task_data)
        tid  = bus.publish_task(task)
        return {"task_id": tid}

    @app.get("/api/tasks", dependencies=[auth])
    def list_tasks(status: Optional[str] = None, direction: Optional[str] = None):
        snap = bus.get_project_snapshot()
        tasks = snap["task_list"]
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        if direction:
            tasks = [t for t in tasks if t["direction"] == direction]
        return {"tasks": tasks}

    # ── Agents ────────────────────────────────────────────────────────────────
    @app.post("/api/agents/heartbeat", dependencies=[auth])
    def heartbeat(agent_id: str, status: str = "idle",
                  current_task_id: Optional[str] = None,
                  context_window_used: float = 0.0):
        """Агент отправляет heartbeat."""
        bus.heartbeat(
            agent_id=agent_id,
            status=AgentStatus(status),
            current_task_id=current_task_id,
            context_window_used=context_window_used,
        )
        return {"ok": True, "timestamp": datetime.utcnow().isoformat() + "Z"}

    @app.post("/api/agents/register", dependencies=[auth])
    def register_agent(agent_data: dict):
        """Агент регистрируется в шине."""
        agent = AgentState.from_dict(agent_data)
        bus.register_agent(agent)
        return {"ok": True}

    @app.get("/api/agents", dependencies=[auth])
    def list_agents():
        agents = bus.get_all_agents()
        return {"agents": [a.to_dict() for a in agents]}

    # ── Inbox ─────────────────────────────────────────────────────────────────
    @app.get("/api/agents/{agent_id}/inbox", dependencies=[auth])
    def read_inbox(agent_id: str):
        """Агент читает и одновременно подтверждает получение команд."""
        commands = bus.read_inbox(agent_id)
        return {"commands": [c.to_dict() for c in commands]}

    @app.post("/api/agents/{agent_id}/command", dependencies=[auth])
    def send_command(agent_id: str, cmd_data: dict):
        """Оркестратор отправляет команду агенту."""
        cmd = OrchestratorCommand(
            type=CommandType(cmd_data.get("type", "pause")),
            reason=cmd_data.get("reason", ""),
            payload=cmd_data.get("payload", {}),
        )
        bus.send_command(agent_id, cmd)
        return {"ok": True, "command_id": cmd.command_id}

    # ── Dashboard ─────────────────────────────────────────────────────────────
    @app.get("/api/snapshot", dependencies=[auth])
    def snapshot():
        """Полный снапшот состояния проекта."""
        return bus.get_project_snapshot()

    @app.get("/health")
    def health():
        return {"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"}

    return app


# ── HTTP-клиент для агентов (без FastAPI зависимости) ─────────────────────────
class BusHttpClient:
    """
    HTTP-клиент для подключения агента к REST-шине.
    Используется вместо TaskBus когда агент на другом ПК.

    bus = BusHttpClient(base_url="http://192.168.1.100:8765", api_key="secret")
    task = bus.claim_next_task(agent_id="agent-2", direction="backend")
    """

    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.headers  = {"Content-Type": "application/json"}
        if api_key:
            self.headers["X-Api-Key"] = api_key

    def _req(self, method: str, path: str, **kwargs):
        import urllib.request
        url  = f"{self.base_url}{path}"
        data = kwargs.get("json")
        body = json.dumps(data).encode() if data else None
        req  = urllib.request.Request(url, data=body,
                                      headers=self.headers, method=method.upper())
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except Exception as exc:
            log.error("HTTP %s %s → %s", method, path, exc)
            return None

    def claim_next_task(self, agent_id: str, direction: str) -> Optional[Task]:
        r = self._req("GET", f"/api/tasks/next?agent_id={agent_id}&direction={direction}")
        if r and r.get("task"):
            return Task.from_dict(r["task"])
        return None

    def complete_task(self, task_id: str, agent_id: str, result: dict) -> bool:
        r = self._req("POST", f"/api/tasks/{task_id}/done?agent_id={agent_id}", json=result)
        return bool(r and r.get("ok"))

    def fail_task(self, task_id: str, agent_id: str, error: str) -> bool:
        r = self._req("POST", f"/api/tasks/{task_id}/failed?agent_id={agent_id}",
                      json={"error": error})
        return bool(r and r.get("ok"))

    def heartbeat(self, agent_id: str, status: AgentStatus,
                  current_task_id: Optional[str] = None,
                  context_window_used: float = 0.0) -> bool:
        params = (f"?agent_id={agent_id}&status={status.value}"
                  f"&context_window_used={context_window_used}")
        if current_task_id:
            params += f"&current_task_id={current_task_id}"
        r = self._req("POST", f"/api/agents/heartbeat{params}")
        return bool(r and r.get("ok"))

    def register_agent(self, agent: AgentState) -> bool:
        r = self._req("POST", "/api/agents/register", json=agent.to_dict())
        return bool(r and r.get("ok"))

    def read_inbox(self, agent_id: str):
        from .protocol import OrchestratorCommand, CommandType
        r = self._req("GET", f"/api/agents/{agent_id}/inbox")
        if not r:
            return []
        return [OrchestratorCommand(
            command_id=c["command_id"],
            timestamp=c["timestamp"],
            type=CommandType(c["type"]),
            reason=c.get("reason", ""),
            payload=c.get("payload", {}),
        ) for c in r.get("commands", [])]


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Agent Bus REST API Server")
    parser.add_argument("--bus-dir", default=".agent-bus")
    parser.add_argument("--host",    default="0.0.0.0")
    parser.add_argument("--port",    default=8765, type=int)
    parser.add_argument("--api-key", default="",
                        help="Bearer token (рекомендуется для prod)")
    args = parser.parse_args()

    if args.api_key:
        os.environ["AGENT_BUS_API_KEY"] = args.api_key

    app = create_app(bus_dir=args.bus_dir)
    print(f"Agent Bus API started: http://{args.host}:{args.port}")
    print(f"Docs: http://{args.host}:{args.port}/docs")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
