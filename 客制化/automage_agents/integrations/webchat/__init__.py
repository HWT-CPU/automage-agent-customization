"""WebChat 集成模块 - 对接 Web 聊天数据源"""

from automage_agents.integrations.webchat.client import WebChatClient
from automage_agents.integrations.webchat.events import WebChatEventAdapter

__all__ = ["WebChatClient", "WebChatEventAdapter"]
