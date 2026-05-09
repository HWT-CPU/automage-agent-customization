"""Skill package for AutoMage-2 agent capabilities."""

from automage_agents.skills.common import agent_init, check_auth_status, load_user_profile
from automage_agents.skills.context import SkillContext
from automage_agents.skills.executive import broadcast_strategy, commit_decision, dream_decision_engine
from automage_agents.skills.knowledge import search_feishu_knowledge
from automage_agents.skills.manager import analyze_team_reports, delegate_task, generate_manager_report, generate_manager_schema
from automage_agents.skills.registry import SKILL_REGISTRY, get_skill
from automage_agents.skills.schema_tools import schema_self_correct
from automage_agents.skills.staff import fetch_my_tasks, import_staff_daily_report_from_markdown, post_daily_report, read_staff_daily_report, update_my_task

__all__ = [
    "SKILL_REGISTRY",
    "SkillContext",
    "agent_init",
    "analyze_team_reports",
    "broadcast_strategy",
    "check_auth_status",
    "commit_decision",
    "delegate_task",
    "dream_decision_engine",
    "fetch_my_tasks",
    "generate_manager_report",
    "generate_manager_schema",
    "get_skill",
    "import_staff_daily_report_from_markdown",
    "load_user_profile",
    "post_daily_report",
    "read_staff_daily_report",
    "schema_self_correct",
    "search_feishu_knowledge",
    "update_my_task",
]
