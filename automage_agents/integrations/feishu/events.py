from __future__ import annotations

import json
import re
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
            "task_update": InternalEventType.TASK_UPDATE_REQUESTED,
            "task_completed": InternalEventType.TASK_COMPLETED,
            "manager_feedback": InternalEventType.MANAGER_FEEDBACK_SUBMITTED,
            "dream_decision": InternalEventType.DREAM_DECISION_REQUESTED,
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
        if any(keyword in text for keyword in ["生成决策草案", "决策草案", "Dream决策", "Dream 决策"]):
            return "dream_decision"
        if any(keyword in text for keyword in ["确认方案", "选择方案", "执行方案", "确认决策", "决策A", "决策B", "方案A", "方案B"]):
            return "executive_decision"
        if any(keyword in text for keyword in ["完成任务", "关闭任务", "开始任务", "更新任务", "任务完成", "任务开始"]):
            return "task_update"
        report_markers = ["今天完成了", "今日完成了", "完成了", "遇到的问题是", "遇到问题是", "明天", "明日", "下一步"]
        if any(marker in text for marker in report_markers):
            return "daily_report_submit"
        if any(keyword in text for keyword in ["查任务", "查询任务", "我的任务", "任务列表"]):
            return "task_query"
        return "daily_report_submit"

    def _build_text_payload(self, text: str, message: dict[str, Any], timestamp: str) -> dict[str, Any]:
        payload = {
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
        event_type = self._classify_text_message(text)
        if event_type in {"dream_decision", "executive_decision"}:
            payload.update(self._extract_decision_payload(text))
        if event_type == "task_update":
            payload.update(self._extract_task_update_payload(text))
        return payload

    def _extract_decision_payload(self, text: str) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        summary_id = self._extract_id(text, prefixes=("SUM", "MSUM"))
        if summary_id:
            payload["summary_id"] = summary_id
        option_id = self._extract_option_id(text)
        if option_id:
            payload["selected_option_id"] = option_id
        payload["decision_summary"] = text
        return payload

    def _extract_task_update_payload(self, text: str) -> dict[str, Any]:
        task_id = self._extract_id(text, prefixes=("TSK", "TASK", "mock-task", "mock-dream"))
        status = "completed" if any(keyword in text for keyword in ["完成任务", "任务完成", "关闭任务", "完成", "关闭"]) else "in_progress"
        return {
            "task_id": task_id or "",
            "status": status,
            "description": text,
            "task_payload": {"source": "feishu_im", "raw_text": text},
        }

    def _extract_option_id(self, text: str) -> str:
        match = re.search(r"(?:方案|决策|选择|确认)\s*([A-Za-z])", text)
        if match:
            return match.group(1).upper()
        return "B" if "B" in text.upper() else "A"

    def _extract_id(self, text: str, *, prefixes: tuple[str, ...]) -> str:
        escaped = "|".join(re.escape(prefix) for prefix in sorted(prefixes, key=len, reverse=True))
        match = re.search(rf"(?<![A-Za-z0-9_-])((?:{escaped})[A-Za-z0-9_-]*)", text, flags=re.IGNORECASE)
        return match.group(1) if match else ""

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
