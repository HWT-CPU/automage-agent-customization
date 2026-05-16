from __future__ import annotations

from automage_agents.core.enums import AgentLevel, AgentRole
from automage_agents.core.models import AgentTemplateSpec, CronEntry


BASE_TEMPLATE = AgentTemplateSpec(
    role=AgentRole.BASE,
    level=AgentLevel.BASE,
    template_name="base",
    description="Shared runtime assumptions for all AutoMage-2 agents.",
    skill_names=[
        "agent_init",
        "check_auth_status",
        "load_user_profile",
        "validate_schema",
    ],
    constraints=[
        "All writes must go through AutoMage-2 backend APIs.",
        "Database is the source of truth; local memory is only auxiliary context.",
        "Do not bypass backend permission checks with prompt-only rules.",
    ],
)


STAFF_TEMPLATE = AgentTemplateSpec(
    role=AgentRole.STAFF,
    level=AgentLevel.L1_STAFF,
    template_name="line_worker",
    description="岗位级 Staff Agent，负责员工日报、任务查询和执行反馈。",
    skill_names=[
        "agent_init",
        "post_daily_report",
        "fetch_my_tasks",
        "check_auth_status",
        "schema_self_correct",
    ],
    cron_entries=[
        CronEntry(
            name="staff_daily_report_card",
            schedule="0 18 * * *",
            agent_role=AgentRole.STAFF,
            skill_name="send_daily_report_card",
            description="每日 18:00 发送员工日报卡片。",
        ),
        CronEntry(
            name="staff_daily_report_reminder",
            schedule="0 20 * * *",
            agent_role=AgentRole.STAFF,
            skill_name="send_reminder_card",
            description="每日 20:00 对未提交日报员工二次催填。",
        ),
    ],
    constraints=[
        "Only access current user_id tasks and reports.",
        "Do not read other staff records.",
        "Do not make department-level or company-level decisions.",
        "TODO(杨卓): Align guidance with final schema_v1_staff fields.",
        "TODO(熊锦文): Align role/user permission checks with backend auth contract.",
    ],
)


MANAGER_TEMPLATE = AgentTemplateSpec(
    role=AgentRole.MANAGER,
    level=AgentLevel.L2_MANAGER,
    template_name="manager",
    description="部门 Manager Agent，负责部门日报汇总、风险识别和权限内任务分发。",
    skill_names=[
        "agent_init",
        "analyze_team_reports",
        "generate_manager_schema",
        "delegate_task",
        "check_auth_status",
    ],
    cron_entries=[
        CronEntry(
            name="manager_daily_summary",
            schedule="0 21 * * *",
            agent_role=AgentRole.MANAGER,
            skill_name="generate_manager_schema",
            description="每日 21:00 读取本部门日报并生成部门汇总。",
        ),
    ],
    constraints=[
        "Only access records in the assigned department_id.",
        "Escalate out-of-scope decisions instead of executing them directly.",
        "TODO(杨卓): Align aggregation logic with final schema_v1_manager fields.",
        "TODO(熊锦文): Confirm department data read API and permission boundary.",
    ],
)


EXECUTIVE_TEMPLATE = AgentTemplateSpec(
    role=AgentRole.EXECUTIVE,
    level=AgentLevel.L3_EXECUTIVE,
    template_name="executive",
    description="公司 Executive Agent，负责全局汇总、Dream 决策和战略任务下发。",
    skill_names=[
        "agent_init",
        "dream_decision_engine",
        "broadcast_strategy",
        "commit_decision",
        "check_auth_status",
    ],
    constraints=[
        "Focus on company-level decision proposals and resource allocation.",
        "Do not directly alter staff reports; use decision and task APIs.",
        "TODO(徐少洋): Replace placeholder Dream input/output with final contract.",
        "TODO(熊锦文): Confirm decision/commit request body and task_queue rules.",
    ],
)


AGENT_TEMPLATES = {
    "base": BASE_TEMPLATE,
    "line_worker": STAFF_TEMPLATE,
    "staff": STAFF_TEMPLATE,
    "manager": MANAGER_TEMPLATE,
    "executive": EXECUTIVE_TEMPLATE,
}


def get_agent_template(name: str) -> AgentTemplateSpec:
    return AGENT_TEMPLATES[name]
