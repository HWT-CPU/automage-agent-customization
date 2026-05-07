from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any

from automage_agents.core.enums import InternalEventType
from automage_agents.core.models import SkillResult


@dataclass(slots=True)
class OutboundMessage:
    target_user_id: str
    title: str
    body: str
    card: dict[str, Any] = field(default_factory=dict)
    receive_id_type: str = "user_id"


class FeishuMessageAdapter:
    def send_message(self, message: OutboundMessage) -> dict[str, Any]:
        # TODO(OpenClaw): Replace this mock response with real Feishu/Lark send API or OpenClaw Channel call.
        # TODO(全栈/运维): Real app_id/app_secret must come from secure environment variables or secret manager.
        return {
            "ok": True,
            "channel": "feishu_mock",
            "target_user_id": message.target_user_id,
            "receive_id_type": message.receive_id_type,
            "title": message.title,
            "body": message.body,
            "card": message.card,
        }

    def send_lark_text(self, lark_client: Any, message: OutboundMessage) -> dict[str, Any]:
        from lark_oapi.api.im.v1 import CreateMessageRequest, CreateMessageRequestBody

        request = (
            CreateMessageRequest.builder()
            .receive_id_type(message.receive_id_type)
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(message.target_user_id)
                .msg_type("text")
                .content(json.dumps({"text": message.body}, ensure_ascii=False))
                .build()
            )
            .build()
        )
        response = lark_client.im.v1.message.create(request)
        data = response.data
        return {
            "ok": response.success(),
            "channel": "feishu",
            "code": response.code,
            "msg": response.msg,
            "log_id": response.get_log_id(),
            "message_id": getattr(data, "message_id", None) if data else None,
            "chat_id": getattr(data, "chat_id", None) if data else None,
        }

    def build_daily_report_card(self, target_user_id: str) -> OutboundMessage:
        return OutboundMessage(
            target_user_id=target_user_id,
            title="日报填写提醒",
            body="请填写今日工作进度、问题、明日计划和资源使用情况。",
            card={"type": "daily_report", "schema_id": "schema_v1_staff"},
        )

    def build_decision_card(self, target_user_id: str, decision_options: list[dict[str, Any]]) -> OutboundMessage:
        return OutboundMessage(
            target_user_id=target_user_id,
            title="A/B 决策确认",
            body="请选择需要执行的策略方案。",
            card={"type": "executive_decision", "options": decision_options},
        )

    def build_processing_result_reply(self, chat_id: str, event_type: str, result: SkillResult) -> OutboundMessage:
        return OutboundMessage(
            target_user_id=chat_id,
            receive_id_type="chat_id",
            title="AutoMage 处理结果",
            body=self._result_body(event_type, result),
            card={"type": "processing_result", "event_type": event_type, "ok": result.ok},
        )

    def _result_body(self, event_type: str, result: SkillResult) -> str:
        if not result.ok:
            return f"AutoMage 处理失败：{result.message}\n错误码：{result.error_code or 'unknown'}"
        if event_type == InternalEventType.DAILY_REPORT_SUBMITTED.value:
            work_record_id = result.data.get("work_record_id") or result.data.get("record", {}).get("work_record_id")
            lines = [
                "日报已收到。",
                "已按 schema_v1_staff v1.0.0 记录。",
                f"记录 ID：{work_record_id or 'mock-pending'}",
                "当前写入 mock backend，后续可切换真实后端。",
            ]
            return "\n".join(lines)
        if event_type == InternalEventType.TASK_QUERY_REQUESTED.value:
            tasks = result.data.get("tasks") or result.data.get("items", [])
            if not tasks:
                return "当前没有待处理任务。"
            lines = ["你的当前任务："]
            for index, task in enumerate(tasks[:5], start=1):
                title = task.get("title", "未命名任务")
                status = task.get("status", "unknown")
                lines.append(f"{index}. {title}（{status}）")
            return "\n".join(lines)
        return result.message or "AutoMage 已处理该事件。"
