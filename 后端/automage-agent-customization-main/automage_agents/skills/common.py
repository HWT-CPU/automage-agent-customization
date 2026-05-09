from __future__ import annotations

from automage_agents.core.models import SkillResult
from automage_agents.skills.context import SkillContext
from automage_agents.skills.result import api_response_to_skill_result


def agent_init(context: SkillContext) -> SkillResult:
    response = context.api_client.agent_init(context.identity, context.runtime_payload())
    return api_response_to_skill_result(response, "agent initialized")


def check_auth_status(context: SkillContext) -> SkillResult:
    # TODO(熊锦文): 如后端提供独立 auth_status 接口，替换为真实轮询接口。
    response = context.api_client.agent_init(context.identity, context.runtime_payload())
    result = api_response_to_skill_result(response, "auth status active")
    if result.ok:
        result.data.setdefault("auth_status", "active")
    return result


def load_user_profile(context: SkillContext) -> SkillResult:
    return SkillResult(ok=True, data=context.user_profile.to_dict(), message="user profile loaded")
