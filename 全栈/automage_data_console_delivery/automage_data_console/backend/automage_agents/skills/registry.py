from __future__ import annotations

from collections.abc import Callable
from typing import Any

from automage_agents.skills.common import agent_init, check_auth_status, load_user_profile
from automage_agents.skills.executive import broadcast_strategy, commit_decision, dream_decision_engine
from automage_agents.skills.knowledge import search_feishu_knowledge
from automage_agents.skills.manager import analyze_team_reports, delegate_task, generate_manager_report, generate_manager_schema
from automage_agents.skills.schema_tools import schema_self_correct
from automage_agents.skills.staff import fetch_my_tasks, import_staff_daily_report_from_markdown, post_daily_report, read_staff_daily_report, update_my_task

SkillCallable = Callable[..., Any]


SKILL_REGISTRY: dict[str, SkillCallable] = {
    "agent_init": agent_init,
    "check_auth_status": check_auth_status,
    "load_user_profile": load_user_profile,
    "search_feishu_knowledge": search_feishu_knowledge,
    "post_daily_report": post_daily_report,
    "fetch_my_tasks": fetch_my_tasks,
    "update_my_task": update_my_task,
    "import_staff_daily_report_from_markdown": import_staff_daily_report_from_markdown,
    "read_staff_daily_report": read_staff_daily_report,
    "analyze_team_reports": analyze_team_reports,
    "generate_manager_report": generate_manager_report,
    "generate_manager_schema": generate_manager_schema,
    "delegate_task": delegate_task,
    "dream_decision_engine": dream_decision_engine,
    "commit_decision": commit_decision,
    "broadcast_strategy": broadcast_strategy,
    "schema_self_correct": schema_self_correct,
}


def get_skill(name: str) -> SkillCallable:
    # TODO(Hermes): 后续用 Hermes 官方 Skill 注册机制替换本地 registry。
    return SKILL_REGISTRY[name]
