from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

from automage_agents.core.models import AgentIdentity
from automage_agents.knowledge.runtime_context import knowledge_refs_from_runtime

STAFF_SCHEMA_ID = "schema_v1_staff"
STAFF_SCHEMA_VERSION = "1.0.0"


def coerce_staff_report_v1_payload(
    payload: dict[str, Any],
    identity: AgentIdentity,
    runtime_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    runtime = runtime_context or {}
    timestamp = _timestamp(payload.get("timestamp"))
    need_support = bool(payload.get("need_support", False))
    need_decision = bool(payload.get("need_decision", False))
    issues = _issue_items(payload.get("issues_faced"))
    support_detail = str(payload.get("support_detail") or payload.get("issues_faced") or payload.get("raw_text") or "").strip()
    decision_detail = str(payload.get("decision_detail") or "").strip()
    result: dict[str, Any] = {
        "schema_id": STAFF_SCHEMA_ID,
        "schema_version": STAFF_SCHEMA_VERSION,
        "timestamp": timestamp,
        "org_id": str(payload.get("org_id") or runtime.get("org_id") or identity.metadata.get("org_id") or "org-001"),
        "department_id": str(payload.get("department_id") or identity.department_id or "dept-unknown"),
        "user_id": str(payload.get("user_id") or identity.user_id),
        "node_id": str(payload.get("node_id") or identity.node_id),
        "record_date": str(payload.get("record_date") or _record_date(timestamp)),
        "task_progress": _task_progress_items(payload.get("task_progress")),
        "work_progress": _work_progress_items(payload.get("work_progress"), payload.get("raw_text")),
        "issues_faced": issues,
        "solution_attempt": _solution_items(payload.get("solution_attempt")),
        "need_support": need_support,
        "need_decision": need_decision,
        "support_detail": support_detail if need_support else _text(payload.get("support_detail")),
        "decision_detail": decision_detail if need_decision else _text(payload.get("decision_detail")),
        "next_day_plan": _plan_items(payload.get("next_day_plan")),
        "resource_usage": _resource_usage(payload.get("resource_usage")),
        "artifacts": _artifact_items(payload.get("artifacts")),
        "related_task_ids": list(payload.get("related_task_ids", [])),
        "risk_level": _risk_level(payload, issues, need_support, need_decision),
        "employee_comment": str(payload.get("employee_comment") or payload.get("raw_text") or ""),
        "signature": _signature(payload, identity, timestamp),
        "meta": _meta(payload, runtime),
    }
    if need_support and not result["support_detail"]:
        result["support_detail"] = "需要进一步确认支持事项。"
    if need_decision and not result["decision_detail"]:
        result["decision_detail"] = support_detail or "需要进一步确认决策事项。"
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


def _title(text: str, fallback: str) -> str:
    clean = text.replace("\n", " ").strip()
    return clean[:40] or fallback


def _work_progress_items(value: Any, raw_text: Any = None) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [_work_progress_item(item) for item in value if isinstance(item, dict)] or [_work_progress_item({"description": _text(raw_text)})]
    text = _text(value) or _text(raw_text)
    return [_work_progress_item({"description": text})]


def _work_progress_item(item: dict[str, Any]) -> dict[str, Any]:
    description = _text(item.get("description") or item.get("today_result") or item.get("title"))
    return {
        "title": _text(item.get("title")) or _title(description, "今日工作进展"),
        "item_type": item.get("item_type") or "other",
        "description": description or "今日工作进展待补充。",
        "status": item.get("status") or "completed",
        "evidence": _text(item.get("evidence")),
        "artifact_ids": list(item.get("artifact_ids", [])),
        "artifact_links": list(item.get("artifact_links", [])),
        "related_module": _text(item.get("related_module")),
        "available_for_integration": bool(item.get("available_for_integration", True)),
    }


def _issue_items(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [_issue_item(item) for item in value if isinstance(item, dict)]
    text = _text(value)
    if not text:
        return []
    return [_issue_item({"description": text})]


def _issue_item(item: dict[str, Any]) -> dict[str, Any]:
    description = _text(item.get("description") or item.get("issue_title"))
    return {
        "issue_title": _text(item.get("issue_title")) or _title(description, "今日问题"),
        "description": description or "问题描述待补充。",
        "impact_scope": _text(item.get("impact_scope")),
        "severity": item.get("severity") or _severity(description),
        "is_blocking": bool(item.get("is_blocking", _contains_any(description, ["阻塞", "卡住", "无法", "不能"]))) ,
        "need_support_from": _text(item.get("need_support_from")),
    }


def _solution_items(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [_solution_item(item) for item in value if isinstance(item, dict)]
    text = _text(value)
    if not text:
        return []
    return [_solution_item({"description": text})]


def _solution_item(item: dict[str, Any]) -> dict[str, Any]:
    description = _text(item.get("description"))
    return {
        "description": description or "处理方式待补充。",
        "result": _text(item.get("result")),
        "status": item.get("status") or "pending_verify",
    }


def _plan_items(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [_plan_item(item) for item in value if isinstance(item, dict)] or [_plan_item({"title": "明日计划待补充"})]
    text = _text(value)
    return [_plan_item({"title": text or "明日计划待补充", "description": text})]


def _plan_item(item: dict[str, Any]) -> dict[str, Any]:
    title = _text(item.get("title") or item.get("description"))
    result: dict[str, Any] = {
        "title": title or "明日计划待补充",
        "description": _text(item.get("description")),
        "priority": item.get("priority") or "medium",
        "expected_output": _text(item.get("expected_output")),
    }
    if item.get("related_task_id"):
        result["related_task_id"] = item["related_task_id"]
    return result


def _task_progress_items(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [_task_progress_item(item) for item in value if isinstance(item, dict)]


def _task_progress_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": item.get("task_id") or "unknown-task",
        "task_title": _text(item.get("task_title")),
        "today_result": _text(item.get("today_result")),
        "previous_status": item.get("previous_status") or "in_progress",
        "current_status": item.get("current_status") or item.get("status") or "in_progress",
        "completion_percent": float(item.get("completion_percent", 0)),
        "need_follow_up": bool(item.get("need_follow_up", True)),
        "blocked_reason": _text(item.get("blocked_reason")),
        "remark": _text(item.get("remark")),
    }


def _artifact_items(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [_artifact_item(item) for item in value if isinstance(item, dict)]


def _artifact_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_type": item.get("artifact_type") or "other",
        "title": _text(item.get("title")) or "未命名产出物",
        "description": _text(item.get("description")),
        "url": _text(item.get("url")),
        "file_name": _text(item.get("file_name")),
        "mime_type": _text(item.get("mime_type")),
        "storage_type": item.get("storage_type") or "text",
        "version": _text(item.get("version")),
        "meta": dict(item.get("meta", {})),
    }


def _resource_usage(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, Any] = {}
    if "work_hours" in value:
        result["work_hours"] = float(value["work_hours"])
    if "tools" in value and isinstance(value["tools"], list):
        result["tools"] = [str(item) for item in value["tools"]]
    if "budget" in value:
        result["budget"] = float(value["budget"])
    if "materials" in value and isinstance(value["materials"], list):
        result["materials"] = [str(item) for item in value["materials"]]
    extras = {key: item for key, item in value.items() if key not in {"work_hours", "tools", "budget", "materials", "other"}}
    if "other" in value or extras:
        result["other"] = _text(value.get("other") or json.dumps(extras, ensure_ascii=False))
    return result


def _signature(payload: dict[str, Any], identity: AgentIdentity, timestamp: str) -> dict[str, Any]:
    existing = payload.get("signature") if isinstance(payload.get("signature"), dict) else {}
    payload_hash = existing.get("payload_hash") or hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest()
    return {
        "confirm_status": existing.get("confirm_status") or "confirmed",
        "signed_by": existing.get("signed_by") or identity.user_id,
        "signed_by_role": existing.get("signed_by_role") or identity.role.value,
        "signed_at": existing.get("signed_at") or timestamp,
        "signature_method": existing.get("signature_method") or "im_confirm",
        "payload_hash": payload_hash,
        "signature_value": existing.get("signature_value") or "",
        "comment": existing.get("comment") or "AutoMage Staff Agent v1 adapter",
    }


def _meta(payload: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_contract_source": "里程碑一_杨卓_交付v1.0.0/schema_v1_staff.json",
        "adapter": "automage_agents.schemas.staff_v1.coerce_staff_report_v1_payload",
        "source_channel": runtime.get("source_channel") or payload.get("source_channel"),
        "feishu_open_id": payload.get("feishu_open_id"),
        "feishu_event_type": payload.get("feishu_event_type"),
        "message_id": payload.get("message_id"),
        "raw_text": payload.get("raw_text"),
        "raw_resource_usage": payload.get("resource_usage"),
        "knowledge_refs": knowledge_refs_from_runtime(runtime),
        "runtime_context": runtime,
    }


def _risk_level(payload: dict[str, Any], issues: list[dict[str, Any]], need_support: bool, need_decision: bool) -> str:
    explicit = payload.get("risk_level")
    if explicit in {"low", "medium", "high", "critical"}:
        return explicit
    if need_decision:
        return "high"
    if any(item.get("severity") in {"high", "critical"} or item.get("is_blocking") for item in issues):
        return "high"
    if need_support or issues:
        return "medium"
    return "low"


def _severity(text: str) -> str:
    if _contains_any(text, ["严重", "高", "阻塞", "无法", "不能"]):
        return "high"
    if _contains_any(text, ["问题", "风险", "不确定", "还没确定"]):
        return "medium"
    return "low"


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)
