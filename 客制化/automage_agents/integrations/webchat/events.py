"""WebChat 事件适配器 - 将 Web 聊天消息转换为内部事件"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from automage_agents.core.enums import InternalEventType, RuntimeChannel
from automage_agents.core.models import InternalEvent


@dataclass(slots=True)
class WebChatMessage:
    """Web 聊天消息"""
    message_id: str
    from_user: str
    content: str
    timestamp: float
    metadata: dict[str, Any]


class WebChatEventAdapter:
    """WebChat 事件适配器"""
    
    def __init__(self, user_mapping: dict[str, str] | None = None):
        """
        Args:
            user_mapping: WebChat user_id 到 AutoMage user_id 的映射
        """
        self.user_mapping = user_mapping or {}
    
    def from_webchat_message(self, raw_message: dict[str, Any]) -> WebChatMessage:
        """从原始消息构建 WebChatMessage"""
        return WebChatMessage(
            message_id=raw_message.get("id", ""),
            from_user=raw_message.get("from_user", ""),
            content=raw_message.get("content", ""),
            timestamp=raw_message.get("timestamp", 0.0),
            metadata=raw_message.get("metadata", {}),
        )
    
    def to_internal_event(self, message: WebChatMessage) -> InternalEvent:
        """将 WebChat 消息转换为内部事件"""
        actor_user_id = self.user_mapping.get(
            message.from_user,
            message.from_user,
        )
        
        content = message.content.strip()
        
        # 判断消息类型
        if self._is_daily_report(content):
            return InternalEvent(
                event_type=InternalEventType.DAILY_REPORT_SUBMITTED,
                source_channel=RuntimeChannel.WEBCHAT,
                actor_user_id=actor_user_id,
                correlation_id=message.message_id,
                payload={
                    "webchat_user_id": message.from_user,
                    "raw_text": content,
                    "channel": "webchat",
                    "metadata": message.metadata,
                },
            )
        
        if self._is_task_query(content):
            return InternalEvent(
                event_type=InternalEventType.TASK_QUERY_REQUESTED,
                source_channel=RuntimeChannel.WEBCHAT,
                actor_user_id=actor_user_id,
                correlation_id=message.message_id,
                payload={
                    "webchat_user_id": message.from_user,
                    "raw_text": content,
                    "channel": "webchat",
                },
            )
        
        # 默认：文本消息
        return InternalEvent(
            event_type=InternalEventType.TEXT_MESSAGE_RECEIVED,
            source_channel=RuntimeChannel.WEBCHAT,
            actor_user_id=actor_user_id,
            correlation_id=message.message_id,
            payload={
                "webchat_user_id": message.from_user,
                "raw_text": content,
                "channel": "webchat",
            },
        )
    
    def _is_daily_report(self, content: str) -> bool:
        """判断是否为日报提交"""
        keywords = ["今天", "完成", "进展", "问题", "计划", "明天"]
        return any(kw in content for kw in keywords)
    
    def _is_task_query(self, content: str) -> bool:
        """判断是否为任务查询"""
        keywords = ["任务", "待办", "查任务", "我的任务"]
        return any(kw in content for kw in keywords)
