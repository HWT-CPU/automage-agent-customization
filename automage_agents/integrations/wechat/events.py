"""WeChat 事件适配器 - 接收老板微信回复"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from automage_agents.core.enums import InternalEventType, RuntimeChannel
from automage_agents.core.models import InternalEvent


@dataclass(slots=True)
class WeChatEvent:
    """微信事件"""
    message_id: str
    from_user: str  # 微信 ID
    content: str
    timestamp: float


class WeChatEventAdapter:
    """微信事件适配器 - 解析老板回复并转换为内部事件"""
    
    def __init__(self, user_mapping: dict[str, str] | None = None):
        """
        Args:
            user_mapping: 微信 ID 到 AutoMage user_id 的映射
                例如: {"o9cq80-4ZTet7x8h6pGOsyDexBik@im.wechat": "chenzong"}
        """
        self.user_mapping = user_mapping or {}
    
    def from_wechat_message(self, raw_event: dict[str, Any]) -> WeChatEvent:
        """从原始微信消息构建 WeChatEvent"""
        return WeChatEvent(
            message_id=raw_event.get("message_id", ""),
            from_user=raw_event.get("from_user", ""),
            content=raw_event.get("content", ""),
            timestamp=raw_event.get("timestamp", 0.0),
        )
    
    def to_internal_event(self, wechat_event: WeChatEvent) -> InternalEvent:
        """将微信事件转换为内部事件"""
        # 映射微信 ID 到 AutoMage user_id
        actor_user_id = self.user_mapping.get(
            wechat_event.from_user,
            wechat_event.from_user,
        )
        
        # 解析消息内容，判断事件类型
        content = wechat_event.content.strip()
        
        # 匹配决策确认：确认方案A summary_xxx 或 确认方案B summary_xxx
        decision_match = re.match(
            r"确认方案\s*([AaBb])\s+(\S+)",
            content,
            re.IGNORECASE,
        )
        
        if decision_match:
            option_key = decision_match.group(1).upper()
            summary_id = decision_match.group(2)
            
            return InternalEvent(
                event_type=InternalEventType.EXECUTIVE_DECISION_SELECTED,
                source_channel=RuntimeChannel.WECHAT,
                actor_user_id=actor_user_id,
                correlation_id=wechat_event.message_id,
                payload={
                    "wechat_user_id": wechat_event.from_user,
                    "summary_id": summary_id,
                    "selected_option": option_key,
                    "raw_text": content,
                    "channel": "wechat",
                },
            )
        
        # 默认：文本消息
        return InternalEvent(
            event_type=InternalEventType.TEXT_MESSAGE_RECEIVED,
            source_channel=RuntimeChannel.WECHAT,
            actor_user_id=actor_user_id,
            correlation_id=wechat_event.message_id,
            payload={
                "wechat_user_id": wechat_event.from_user,
                "raw_text": content,
                "channel": "wechat",
            },
        )
