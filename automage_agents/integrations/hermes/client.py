from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from automage_agents.core.enums import AgentRole
from automage_agents.core.models import SkillResult
from automage_agents.integrations.hermes.contracts import HermesInvokeRequest, HermesInvokeResponse
from automage_agents.skills.context import SkillContext
from automage_agents.skills.registry import get_skill


@dataclass(slots=True)
class LocalHermesClient:
    staff_context: SkillContext
    manager_context: SkillContext
    executive_context: SkillContext
    skill_resolver: Callable[[str], Callable[..., Any]] = get_skill

    def invoke_skill(self, request: HermesInvokeRequest) -> HermesInvokeResponse:
        try:
            skill = self.skill_resolver(request.skill_name)
            context = self._context_for_skill(request.skill_name, request.actor_user_id)
            result = skill(context, **request.payload)
        except KeyError as exc:
            result = SkillResult(ok=False, data={"skill_name": request.skill_name}, message=f"Unknown Hermes skill: {request.skill_name}", error_code="unknown_skill")
        except TypeError as exc:
            result = SkillResult(
                ok=False,
                data={"skill_name": request.skill_name, "payload": request.payload, "error": str(exc)},
                message="Hermes skill invocation failed because the payload does not match the skill signature.",
                error_code="skill_signature_mismatch",
            )
        except Exception as exc:
            result = SkillResult(
                ok=False,
                data={"skill_name": request.skill_name, "payload": request.payload, "error": str(exc)},
                message="Hermes skill invocation failed.",
                error_code="skill_invocation_failed",
            )
        return HermesInvokeResponse(
            ok=result.ok,
            skill_name=request.skill_name,
            actor_user_id=request.actor_user_id,
            result=result,
            trace=request.trace,
        )

    def _context_for_skill(self, skill_name: str, actor_user_id: str) -> SkillContext:
        if skill_name in {"post_daily_report", "fetch_my_tasks", "update_my_task", "import_staff_daily_report_from_markdown", "read_staff_daily_report", "search_feishu_knowledge"}:
            return self.staff_context
        if skill_name in {"analyze_team_reports", "generate_manager_report", "generate_manager_schema", "delegate_task"}:
            return self.manager_context
        if skill_name in {"dream_decision_engine", "commit_decision", "broadcast_strategy"}:
            return self.executive_context
        if self.staff_context.identity.user_id == actor_user_id or self.staff_context.identity.role == AgentRole.STAFF:
            return self.staff_context
        if self.manager_context.identity.user_id == actor_user_id:
            return self.manager_context
        if self.executive_context.identity.user_id == actor_user_id:
            return self.executive_context
        return self.staff_context
