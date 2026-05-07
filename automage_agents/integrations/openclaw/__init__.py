"""OpenClaw adapter placeholder."""

from automage_agents.integrations.openclaw.adapter import OpenClawAdapter
from automage_agents.integrations.openclaw.client import LocalOpenClawClient
from automage_agents.integrations.openclaw.config import (
    OpenClawChannelConfig,
    OpenClawCommandConfig,
    OpenClawConfig,
    OpenClawRoutingConfig,
    load_openclaw_config,
)
from automage_agents.integrations.openclaw.contracts import OpenClawEvent, OpenClawResponse
from automage_agents.integrations.openclaw.parser import OpenClawCommandParser, ParsedOpenClawCommand

__all__ = [
    "LocalOpenClawClient",
    "OpenClawAdapter",
    "OpenClawChannelConfig",
    "OpenClawCommandConfig",
    "OpenClawCommandParser",
    "OpenClawConfig",
    "OpenClawEvent",
    "OpenClawResponse",
    "OpenClawRoutingConfig",
    "ParsedOpenClawCommand",
    "load_openclaw_config",
]
