from __future__ import annotations

from functools import lru_cache
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from automage_agents.integrations.hermes import HermesOpenClawRuntime
from automage_agents.integrations.hermes.contracts import HermesInvokeRequest, HermesTrace
from automage_agents.skills.registry import SKILL_REGISTRY


class HermesTracePayload(BaseModel):
    run_id: str | None = None
    trace_id: str | None = None
    correlation_id: str | None = None
    created_at: str | None = None


class HermesSkillInvokeRequest(BaseModel):
    actor_user_id: str = Field(default="user-001")
    payload: dict[str, Any] = Field(default_factory=dict)
    trace: HermesTracePayload | None = None


class HermesSkillInvokeEnvelope(BaseModel):
    ok: bool
    skill_name: str
    actor_user_id: str
    trace: dict[str, Any]
    result: dict[str, Any]


router = APIRouter(prefix="/hermes", tags=["Hermes Skill Server"])


@lru_cache(maxsize=1)
def get_hermes_runtime() -> HermesOpenClawRuntime:
    return HermesOpenClawRuntime.from_config_files(
        hermes_config_path="configs/hermes.example.toml",
        openclaw_config_path="configs/openclaw.example.toml",
        user_mapping={"staff-open-id": "user-001", "manager-open-id": "manager-001", "executive-open-id": "executive-001"},
    )


@router.get("/healthz", summary="Hermes Skill Server 健康检查")
def hermes_healthz() -> dict[str, Any]:
    runtime = get_hermes_runtime()
    return {
        "status": "ok",
        "mode": "http_skill_server",
        "skill_count": len(SKILL_REGISTRY),
        "state": runtime.state_summary(),
    }


@router.get("/skills", summary="列出 AutoMage 可供 Hermes 调用的 Skill")
def list_hermes_skills() -> dict[str, Any]:
    return {
        "ok": True,
        "skills": [
            {
                "name": name,
                "transport": "http",
                "invoke_url": f"/hermes/skills/{name}/invoke",
            }
            for name in sorted(SKILL_REGISTRY)
        ],
    }


@router.post("/skills/{skill_name}/invoke", response_model=HermesSkillInvokeEnvelope, summary="调用 AutoMage Hermes Skill")
def invoke_hermes_skill(skill_name: str, request: HermesSkillInvokeRequest) -> dict[str, Any]:
    if skill_name not in SKILL_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Unknown Hermes skill: {skill_name}")
    runtime = get_hermes_runtime()
    if runtime.hermes_client is None:
        raise HTTPException(status_code=500, detail="Hermes client was not initialized")
    trace = _build_trace(request.trace)
    response = runtime.hermes_client.invoke_skill(
        HermesInvokeRequest(
            skill_name=skill_name,
            actor_user_id=request.actor_user_id,
            payload=request.payload,
            trace=trace,
        )
    )
    return response.to_dict()


def _build_trace(payload: HermesTracePayload | None) -> HermesTrace:
    trace = HermesTrace()
    if payload is None:
        return trace
    if payload.run_id:
        trace.run_id = payload.run_id
    if payload.trace_id:
        trace.trace_id = payload.trace_id
    if payload.correlation_id:
        trace.correlation_id = payload.correlation_id
    if payload.created_at:
        trace.created_at = payload.created_at
    return trace
