"""AutoMage-2 Agent skeleton package."""

from automage_agents.config.settings import RuntimeSettings
from automage_agents.core.enums import AgentLevel, AgentRole
from automage_agents.core.models import AgentIdentity, UserProfile

__all__ = [
    "AgentIdentity",
    "AgentLevel",
    "AgentRole",
    "RuntimeSettings",
    "UserProfile",
]
