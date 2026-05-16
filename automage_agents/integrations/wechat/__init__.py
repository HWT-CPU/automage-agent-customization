"""WeChat 集成模块"""

from automage_agents.integrations.wechat.messages import WeChatMessageAdapter
from automage_agents.integrations.wechat.events import WeChatEventAdapter

__all__ = ["WeChatMessageAdapter", "WeChatEventAdapter"]
