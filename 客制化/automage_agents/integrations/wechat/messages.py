"""WeChat 消息适配器 - 推送决策和通知到老板微信"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

import requests

from automage_agents.core.enums import InternalEventType
from automage_agents.core.models import SkillResult


@dataclass(slots=True)
class WeChatOutboundMessage:
    """微信推送消息"""
    target_user_id: str  # 微信 ID，如 o9cq80-4ZTet7x8h6pGOsyDexBik@im.wechat
    title: str
    body: str
    channel: str = "openclaw-weixin"
    kind: str = "systemEvent"
    card: dict[str, Any] = field(default_factory=dict)


class WeChatMessageAdapter:
    """微信消息适配器 - 通过后端 API 推送消息"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000", timeout: int = 10):
        self.api_base_url = api_base_url.rstrip("/")
        self.timeout = timeout
    
    def send_message(self, message: WeChatOutboundMessage) -> dict[str, Any]:
        """发送微信消息（通过后端 API）"""
        try:
            response = requests.post(
                f"{self.api_base_url}/internal/wechat",
                json={
                    "channel": message.channel,
                    "to": message.target_user_id,
                    "title": message.title,
                    "message": message.body,
                    "kind": message.kind,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            result = response.json()
            return {
                "ok": True,
                "channel": "wechat",
                "target_user_id": message.target_user_id,
                "title": message.title,
                "response": result,
            }
        except Exception as exc:
            return {
                "ok": False,
                "channel": "wechat",
                "error": str(exc),
                "target_user_id": message.target_user_id,
            }
    
    def build_decision_card(
        self, 
        target_user_id: str, 
        summary_id: str,
        department: str,
        decision_options: list[dict[str, Any]]
    ) -> WeChatOutboundMessage:
        """构建 A/B 决策推送卡片"""
        lines = [
            f"📋 AutoMage 决策推送",
            f"",
            f"部门：{department}",
            f"汇总 ID：{summary_id}",
            f"",
            f"请选择执行方案：",
        ]
        
        for option in decision_options:
            option_id = option.get("option_id") or option.get("key") or "?"
            title = option.get("title") or "未命名方案"
            summary = option.get("summary") or ""
            tasks = option.get("task_candidates") or []
            
            lines.append(f"")
            lines.append(f"【方案 {option_id}】{title}")
            lines.append(f"摘要：{summary}")
            lines.append(f"任务数：{len(tasks)} 个")
        
        lines.append(f"")
        lines.append(f"回复格式：确认方案A {summary_id}")
        
        body = "\n".join(lines)
        
        return WeChatOutboundMessage(
            target_user_id=target_user_id,
            title="AutoMage 决策推送",
            body=body,
            card={
                "type": "executive_decision",
                "summary_id": summary_id,
                "department": department,
                "options": decision_options,
            },
        )

    def build_manager_summary_notification(
        self,
        target_user_id: str,
        summary_id: str,
        department: str,
        overall_health: str,
        top_risks: list[dict[str, Any]],
    ) -> WeChatOutboundMessage:
        """构建 Manager 汇总通知"""
        health_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(overall_health, "⚪")
        
        lines = [
            f"📊 Manager 汇总已生成",
            f"",
            f"部门：{department}",
            f"汇总 ID：{summary_id}",
            f"健康度：{health_emoji} {overall_health}",
            f"",
        ]
        
        if top_risks:
            lines.append("⚠️ 主要风险：")
            for i, risk in enumerate(top_risks[:3], 1):
                title = risk.get("risk_title") or risk.get("title") or "未命名风险"
                severity = risk.get("severity", "unknown")
                lines.append(f"{i}. [{severity}] {title}")
        else:
            lines.append("✅ 无重大风险")
        
        body = "\n".join(lines)
        
        return WeChatOutboundMessage(
            target_user_id=target_user_id,
            title="Manager 汇总通知",
            body=body,
            kind="notification",
        )
    
    def build_daily_report_reminder(
        self,
        target_user_id: str,
        missing_staff: list[str],
    ) -> WeChatOutboundMessage:
        """构建日报提醒"""
        lines = [
            f"⏰ 日报提醒",
            f"",
            f"以下员工尚未提交今日日报：",
            f"",
        ]
        
        for staff in missing_staff:
            lines.append(f"• {staff}")
        
        lines.append(f"")
        lines.append(f"请及时提醒员工提交日报。")
        
        body = "\n".join(lines)
        
        return WeChatOutboundMessage(
            target_user_id=target_user_id,
            title="日报提醒",
            body=body,
            kind="reminder",
        )
