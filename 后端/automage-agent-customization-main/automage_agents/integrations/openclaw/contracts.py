from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from automage_agents.core.enums import RuntimeChannel
from automage_agents.integrations.hermes.contracts import HermesInvokeResponse


@dataclass(slots=True)
class OpenClawEvent:
    channel: RuntimeChannel
    actor_external_id: str
    text: str
    event_id: str = field(default_factory=lambda: f"openclaw-event-{uuid4()}")
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().astimezone().isoformat())


@dataclass(slots=True)
class OpenClawResponse:
    ok: bool
    event: OpenClawEvent
    event_type: str
    skill_name: str
    reply_text: str
    hermes: HermesInvokeResponse | None = None
    error_code: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "event": {
                "event_id": self.event.event_id,
                "channel": self.event.channel.value,
                "actor_external_id": self.event.actor_external_id,
                "text": self.event.text,
                "payload": self.event.payload,
                "created_at": self.event.created_at,
            },
            "event_type": self.event_type,
            "skill_name": self.skill_name,
            "reply_text": self.reply_text,
            "error_code": self.error_code,
            "hermes": self.hermes.to_dict() if self.hermes else None,
        }
