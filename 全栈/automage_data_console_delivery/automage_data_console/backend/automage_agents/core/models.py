from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from automage_agents.core.enums import AgentLevel, AgentRole, InternalEventType, RuntimeChannel


@dataclass(slots=True)
class AgentIdentity:
    node_id: str
    user_id: str
    role: AgentRole
    level: AgentLevel
    department_id: str | None = None
    manager_node_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["role"] = self.role.value
        data["level"] = self.level.value
        return data


@dataclass(slots=True)
class UserProfile:
    identity: AgentIdentity
    display_name: str
    job_title: str
    responsibilities: list[str] = field(default_factory=list)
    input_sources: list[str] = field(default_factory=list)
    output_requirements: list[str] = field(default_factory=list)
    personalized_context: str = ""
    permission_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["identity"] = self.identity.to_dict()
        return data


@dataclass(slots=True)
class RuntimeContextV0:
    context_version: str = "context_v0"
    org_id: str = "org-001"
    run_date: str = ""
    workflow_name: str = "automage_mvp_dag"
    workflow_stage: str = ""
    source_channel: RuntimeChannel = RuntimeChannel.MOCK
    input_refs: dict[str, Any] = field(default_factory=dict)
    output_refs: dict[str, Any] = field(default_factory=dict)

    def to_dict(self, identity: AgentIdentity | None = None) -> dict[str, Any]:
        data = asdict(self)
        data["source_channel"] = self.source_channel.value
        if identity is not None:
            data["identity"] = identity.to_dict()
        return data


@dataclass(slots=True)
class CronEntry:
    name: str
    schedule: str
    agent_role: AgentRole
    skill_name: str
    description: str
    enabled: bool = True


@dataclass(slots=True)
class AgentTemplateSpec:
    role: AgentRole
    level: AgentLevel
    template_name: str
    description: str
    skill_names: list[str] = field(default_factory=list)
    cron_entries: list[CronEntry] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)


@dataclass(slots=True)
class InternalEvent:
    event_type: InternalEventType
    source_channel: RuntimeChannel
    actor_user_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None


@dataclass(slots=True)
class SkillResult:
    ok: bool
    data: dict[str, Any] = field(default_factory=dict)
    message: str = ""
    error_code: str | None = None
