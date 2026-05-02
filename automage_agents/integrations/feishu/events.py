from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from automage_agents.core.enums import InternalEventType, RuntimeChannel
from automage_agents.core.models import InternalEvent


@dataclass(slots=True)
class FeishuEvent:
    event_type: str
    open_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    message_id: str | None = None


class FeishuEventAdapter:
    def __init__(self, user_mapping: dict[str, str] | None = None):
        self.user_mapping = user_mapping or {}

    def to_internal_event(self, event: FeishuEvent) -> InternalEvent:
        actor_user_id = self.user_mapping.get(event.open_id, event.open_id)
        internal_type = self._map_event_type(event.event_type)
        return InternalEvent(
            event_type=internal_type,
            source_channel=RuntimeChannel.FEISHU,
            actor_user_id=actor_user_id,
            payload={
                "feishu_open_id": event.open_id,
                "feishu_event_type": event.event_type,
                "message_id": event.message_id,
                **event.payload,
            },
            correlation_id=event.message_id,
        )

    def _map_event_type(self, event_type: str) -> InternalEventType:
        # TODO(OpenClaw): Replace this mapping after real Feishu/Lark callback payloads are confirmed.
        mapping = {
            "daily_report_submit": InternalEventType.DAILY_REPORT_SUBMITTED,
            "task_query": InternalEventType.TASK_QUERY_REQUESTED,
            "task_completed": InternalEventType.TASK_COMPLETED,
            "manager_feedback": InternalEventType.MANAGER_FEEDBACK_SUBMITTED,
            "executive_decision": InternalEventType.EXECUTIVE_DECISION_SELECTED,
            "auth_failed": InternalEventType.AUTH_FAILED,
        }
        return mapping[event_type]
