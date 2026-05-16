"""Agent template metadata, registry, and rendering helpers."""

from automage_agents.agents.registry import AGENT_TEMPLATES, get_agent_template
from automage_agents.agents.renderer import render_agent_markdown, write_rendered_agent

__all__ = [
    "AGENT_TEMPLATES",
    "get_agent_template",
    "render_agent_markdown",
    "write_rendered_agent",
]
