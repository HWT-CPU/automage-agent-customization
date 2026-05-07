from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
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

    def from_message_receive_v1(self, raw_event: dict[str, Any]) -> FeishuEvent:
        event = raw_event.get("event", raw_event)
        sender = event.get("sender", {})
        sender_id = sender.get("sender_id", {})
        message = event.get("message", {})
        text = self._extract_text(message)
        timestamp = self._message_timestamp(message)
        event_type = self._classify_text_message(text)
        payload = self._build_text_payload(text, message, timestamp)
        payload["raw_event_type"] = raw_event.get("header", {}).get("event_type", "im.message.receive_v1")
        return FeishuEvent(
            event_type=event_type,
            open_id=str(sender_id.get("open_id") or sender_id.get("user_id") or sender_id.get("union_id") or "unknown_feishu_user"),
            payload=payload,
            message_id=message.get("message_id"),
        )

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

    def _extract_text(self, message: dict[str, Any]) -> str:
        content = message.get("content", {})
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                return content.strip()
        if not isinstance(content, dict):
            return ""
        return str(content.get("text") or content.get("content") or "").strip()

    def _message_timestamp(self, message: dict[str, Any]) -> str:
        raw_timestamp = message.get("create_time") or message.get("update_time")
        if raw_timestamp:
            try:
                timestamp = int(str(raw_timestamp))
                if timestamp > 10_000_000_000:
                    timestamp = timestamp // 1000
                return datetime.fromtimestamp(timestamp, tz=timezone.utc).astimezone().isoformat()
            except ValueError:
                return str(raw_timestamp)
        return datetime.now().astimezone().isoformat()

    def _classify_text_message(self, text: str) -> str:
        if any(keyword in text for keyword in ["查任务", "查询任务", "我的任务", "任务列表"]):
            return "task_query"
        return "daily_report_submit"

    def _build_text_payload(self, text: str, message: dict[str, Any], timestamp: str) -> dict[str, Any]:
        return {
            "timestamp": timestamp,
            "work_progress": self._extract_segment(text, ["今天完成了", "今日完成了", "完成了"], ["遇到的问题是", "遇到问题是", "问题是", "明天", "明日"]) or text,
            "issues_faced": self._extract_segment(text, ["遇到的问题是", "遇到问题是", "问题是", "阻塞是"], ["明天", "明日", "下一步"]),
            "solution_attempt": self._extract_segment(text, ["已处理", "已尝试", "解决方式是"], ["明天", "明日", "下一步"]),
            "need_support": any(keyword in text for keyword in ["需要支持", "阻塞", "问题", "还没确定", "不确定"]),
            "next_day_plan": self._extract_segment(text, ["明天", "明日", "下一步"], []),
            "resource_usage": {
                "source": "feishu_im",
                "chat_id": message.get("chat_id"),
                "chat_type": message.get("chat_type"),
                "message_type": message.get("message_type"),
            },
            "raw_text": text,
        }

    def _extract_segment(self, text: str, start_markers: list[str], end_markers: list[str]) -> str:
        start_index = -1
        marker_length = 0
        for marker in start_markers:
            index = text.find(marker)
            if index >= 0 and (start_index < 0 or index < start_index):
                start_index = index
                marker_length = len(marker)
        if start_index < 0:
            return ""
        segment = text[start_index + marker_length :]
        end_indexes = [segment.find(marker) for marker in end_markers if segment.find(marker) >= 0]
        if end_indexes:
            segment = segment[: min(end_indexes)]
        return segment.strip(" ：:，,。.\n")
