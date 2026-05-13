from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from automage_agents.core.enums import RuntimeChannel
from automage_agents.integrations.hermes import HermesOpenClawRuntime
from automage_agents.integrations.openclaw import OpenClawEvent


class OpenClawMessageSender(BaseModel):
    id: str = Field(default="unknown-user")
    name: str | None = None


class OpenClawChannelMessage(BaseModel):
    id: str | None = None
    text: str = ""
    from_: OpenClawMessageSender = Field(default_factory=OpenClawMessageSender, alias="from")
    timestamp: int | None = None
    attachments: list[dict[str, Any]] = Field(default_factory=list)


class OpenClawChannelEventRequest(BaseModel):
    channel: str = Field(default="openclaw")
    accountId: str | None = None
    message: OpenClawChannelMessage
    payload: dict[str, Any] = Field(default_factory=dict)


router = APIRouter(prefix="/openclaw", tags=["OpenClaw HTTP Bridge"])

DEFAULT_USER_MAPPING = {"staff-open-id": "user-001", "manager-open-id": "manager-001", "executive-open-id": "executive-001"}
DEFAULT_USER_MAP_PATH = Path("configs/feishu_user_map.local.json")
DEFAULT_HERMES_CONFIG_PATH = Path("configs/hermes.example.toml")
DEFAULT_OPENCLAW_CONFIG_PATH = Path("configs/openclaw.example.toml")


@lru_cache(maxsize=1)
def get_openclaw_runtime() -> HermesOpenClawRuntime:
    hermes_config_path = _configured_path("AUTOMAGE_HERMES_CONFIG", "HERMES_CONFIG")
    openclaw_config_path = _configured_path("AUTOMAGE_OPENCLAW_CONFIG", "OPENCLAW_CONFIG") or DEFAULT_OPENCLAW_CONFIG_PATH
    if hermes_config_path:
        return HermesOpenClawRuntime.from_config_files(
            hermes_config_path=hermes_config_path,
            openclaw_config_path=openclaw_config_path,
            user_mapping=load_openclaw_user_mapping(),
        )
    return HermesOpenClawRuntime.from_config_files(
        hermes_config_path=DEFAULT_HERMES_CONFIG_PATH,
        openclaw_config_path=openclaw_config_path,
        user_mapping=load_openclaw_user_mapping(),
    )


def _configured_path(*env_names: str) -> str | Path | None:
    for env_name in env_names:
        value = os.getenv(env_name, "").strip()
        if value:
            return value
    return None


def load_openclaw_user_mapping(path: str | Path | None = None) -> dict[str, str]:
    mapping = dict(DEFAULT_USER_MAPPING)
    configured_path = path or os.getenv("AUTOMAGE_FEISHU_USER_MAP_JSON") or os.getenv("FEISHU_USER_MAP_JSON")
    mapping_path = Path(configured_path) if configured_path else DEFAULT_USER_MAP_PATH
    if not mapping_path.exists():
        return mapping
    raw = json.loads(mapping_path.read_text(encoding="utf-8-sig"))
    if not isinstance(raw, dict):
        raise ValueError(f"OpenClaw user mapping must be a JSON object: {mapping_path}")
    mapping.update({str(key): str(value) for key, value in raw.items()})
    return mapping


@router.get("/healthz", summary="OpenClaw HTTP Bridge 健康检查")
def openclaw_healthz() -> dict[str, Any]:
    runtime = get_openclaw_runtime()
    return {
        "status": "ok",
        "mode": "http_channel_bridge",
        "state": runtime.state_summary(),
    }


@router.post("/events", summary="接收真实 OpenClaw Channel 消息并转为 AutoMage Skill 调用")
def submit_openclaw_event(request: OpenClawChannelEventRequest) -> dict[str, Any]:
    runtime = get_openclaw_runtime()
    if runtime.openclaw_client is None:
        raise HTTPException(status_code=500, detail="OpenClaw client was not initialized")
    event = _to_openclaw_event(request)
    response = runtime.openclaw_client.submit_event(event)
    return {
        "ok": response.ok,
        "reply": {
            "text": response.reply_text,
            "attachments": [],
            "actions": [],
        },
        "response": response.to_dict(),
    }


def _to_openclaw_event(request: OpenClawChannelEventRequest) -> OpenClawEvent:
    message = request.message
    event_id = message.id or None
    payload = {
        **request.payload,
        "openclaw_channel": request.channel,
        "openclaw_account_id": request.accountId,
        "openclaw_sender": message.from_.model_dump(),
        "openclaw_timestamp": message.timestamp,
        "attachments": message.attachments,
    }
    return OpenClawEvent(
        channel=_runtime_channel(request.channel),
        actor_external_id=message.from_.id,
        text=message.text,
        event_id=event_id or f"openclaw-event-{uuid4()}",
        payload=payload,
    )


def _runtime_channel(channel: str) -> RuntimeChannel:
    normalized = channel.strip().lower()
    if normalized in {"feishu", "lark"}:
        return RuntimeChannel.FEISHU
    if normalized in {"mock", "test"}:
        return RuntimeChannel.MOCK
    if normalized in {"cli", "terminal"}:
        return RuntimeChannel.CLI
    return RuntimeChannel.OPENCLAW
