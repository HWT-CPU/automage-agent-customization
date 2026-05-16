from __future__ import annotations

from typing import Any

from automage_agents.ai.analysis_service import get_analysis_service
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
    """生成 Executive 决策方案，使用 AI 生成 A/B 方案"""
    payload = _to_payload(dream_input)
    ensure_feishu_knowledge_for_payload(context.runtime, payload, "dream_decision_engine", context.identity.role.value)
    runtime_payload = context.runtime_payload()
    payload = enrich_business_payload_with_knowledge(payload, runtime_payload, "dream_input")
    
    # 使用 AI 生成决策方案
    try:
        knowledge_context = _extract_knowledge_context(context)
        analysis_service = get_analysis_service()
        
        # 生成 A/B 决策方案
        decision_result = analysis_service.generate_decision_options(
            manager_summary=payload,
            department=context.identity.department_id or "unknown",
            date=payload.get("summary_date", "today"),
            knowledge_context=knowledge_context,
        )
        
        # 将 AI 生成的决策方案合并到 payload
        if "decision_options" in decision_result:
            payload["decision_options"] = decision_result["decision_options"]
        if "recommendation" in decision_result:
            payload["recommendation"] = decision_result["recommendation"]
    except Exception as e:
        # AI 生成失败，使用默认方案
        payload.setdefault("meta", {})
        if isinstance(payload["meta"], dict):
            payload["meta"]["ai_generation_error"] = str(e)
    
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
        message="Dream decision draft generated with AI.",
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



def _extract_knowledge_context(context: SkillContext) -> str:
    """从 runtime context 中提取知识库上下文"""
    try:
        feishu_ref = context.runtime.input_refs.get("feishu_knowledge", {})
        if isinstance(feishu_ref, dict):
            return str(feishu_ref.get("context_text", ""))
    except Exception:
        pass
    return ""
