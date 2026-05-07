from __future__ import annotations

from typing import Any

from automage_agents.core.models import SkillResult
from automage_agents.knowledge.auto_context import ensure_feishu_knowledge_for_payload
from automage_agents.knowledge.payload_enrichment import enrich_business_payload_with_knowledge
from automage_agents.knowledge.runtime_context import knowledge_refs_from_runtime
from automage_agents.schemas.placeholders import DREAM_DECISION_SCHEMA_ID, DreamDecisionDraft
from automage_agents.skills.context import SkillContext
from automage_agents.skills.result import api_response_to_skill_result


def dream_decision_engine(context: SkillContext, dream_input: DreamDecisionDraft | dict[str, Any]) -> SkillResult:
    payload = _to_payload(dream_input)
    ensure_feishu_knowledge_for_payload(context.runtime, payload, "dream_decision_engine", context.identity.role.value)
    runtime_payload = context.runtime_payload()
    payload = enrich_business_payload_with_knowledge(payload, runtime_payload, "dream_input")
    summary_id = payload.get("summary_id") or payload.get("source_summary_id")
    if summary_id:
        response = context.api_client.run_dream(context.identity, str(summary_id))
        return api_response_to_skill_result(response, "dream decision draft generated")

    return SkillResult(
        ok=True,
        data={
            "schema_id": DREAM_DECISION_SCHEMA_ID,
            "input": payload,
            "knowledge_refs": knowledge_refs_from_runtime(runtime_payload),
            "runtime_context": runtime_payload,
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
    ensure_feishu_knowledge_for_payload(context.runtime, decision_payload, "commit_decision", context.identity.role.value)
    runtime_payload = context.runtime_payload()
    payload = enrich_business_payload_with_knowledge(decision_payload, runtime_payload, "decision_payload")
    meta = dict(payload.get("meta", {})) if isinstance(payload.get("meta"), dict) else {}
    meta.setdefault("knowledge_refs", knowledge_refs_from_runtime(runtime_payload))
    payload["meta"] = meta
    response = context.api_client.commit_decision(context.identity, payload, runtime_payload)
    return api_response_to_skill_result(response, "decision committed")


def broadcast_strategy(context: SkillContext, decision_payload: dict[str, Any]) -> SkillResult:
    # TODO(OpenClaw): 老板确认后的飞书群内广播应由 OpenClaw / Feishu 适配层发送。
    return commit_decision(context, decision_payload)


def _to_payload(dream_input: DreamDecisionDraft | dict[str, Any]) -> dict[str, Any]:
    if isinstance(dream_input, DreamDecisionDraft):
        return dream_input.to_payload()
    return dict(dream_input)
