from __future__ import annotations

from typing import Any

from automage_agents.core.models import SkillResult
from automage_agents.knowledge.auto_context import ensure_feishu_knowledge_for_payload
from automage_agents.knowledge.payload_enrichment import enrich_business_payload_with_knowledge
from automage_agents.knowledge.runtime_context import knowledge_refs_from_runtime
from automage_agents.schemas.executive_v1 import (
    coerce_decision_commit_payload,
    coerce_executive_decision_card_payload,
    decision_options_from_executive_card,
)
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
        result = api_response_to_skill_result(response, "dream decision draft generated")
        if result.ok:
            result.data = _with_executive_contract({**payload, **result.data}, context, runtime_payload)
        return result

    data = _with_executive_contract(payload, context, runtime_payload)
    return SkillResult(
        ok=True,
        data=data,
        message="Dream decision draft generated.",
    )


def commit_decision(context: SkillContext, decision_payload: dict[str, Any]) -> SkillResult:
    ensure_feishu_knowledge_for_payload(context.runtime, decision_payload, "commit_decision", context.identity.role.value)
    runtime_payload = context.runtime_payload()
    payload = enrich_business_payload_with_knowledge(decision_payload, runtime_payload, "decision_payload")
    payload = coerce_decision_commit_payload(payload, context.identity, runtime_payload)
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


def _with_executive_contract(payload: dict[str, Any], context: SkillContext, runtime_payload: dict[str, Any]) -> dict[str, Any]:
    data = dict(payload)
    data.setdefault("decision_options", _default_decision_options(data))
    data.setdefault("generated_tasks", _generated_tasks_from_options(data.get("decision_options")))
    card = coerce_executive_decision_card_payload(data, context.identity, runtime_payload)
    result = dict(card)
    result["decision_options"] = decision_options_from_executive_card(card)
    if data.get("decision_options"):
        result["decision_options"] = list(data["decision_options"])
    result["input"] = payload
    result["knowledge_refs"] = knowledge_refs_from_runtime(runtime_payload)
    result["runtime_context"] = runtime_payload
    result["contract_status"] = "schema_v1_executive_ready"
    result["legacy_schema_id"] = DREAM_DECISION_SCHEMA_ID
    return result


def _default_decision_options(payload: dict[str, Any]) -> list[dict[str, Any]]:
    source_summary_id = str(payload.get("summary_id") or payload.get("source_summary_id") or "pending")
    return [
        {
            "option_id": "A",
            "title": "Conservative execution plan",
            "summary": "Prioritize confirmed tasks and reduce execution risk.",
            "task_candidates": [],
            "source_summary_id": source_summary_id,
        },
        {
            "option_id": "B",
            "title": "Aggressive execution plan",
            "summary": "Prioritize high-impact opportunities and resource reallocation.",
            "task_candidates": [],
            "source_summary_id": source_summary_id,
        },
    ]


def _generated_tasks_from_options(options: Any) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    if not isinstance(options, list):
        return tasks
    for option in options:
        if isinstance(option, dict):
            tasks.extend(task for task in option.get("task_candidates", []) if isinstance(task, dict))
    return tasks
