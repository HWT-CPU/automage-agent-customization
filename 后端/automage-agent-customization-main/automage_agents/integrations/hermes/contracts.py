from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from automage_agents.core.models import SkillResult


@dataclass(slots=True)
class HermesTrace:
    run_id: str = field(default_factory=lambda: f"hermes-run-{uuid4()}")
    trace_id: str = field(default_factory=lambda: f"hermes-trace-{uuid4()}")
    correlation_id: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now().astimezone().isoformat())


@dataclass(slots=True)
class HermesInvokeRequest:
    skill_name: str
    actor_user_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    trace: HermesTrace = field(default_factory=HermesTrace)


@dataclass(slots=True)
class HermesInvokeResponse:
    ok: bool
    skill_name: str
    actor_user_id: str
    result: SkillResult
    trace: HermesTrace

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "skill_name": self.skill_name,
            "actor_user_id": self.actor_user_id,
            "trace": {
                "run_id": self.trace.run_id,
                "trace_id": self.trace.trace_id,
                "correlation_id": self.trace.correlation_id,
                "created_at": self.trace.created_at,
            },
            "result": {
                "ok": self.result.ok,
                "message": self.result.message,
                "error_code": self.result.error_code,
                "data": self.result.data,
            },
        }
