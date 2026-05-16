from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from automage_agents.config.loader import load_toml
from automage_agents.core.enums import RuntimeChannel


@dataclass(slots=True)
class HermesAgentConfig:
    enabled: bool
    profile_path: str
    workflow_stage: str


@dataclass(slots=True)
class HermesContextConfig:
    org_id: str = "org-001"
    run_date: str = ""
    workflow_name: str = "automage_mvp_dag"
    source_channel: RuntimeChannel = RuntimeChannel.MOCK


@dataclass(slots=True)
class HermesConfig:
    enabled: bool
    runtime_name: str
    mode: str
    settings_path: str
    use_mock_api: bool
    skill_registry: str
    context: HermesContextConfig
    staff: HermesAgentConfig
    manager: HermesAgentConfig
    executive: HermesAgentConfig


def load_hermes_config(path: str | Path = "configs/hermes.example.toml") -> HermesConfig:
    raw = load_toml(path).get("hermes", {})
    agents = raw.get("agents", {})
    return HermesConfig(
        enabled=bool(raw.get("enabled", True)),
        runtime_name=str(raw.get("runtime_name", "automage-hermes-local")),
        mode=str(raw.get("mode", "local")),
        settings_path=str(raw.get("settings_path", "configs/automage.example.toml")),
        use_mock_api=bool(raw.get("use_mock_api", True)),
        skill_registry=str(raw.get("skill_registry", "automage_agents.skills.registry.SKILL_REGISTRY")),
        context=_build_context_config(raw.get("context", {})),
        staff=_build_agent_config(agents.get("staff", {}), "examples/user.staff.example.toml", "staff_daily_report"),
        manager=_build_agent_config(agents.get("manager", {}), "examples/user.manager.example.toml", "manager_summary"),
        executive=_build_agent_config(agents.get("executive", {}), "examples/user.executive.example.toml", "executive_decision"),
    )


def _build_context_config(raw: dict[str, Any]) -> HermesContextConfig:
    return HermesContextConfig(
        org_id=str(raw.get("org_id", "org-001")),
        run_date=str(raw.get("run_date", "")),
        workflow_name=str(raw.get("workflow_name", "automage_mvp_dag")),
        source_channel=RuntimeChannel(str(raw.get("source_channel", RuntimeChannel.MOCK.value))),
    )


def _build_agent_config(raw: dict[str, Any], default_profile_path: str, default_workflow_stage: str) -> HermesAgentConfig:
    return HermesAgentConfig(
        enabled=bool(raw.get("enabled", True)),
        profile_path=str(raw.get("profile_path", default_profile_path)),
        workflow_stage=str(raw.get("workflow_stage", default_workflow_stage)),
    )
