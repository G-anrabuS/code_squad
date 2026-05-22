from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any, Dict


TASK_TTL = timedelta(hours=1)
TASK_STEPS = ["scan", "summary", "judge", "architect", "performance", "security"]
TASK_STATUS: Dict[str, Dict[str, Any]] = {}


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _default_steps() -> Dict[str, str]:
    return {step: "pending" for step in TASK_STEPS}


def _cleanup_expired_tasks() -> None:
    cutoff = datetime.utcnow() - TASK_TTL
    expired = []
    for task_id, task in TASK_STATUS.items():
        created_at = task.get("created_at")
        if not created_at:
            continue
        try:
            created_at_dt = datetime.fromisoformat(created_at)
        except ValueError:
            expired.append(task_id)
            continue
        if created_at_dt < cutoff:
            expired.append(task_id)

    for task_id in expired:
        TASK_STATUS.pop(task_id, None)


def create_task(task_id: str, repo_name: str) -> Dict[str, Any]:
    _cleanup_expired_tasks()
    task = {
        "status": "pending",
        "repo_name": repo_name,
        "created_at": _now_iso(),
        "steps": _default_steps(),
        "step_errors": {},
        "message": None,
        "data": None,
    }
    TASK_STATUS[task_id] = task
    return deepcopy(task)


def get_task(task_id: str) -> Dict[str, Any] | None:
    _cleanup_expired_tasks()
    task = TASK_STATUS.get(task_id)
    return deepcopy(task) if task else None


def set_task_status(task_id: str, status: str, message: str | None = None) -> None:
    task = TASK_STATUS.get(task_id)
    if not task:
        return
    task["status"] = status
    if message is not None:
        task["message"] = message


def update_step(
    task_id: str,
    step: str,
    status: str,
    message: str | None = None,
) -> None:
    task = TASK_STATUS.get(task_id)
    if not task or step not in task["steps"]:
        return
    task["steps"][step] = status
    if message:
        task["step_errors"][step] = message
        task["message"] = message
    elif status == "completed":
        task["step_errors"].pop(step, None)


def complete_task(task_id: str, data: Dict[str, Any]) -> None:
    task = TASK_STATUS.get(task_id)
    if not task:
        return
    task["status"] = "completed"
    task["data"] = data
    task["message"] = None


def fail_task(task_id: str, message: str) -> None:
    task = TASK_STATUS.get(task_id)
    if not task:
        return
    task["status"] = "failed"
    task["message"] = message
