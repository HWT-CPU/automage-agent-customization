from __future__ import annotations

from pathlib import Path

from automage_agents.agents.registry import get_agent_template
from automage_agents.core.models import AgentTemplateSpec, CronEntry, UserProfile
from automage_agents.utils.paths import TEMPLATE_ROOT


ROLE_TO_TEMPLATE_NAME = {
    "base": "base",
    "staff": "line_worker",
    "manager": "manager",
    "executive": "executive",
}


def render_agent_markdown(user_profile: UserProfile, template_name: str | None = None) -> str:
    resolved_template_name = template_name or ROLE_TO_TEMPLATE_NAME[user_profile.identity.role.value]
    spec = get_agent_template(resolved_template_name)
    template_body = load_agent_template_body(resolved_template_name)
    return "\n".join(
        [
            template_body.rstrip(),
            "",
            "---",
            "",
            render_user_context(user_profile),
            "",
            render_template_contract(spec),
            "",
        ]
    )


def load_agent_template_body(template_name: str) -> str:
    path = TEMPLATE_ROOT / template_name / "agents.md"
    if not path.exists():
        raise FileNotFoundError(f"Agent template not found: {path}")
    return path.read_text(encoding="utf-8")


def render_user_context(user_profile: UserProfile) -> str:
    identity = user_profile.identity
    return "\n".join(
        [
            "# Rendered User Context",
            "",
            "TODO(Hermes): Confirm whether this rendered block should be injected into Hermes prompt, memory, or config.",
            "",
            "## Identity",
            "",
            f"- `user_id`: `{identity.user_id}`",
            f"- `node_id`: `{identity.node_id}`",
            f"- `role`: `{identity.role.value}`",
            f"- `level`: `{identity.level.value}`",
            f"- `department_id`: `{identity.department_id or ''}`",
            f"- `manager_node_id`: `{identity.manager_node_id or ''}`",
            f"- `display_name`: {user_profile.display_name}",
            f"- `job_title`: {user_profile.job_title}",
            "",
            "## Responsibilities",
            "",
            render_bullets(user_profile.responsibilities),
            "",
            "## Input Sources",
            "",
            render_bullets(user_profile.input_sources),
            "",
            "## Output Requirements",
            "",
            render_bullets(user_profile.output_requirements),
            "",
            "## Permission Notes",
            "",
            render_bullets(user_profile.permission_notes),
            "",
            "## Personalized Context",
            "",
            user_profile.personalized_context or "TODO: Fill personalized context in user.md.",
        ]
    )


def render_template_contract(spec: AgentTemplateSpec) -> str:
    return "\n".join(
        [
            "# Rendered Template Contract",
            "",
            f"- `template_name`: `{spec.template_name}`",
            f"- `role`: `{spec.role.value}`",
            f"- `level`: `{spec.level.value}`",
            f"- `description`: {spec.description}",
            "",
            "## Skill List",
            "",
            render_bullets([f"`{name}`" for name in spec.skill_names]),
            "",
            "## Cron Entries",
            "",
            render_cron_entries(spec.cron_entries),
            "",
            "## Constraints",
            "",
            render_bullets(spec.constraints),
        ]
    )


def render_bullets(items: list[str]) -> str:
    if not items:
        return "- TODO: Fill this section."
    return "\n".join(f"- {item}" for item in items)


def render_cron_entries(entries: list[CronEntry]) -> str:
    if not entries:
        return "- No cron entry in this template draft."
    return "\n".join(
        f"- `{entry.schedule}` → `{entry.skill_name}`: {entry.description}"
        for entry in entries
        if entry.enabled
    )


def write_rendered_agent(user_profile: UserProfile, output_path: str | Path, template_name: str | None = None) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_agent_markdown(user_profile, template_name), encoding="utf-8")
    return path
