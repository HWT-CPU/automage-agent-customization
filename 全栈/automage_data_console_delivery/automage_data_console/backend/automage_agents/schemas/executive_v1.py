from __future__ import annotations

from datetime import datetime
from typing import Any

from automage_agents.core.models import AgentIdentity
from automage_agents.knowledge.runtime_context import knowledge_refs_from_runtime

EXECUTIVE_SCHEMA_ID = "schema_v1_executive"
EXECUTIVE_SCHEMA_VERSION = "1.0.0"
TASK_SCHEMA_ID = "schema_v1_task"
TASK_SCHEMA_VERSION = "1.0.0"


def coerce_executive_decision_card_payload(
    payload: dict[str, Any],
    identity: AgentIdentity,
    runtime_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    runtime = runtime_context or {}
    timestamp = _text(payload.get("timestamp")) or datetime.now().astimezone().isoformat()
    source_summary_ids = _string_list(payload.get("source_summary_ids"))
    source_summary_id = _text(payload.get("summary_id") or payload.get("source_summary_id"))
    if source_summary_id and source_summary_id not in source_summary_ids:
        source_summary_ids.append(source_summary_id)
    option_a = _option_payload(payload.get("option_a"), payload.get("decision_options"), "A")
    option_b = _option_payload(payload.get("option_b"), payload.get("decision_options"), "B")
    recommended_option = _text(payload.get("recommended_option") or payload.get("selected_option_id") or payload.get("selected_option_key")) or "A"
    confirmed_option = _text(payload.get("confirmed_option") or payload.get("selected_option_id") or payload.get("selected_option_key"))
    human_confirm_status = _text(payload.get("human_confirm_status")) or ("confirmed" if confirmed_option else "pending")
    generated_tasks = list(payload.get("generated_tasks") or payload.get("task_candidates") or [])
    card = {
        "schema_id": EXECUTIVE_SCHEMA_ID,
        "schema_version": _text(payload.get("schema_version")) or EXECUTIVE_SCHEMA_VERSION,
        "timestamp": timestamp,
        "org_id": _text(payload.get("org_id") or runtime.get("org_id") or identity.metadata.get("org_id")) or "org-001",
        "executive_user_id": _text(payload.get("executive_user_id") or payload.get("user_id")) or identity.user_id,
        "executive_node_id": _text(payload.get("executive_node_id") or payload.get("node_id")) or identity.node_id,
        "summary_date": _text(payload.get("summary_date") or payload.get("record_date")) or _date_from_timestamp(timestamp),
        "business_summary": _text(payload.get("business_summary") or payload.get("decision_summary") or payload.get("summary")) or "待高层确认的业务摘要。",
        "key_risks": list(payload.get("key_risks") or payload.get("risks") or []),
        "decision_required": bool(payload.get("decision_required", True)),
        "decision_items": _decision_items(payload, option_a, option_b, recommended_option),
        "option_a": option_a,
        "option_b": option_b,
        "recommended_option": recommended_option,
        "reasoning_summary": _text(payload.get("reasoning_summary") or payload.get("decision_summary")) or "基于 Manager 汇总和当前风险，建议优先选择可落地的执行方案。",
        "expected_impact": _expected_impact(payload),
        "generated_tasks": generated_tasks,
        "source_summary_ids": source_summary_ids,
        "source_decision_ids": _string_list(payload.get("source_decision_ids")),
        "source_incident_ids": _string_list(payload.get("source_incident_ids")),
        "human_confirm_status": human_confirm_status,
        "confirmed_by": payload.get("confirmed_by"),
        "confirmed_at": payload.get("confirmed_at"),
        "confirmed_option": confirmed_option,
        "signature": _signature(payload, identity, timestamp, human_confirm_status),
        "meta": _meta(payload, runtime),
    }
    return card


def decision_options_from_executive_card(card: dict[str, Any]) -> list[dict[str, Any]]:
    options: list[dict[str, Any]] = []
    for key in ["A", "B"]:
        option = card.get(f"option_{key.lower()}")
        if isinstance(option, dict):
            options.append(
                {
                    "option_id": option.get("option_id") or key,
                    "title": option.get("title") or f"方案 {key}",
                    "summary": option.get("description") or option.get("summary") or "",
                    "task_candidates": list(option.get("task_candidates") or []),
                }
            )
    return options


def coerce_decision_commit_payload(
    payload: dict[str, Any],
    identity: AgentIdentity,
    runtime_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    runtime = runtime_context or {}
    result = dict(payload)
    result.setdefault("org_id", _text(runtime.get("org_id") or identity.metadata.get("org_id")) or "org-001")
    result.setdefault("department_id", identity.department_id)
    source_summary_ids = _string_list(result.get("source_summary_ids"))
    if result.get("summary_id") and str(result["summary_id"]) not in source_summary_ids:
        source_summary_ids.append(str(result["summary_id"]))
    if not result.get("summary_id") and source_summary_ids:
        result["summary_id"] = source_summary_ids[0]
    if source_summary_ids:
        result["source_summary_ids"] = source_summary_ids
    card = coerce_executive_decision_card_payload(result, identity, runtime)
    result.setdefault("schema_id", EXECUTIVE_SCHEMA_ID)
    result.setdefault("schema_version", EXECUTIVE_SCHEMA_VERSION)
    result.setdefault("decision_options", decision_options_from_executive_card(card))
    result.setdefault("selected_option_id", result.get("confirmed_option") or card.get("confirmed_option") or card.get("recommended_option"))
    result.setdefault("selected_option_label", f"方案 {result.get('selected_option_id')}")
    result.setdefault("decision_summary", card["reasoning_summary"])
    result.setdefault("title", card["business_summary"][:80])
    result.setdefault("priority", "high")
    task_candidates = list(result.get("task_candidates") or result.get("generated_tasks") or card.get("generated_tasks") or [])
    result["task_candidates"] = [
        coerce_task_v1_payload(task, identity, runtime, decision_payload=result, index=index)
        for index, task in enumerate(task_candidates, start=1)
    ]
    meta = dict(result.get("meta") or {})
    meta.setdefault("executive_card", card)
    meta.setdefault("knowledge_refs", knowledge_refs_from_runtime(runtime))
    result["meta"] = meta
    return result


def coerce_task_v1_payload(
    task: dict[str, Any],
    identity: AgentIdentity,
    runtime_context: dict[str, Any] | None = None,
    *,
    decision_payload: dict[str, Any] | None = None,
    index: int = 1,
) -> dict[str, Any]:
    runtime = runtime_context or {}
    decision = decision_payload or {}
    source_summary_id = _text(task.get("source_summary_id") or decision.get("summary_id") or decision.get("source_summary_id"))
    source_decision_id = _text(task.get("source_decision_id") or decision.get("source_decision_id") or decision.get("decision_id"))
    source_id = _text(task.get("source_id") or source_decision_id or source_summary_id)
    task_id = _text(task.get("task_id")) or _generated_task_id(source_id, index)
    meta = dict(task.get("meta") or {})
    meta.setdefault("source_payload_keys", sorted(task.keys()))
    return {
        "schema_id": TASK_SCHEMA_ID,
        "schema_version": _text(task.get("schema_version")) or TASK_SCHEMA_VERSION,
        "task_id": task_id,
        "org_id": _text(task.get("org_id") or decision.get("org_id") or runtime.get("org_id") or identity.metadata.get("org_id")) or "org-001",
        "department_id": _text(task.get("department_id") or decision.get("department_id") or identity.department_id),
        "task_title": _text(task.get("task_title") or task.get("title")) or "高层决策执行任务",
        "task_description": _text(task.get("task_description") or task.get("description")) or "根据高层确认决策自动生成。",
        "source_type": _text(task.get("source_type") or decision.get("source_type")) or "executive_decision",
        "source_id": source_id,
        "source_summary_id": source_summary_id,
        "source_decision_id": source_decision_id,
        "creator_user_id": _text(task.get("creator_user_id") or decision.get("creator_user_id")) or identity.user_id,
        "created_by_node_id": _text(task.get("created_by_node_id") or decision.get("created_by_node_id")) or identity.node_id,
        "assignee_user_id": _text(task.get("assignee_user_id")) or identity.user_id,
        "assignee_role": _text(task.get("assignee_role")) or "staff",
        "assignment_type": _text(task.get("assignment_type")) or "owner",
        "priority": _text(task.get("priority")) or "high",
        "status": _text(task.get("status")) or "pending",
        "due_at": task.get("due_at"),
        "artifacts": list(task.get("artifacts") or []),
        "confirm_required": bool(task.get("confirm_required", False)),
        "meta": meta,
    }


def _decision_items(payload: dict[str, Any], option_a: dict[str, Any], option_b: dict[str, Any], recommended_option: str) -> list[dict[str, Any]]:
    existing = payload.get("decision_items")
    if isinstance(existing, list) and existing:
        return existing
    return [
        {
            "decision_id": _text(payload.get("decision_id")) or "DEC-AUTOMAGE-001",
            "decision_title": _text(payload.get("title") or payload.get("decision_title")) or "确认执行方案",
            "background": _text(payload.get("business_summary") or payload.get("decision_summary")) or "来自 Manager 汇总的待确认事项。",
            "decision_level": "L3",
            "risk_level": _text(payload.get("risk_level")) or "medium",
            "options": [option_a, option_b],
            "recommended_option": recommended_option,
            "reasoning_summary": _text(payload.get("reasoning_summary") or payload.get("decision_summary")) or "优先选择能闭合主链路的方案。",
            "expected_impact": _expected_impact(payload),
        }
    ]


def _option_payload(raw_option: Any, decision_options: Any, option_id: str) -> dict[str, Any]:
    if isinstance(raw_option, dict):
        result = dict(raw_option)
        result.setdefault("option_id", option_id)
        result.setdefault("title", f"方案 {option_id}")
        result.setdefault("description", result.get("summary") or "")
        return result
    if isinstance(decision_options, list):
        for option in decision_options:
            if isinstance(option, dict) and str(option.get("option_id") or option.get("key") or "").upper() == option_id:
                return {
                    "option_id": option_id,
                    "title": _text(option.get("title") or option.get("label")) or f"方案 {option_id}",
                    "description": _text(option.get("summary") or option.get("description")),
                    "task_candidates": list(option.get("task_candidates") or []),
                }
    return {"option_id": option_id, "title": f"方案 {option_id}", "description": "", "task_candidates": []}


def _expected_impact(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("expected_impact")
    if isinstance(value, dict):
        return dict(value)
    return {
        "summary": _text(value or payload.get("decision_summary")) or "确认后将生成执行任务并进入后续跟踪。",
        "impact_level": _text(payload.get("impact_level")) or "medium",
        "target_date": payload.get("target_date"),
    }


def _signature(payload: dict[str, Any], identity: AgentIdentity, timestamp: str, confirm_status: str) -> dict[str, Any]:
    existing = payload.get("signature") if isinstance(payload.get("signature"), dict) else {}
    return {
        "confirm_status": existing.get("confirm_status") or confirm_status,
        "signed_by": existing.get("signed_by") or identity.user_id,
        "signed_by_role": existing.get("signed_by_role") or identity.role.value,
        "signed_at": existing.get("signed_at") or timestamp,
        "signature_method": existing.get("signature_method") or "executive_confirm",
        "signature_value": existing.get("signature_value") or "",
    }


def _meta(payload: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    meta = dict(payload.get("meta") or {})
    meta.setdefault("adapter", "automage_agents.schemas.executive_v1")
    meta.setdefault("knowledge_refs", knowledge_refs_from_runtime(runtime))
    return meta


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if value is None:
        return []
    text = str(value).strip()
    return [text] if text else []


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _date_from_timestamp(timestamp: str) -> str:
    return timestamp[:10] if len(timestamp) >= 10 else datetime.now().astimezone().date().isoformat()


def _generated_task_id(source_id: str, index: int) -> str:
    normalized = source_id.replace(" ", "-") if source_id else "AUTOMAGE"
    return f"TASK-{normalized}-{index}"
