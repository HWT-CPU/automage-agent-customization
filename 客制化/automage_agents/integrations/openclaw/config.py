from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from automage_agents.config.loader import load_toml


@dataclass(slots=True)
class OpenClawChannelConfig:
    enabled: bool = True
    event_mode: str = "real"  # 默认使用真实模式
    reply_enabled: bool = True


@dataclass(slots=True)
class OpenClawRoutingConfig:
    default_daily_report: str = "daily_report_submit"
    default_task_query: str = "task_query"
    default_knowledge_query: str = "knowledge_query"
    default_manager_feedback: str = "manager_feedback"
    default_executive_decision: str = "executive_decision"
    default_markdown_import: str = "daily_report_markdown_import"


@dataclass(slots=True)
class OpenClawCommandConfig:
    daily_report: list[str] = field(default_factory=list)
    task_query: list[str] = field(default_factory=list)
    knowledge_query: list[str] = field(default_factory=list)
    manager_feedback: list[str] = field(default_factory=list)
    executive_decision: list[str] = field(default_factory=list)
    markdown_import: list[str] = field(default_factory=list)


@dataclass(slots=True)
class OpenClawConfig:
    enabled: bool
    runtime_name: str
    default_channel: str
    reply_enabled: bool
    cli: OpenClawChannelConfig
    feishu: OpenClawChannelConfig
    routing: OpenClawRoutingConfig
    commands: OpenClawCommandConfig


def load_openclaw_config(path: str | Path = "configs/openclaw.example.toml") -> OpenClawConfig:
    raw = load_toml(path).get("openclaw", {})
    channels = raw.get("channels", {})
    commands = raw.get("commands", {})
    return OpenClawConfig(
        enabled=bool(raw.get("enabled", True)),
        runtime_name=str(raw.get("runtime_name", "automage-openclaw-local")),
        default_channel=str(raw.get("default_channel", "cli")),
        reply_enabled=bool(raw.get("reply_enabled", True)),
        cli=_build_channel_config(channels.get("cli", {}), "real"),  # CLI 默认真实模式
        feishu=_build_channel_config(channels.get("feishu", {}), "websocket"),
        routing=_build_routing_config(raw.get("routing", {})),
        commands=OpenClawCommandConfig(
            daily_report=list(commands.get("daily_report", {}).get("keywords", [])),
            task_query=list(commands.get("task_query", {}).get("keywords", [])),
            knowledge_query=list(commands.get("knowledge_query", {}).get("keywords", [])),
            manager_feedback=list(commands.get("manager_feedback", {}).get("keywords", [])),
            executive_decision=list(commands.get("executive_decision", {}).get("keywords", [])),
            markdown_import=list(commands.get("markdown_import", {}).get("keywords", [])),
        ),
    )


def _build_channel_config(raw: dict[str, Any], default_event_mode: str) -> OpenClawChannelConfig:
    return OpenClawChannelConfig(
        enabled=bool(raw.get("enabled", True)),
        event_mode=str(raw.get("event_mode", default_event_mode)),
        reply_enabled=bool(raw.get("reply_enabled", True)),
    )


def _build_routing_config(raw: dict[str, Any]) -> OpenClawRoutingConfig:
    return OpenClawRoutingConfig(
        default_daily_report=str(raw.get("default_daily_report", "daily_report_submit")),
        default_task_query=str(raw.get("default_task_query", "task_query")),
        default_knowledge_query=str(raw.get("default_knowledge_query", "knowledge_query")),
        default_manager_feedback=str(raw.get("default_manager_feedback", "manager_feedback")),
        default_executive_decision=str(raw.get("default_executive_decision", "executive_decision")),
        default_markdown_import=str(raw.get("default_markdown_import", "daily_report_markdown_import")),
    )
