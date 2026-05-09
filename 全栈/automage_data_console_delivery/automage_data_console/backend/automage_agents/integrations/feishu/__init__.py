"""Feishu/Lark event and message adapters."""

from automage_agents.integrations.feishu.docs_cli import FeishuDocsCliClient, FeishuDocsFetchResult
from automage_agents.integrations.feishu.events import FeishuEvent, FeishuEventAdapter
from automage_agents.integrations.feishu.messages import FeishuMessageAdapter, OutboundMessage

__all__ = [
    "FeishuDocsCliClient",
    "FeishuDocsFetchResult",
    "FeishuEvent",
    "FeishuEventAdapter",
    "FeishuMessageAdapter",
    "OutboundMessage",
]
