from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

from automage_agents.core.models import AgentIdentity
from automage_agents.knowledge.runtime_context import knowledge_refs_from_runtime

MANAGER_SCHEMA_ID = "schema_v1_manager"
MANAGER_SCHEMA_VERSION = "1.0.0"


def coerce_manager_report_v1_payload(
    payload: dict[str, Any],
    identity: AgentIdentity,
    runtime_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    runtime = runtime_context or {}
    timestamp = _timestamp(payload.get("timestamp"))
    source_record_ids = _id_list(payload.get("source_record_ids"))
    result: dict[str, Any] = {
        "schema_id": MANAGER_SCHEMA_ID,
        "schema_version": MANAGER_SCHEMA_VERSION,
        "timestamp": timestamp,
        "org_id": _id(payload.get("org_id") or runtime.get("org_id") or identity.metadata.get("org_id") or "org-001"),
        "dept_id": _id(payload.get("dept_id") or payload.get("department_id") or identity.department_id or "dept-unknown"),
        "manager_user_id": _id(payload.get("manager_user_id") or identity.user_id),
        "manager_node_id": _text(payload.get("manager_node_id") or identity.node_id or "manager-node-unknown"),
        "summary_date": str(payload.get("summary_date") or payload.get("record_date") or _record_date(timestamp)),
        "staff_report_count": int(payload.get("staff_report_count", len(source_record_ids))),
        "missing_report_count": int(payload.get("missing_report_count", 0)),
        "missing_staff_ids": _id_list(payload.get("missing_staff_ids")),
        "overall_health": _overall_health(payload.get("overall_health")),
        "aggregated_summary": _text(payload.get("aggregated_summary")) or "部门日报汇总待补充。",
        "top_3_risks": _risk_items(payload.get("top_3_risks")),
        "workforce_efficiency": _workforce_efficiency(payload.get("workforce_efficiency")),
        "pending_approvals": int(payload.get("pending_approvals", 0)),
        "highlight_staff": _highlight_staff_items(payload.get("highlight_staff")),
        "blocked_items": _blocked_items(payload.get("blocked_items")),
        "manager_decisions": _decision_items(payload.get("manager_decisions")),
        "need_executive_decision": _executive_decision_items(payload.get("need_executive_decision")),
        "next_day_adjustment": _adjustment_items(payload.get("next_day_adjustment")),
        "source_record_ids": source_record_ids,
        "source_task_ids": _id_list(payload.get("source_task_ids")),
        "source_incident_ids": _id_list(payload.get("source_incident_ids")),
        "signature": _signature(payload, identity, timestamp),
        "meta": _meta(payload, runtime),
    }
    return result


def _timestamp(value: Any) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return datetime.now().astimezone().isoformat()


def _record_date(timestamp: str) -> str:
    if len(timestamp) >= 10:
        return timestamp[:10]
    return datetime.now().astimezone().date().isoformat()


def _text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if value is None:
        return ""
    return str(value).strip()


def _id(value: Any) -> int | str:
    if isinstance(value, int) and value >= 1:
        return value
    text = _text(value)
    return text or "unknown-id"


def _id_list(value: Any) -> list[int | str]:
    if not isinstance(value, list):
        return []
    result: list[int | str] = []
    seen: set[str] = set()
    for item in value:
        candidate = _id(item)
        key = str(candidate)
        if key != "unknown-id" and key not in seen:
            result.append(candidate)
            seen.add(key)
    return result


def _overall_health(value: Any) -> str:
    text = _text(value)
    if text in {"green", "yellow", "red"}:
        return text
    return "yellow"


def _risk_items(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [_risk_item(item) for item in value[:3]]
    text = _text(value)
    if not text:
        return []
    return [_risk_item(text)]


def _risk_item(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        title = _text(value.get("risk_title") or value.get("title") or value.get("description"))
        return {
            "risk_title": title or "未命名风险",
            "description": _text(value.get("description")),
            "severity": _severity(value.get("severity")),
            "source_type": _text(value.get("source_type")),
            "suggested_action": _text(value.get("suggested_action")),
            "need_escalation": bool(value.get("need_escalation", _severity(value.get("severity")) in {"high", "critical"})),
        }
    text = _text(value)
    return {
        "risk_title": text or "未命名风险",
        "description": text,
        "severity": _severity(text),
        "source_type": "staff_report",
        "suggested_action": "由 Manager Agent 继续跟进。",
        "need_escalation": _severity(text) in {"high", "critical"},
    }


def _severity(value: Any) -> str:
    text = _text(value)
    if text in {"low", "medium", "high", "critical"}:
        return text
    if any(keyword in text for keyword in ["严重", "阻塞", "无法", "高"]):
        return "high"
    if any(keyword in text for keyword in ["风险", "问题", "不足", "等待", "不确定"]):
        return "medium"
    return "medium"


def _workforce_efficiency(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        score = _score(value.get("score", 0))
        return {
            "score": score,
            "level": value.get("level") if value.get("level") in {"low", "medium", "high"} else _efficiency_level(score),
            "explanation": _text(value.get("explanation")),
        }
    score = _score(value)
    return {"score": score, "level": _efficiency_level(score), "explanation": "由当前 demo 输入换算。"}


def _score(value: Any) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0
    if 0 <= score <= 1:
        score *= 100
    return max(0.0, min(score, 100.0))


def _efficiency_level(score: float) -> str:
    if score >= 80:
        return "high"
    if score >= 50:
        return "medium"
    return "low"


def _highlight_staff_items(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        items.append(
            {
                "user_id": _id(item.get("user_id")),
                "display_name": _text(item.get("display_name")),
                "reason": _text(item.get("reason")) or "表现突出。",
                "evidence_record_ids": _id_list(item.get("evidence_record_ids")),
            }
        )
    return items


def _blocked_items(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        title = _text(item.get("title") or item.get("description"))
        items.append(
            {
                "title": title or "未命名阻塞项",
                "description": _text(item.get("description")),
                "severity": _severity(item.get("severity")),
                "source_record_ids": _id_list(item.get("source_record_ids")),
                "need_executive_decision": bool(item.get("need_executive_decision", False)),
                "suggested_action": _text(item.get("suggested_action")),
            }
        )
    return items


def _decision_items(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        title = _text(item.get("decision_title") or item.get("title"))
        items.append(
            {
                "decision_title": title or "未命名经理决策",
                "decision_level": item.get("decision_level") if item.get("decision_level") in {"L0", "L1", "L2", "L3", "L4"} else "L2",
                "background": _text(item.get("background")),
                "handled_by": _id(item.get("handled_by")),
                "result": _text(item.get("result")),
                "status": item.get("status") if item.get("status") in {"draft", "pending", "confirmed", "rejected", "executed", "cancelled"} else "draft",
                "source_record_ids": _id_list(item.get("source_record_ids")),
            }
        )
    return items


def _executive_decision_items(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        title = _text(item.get("decision_title") or item.get("title"))
        background = _text(item.get("background"))
        items.append(
            {
                "decision_title": title or "未命名上升决策",
                "background": background or title or "上升决策背景待补充。",
                "reason_to_escalate": _text(item.get("reason_to_escalate")),
                "risk_level": _severity(item.get("risk_level")),
                "option_a": _option_value(item.get("option_a")),
                "option_b": _option_value(item.get("option_b")),
                "recommended_option": _text(item.get("recommended_option")),
                "expected_impact": _impact_value(item.get("expected_impact")),
                "source_record_ids": _id_list(item.get("source_record_ids")),
            }
        )
    return items


def _option_value(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    text = _text(value)
    if not text:
        return {}
    return {"description": text}


def _impact_value(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    text = _text(value)
    if not text:
        return {}
    return {"summary": text}


def _adjustment_items(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        title = _text(item.get("title") or item.get("description"))
        priority = item.get("priority") if item.get("priority") in {"low", "medium", "high", "critical"} else "medium"
        items.append(
            {
                "title": title or "未命名明日调整",
                "description": _text(item.get("description")),
                "target_role": _text(item.get("target_role")),
                "priority": priority,
                "expected_output": _text(item.get("expected_output")),
            }
        )
    return items


def _signature(payload: dict[str, Any], identity: AgentIdentity, timestamp: str) -> dict[str, Any]:
    existing = payload.get("signature") if isinstance(payload.get("signature"), dict) else {}
    payload_hash = existing.get("payload_hash") or hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest()
    return {
        "confirm_status": existing.get("confirm_status") or "confirmed",
        "signed_by": existing.get("signed_by") or identity.user_id,
        "signed_by_role": existing.get("signed_by_role") or identity.role.value,
        "signed_at": existing.get("signed_at") or timestamp,
        "signature_method": existing.get("signature_method") or "system",
        "payload_hash": payload_hash,
        "signature_value": existing.get("signature_value") or "",
        "comment": existing.get("comment") or "AutoMage Manager Agent v1 adapter",
    }


def _meta(payload: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_contract_source": "里程碑一_杨卓_交付v1.0.0/schema_v1_manager.json",
        "adapter": "automage_agents.schemas.manager_v1.coerce_manager_report_v1_payload",
        "knowledge_refs": knowledge_refs_from_runtime(runtime),
        "runtime_context": runtime,
        "legacy_payload": payload,
    }
