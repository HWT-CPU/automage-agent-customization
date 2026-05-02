from __future__ import annotations

from typing import Any

from automage_agents.core.models import SkillResult
from automage_agents.schemas.placeholders import DREAM_DECISION_SCHEMA_ID, DreamDecisionDraft
from automage_agents.skills.context import SkillContext
from automage_agents.skills.result import api_response_to_skill_result


def dream_decision_engine(context: SkillContext, dream_input: DreamDecisionDraft | dict[str, Any]) -> SkillResult:
    payload = _to_payload(dream_input)
    # TODO(徐少洋): 替换为真实 Dream 机制输入输出，当前只返回可联调的 A/B 决策草案结构。
    return SkillResult(
        ok=True,
        data={
            "schema_id": DREAM_DECISION_SCHEMA_ID,
            "input": payload,
            "decision_options": [
                {
                    "option_id": "A",
                    "title": "Conservative execution plan",
                    "summary": "Prioritize confirmed tasks and reduce execution risk.",
                    "task_candidates": [],
                },
                {
                    "option_id": "B",
                    "title": "Aggressive execution plan",
                    "summary": "Prioritize high-impact opportunities and resource reallocation.",
                    "task_candidates": [],
                },
            ],
            "contract_status": "pending_dream_confirmation",
        },
        message="Dream decision draft generated with placeholder contract.",
    )


def commit_decision(context: SkillContext, decision_payload: dict[str, Any]) -> SkillResult:
    response = context.api_client.commit_decision(context.identity, decision_payload)
    return api_response_to_skill_result(response, "decision committed")


def broadcast_strategy(context: SkillContext, decision_payload: dict[str, Any]) -> SkillResult:
    # TODO(OpenClaw): 老板确认后的飞书群内广播应由 OpenClaw / Feishu 适配层发送。
    return commit_decision(context, decision_payload)


def _to_payload(dream_input: DreamDecisionDraft | dict[str, Any]) -> dict[str, Any]:
    if isinstance(dream_input, DreamDecisionDraft):
        return dream_input.to_payload()
    return dict(dream_input)
