from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class OutboundMessage:
    target_user_id: str
    title: str
    body: str
    card: dict[str, Any] = field(default_factory=dict)


class FeishuMessageAdapter:
    def send_message(self, message: OutboundMessage) -> dict[str, Any]:
        # TODO(OpenClaw): Replace this mock response with real Feishu/Lark send API or OpenClaw Channel call.
        # TODO(全栈/运维): Real app_id/app_secret must come from secure environment variables or secret manager.
        return {
            "ok": True,
            "channel": "feishu_mock",
            "target_user_id": message.target_user_id,
            "title": message.title,
            "body": message.body,
            "card": message.card,
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
