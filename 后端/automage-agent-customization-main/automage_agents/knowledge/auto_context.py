from __future__ import annotations

import re
from typing import Any

from automage_agents.core.models import RuntimeContextV0
from automage_agents.knowledge.runtime_context import FEISHU_KNOWLEDGE_INPUT_REF_KEY, attach_feishu_knowledge_to_runtime


SKILL_QUERY_HINTS = {
    "post_daily_report": ["Staff 日报模板", "schema_v1_staff", "日报", "工作记录"],
    "import_staff_daily_report_from_markdown": ["Staff 日报模板", "schema_v1_staff", "日报", "Markdown"],
    "generate_manager_report": ["Manager 汇总", "schema_v1_manager", "部门汇总", "风险", "日报汇总"],
    "generate_manager_schema": ["Manager 汇总", "schema_v1_manager", "部门汇总", "风险", "日报汇总"],
    "dream_decision_engine": ["Executive 决策", "Dream 决策", "任务下发", "决策记录"],
    "commit_decision": ["Executive 决策", "decision commit", "任务下发", "决策记录"],
}

TEXT_FIELD_PRIORITY = [
    "query",
    "requested_query",
    "raw_text",
    "work_progress",
    "issues_faced",
    "solution_attempt",
    "next_day_plan",
    "aggregated_summary",
    "top_3_risks",
    "blocked_items",
    "manager_decisions",
    "need_executive_decision",
    "stage_goal",
    "decision_summary",
    "title",
    "description",
    "expected_output",
]

SKIP_TEXT_KEYS = {
    "schema_id",
    "schema_version",
    "timestamp",
    "record_date",
    "summary_date",
    "org_id",
    "dept_id",
    "department_id",
    "user_id",
    "node_id",
    "manager_user_id",
    "manager_node_id",
    "source_record_ids",
    "source_task_ids",
    "source_incident_ids",
    "signature",
    "meta",
    "runtime_context",
    "knowledge_refs",
}


def ensure_feishu_knowledge_for_payload(
    runtime: RuntimeContextV0,
    payload: dict[str, Any],
    skill_name: str,
    role: str,
    cache_dir: str = "_cache/feishu_wiki",
    limit: int = 3,
    max_context_chars: int = 3000,
) -> dict[str, Any]:
    existing = runtime.input_refs.get(FEISHU_KNOWLEDGE_INPUT_REF_KEY)
    if isinstance(existing, dict) and existing.get("context_text"):
        return {
            "attached": False,
            "reason": "existing_context",
            "query": str(existing.get("query") or ""),
            "source_count": len(existing.get("sources", [])) if isinstance(existing.get("sources"), list) else 0,
        }
    query = build_auto_feishu_knowledge_query(payload, skill_name=skill_name, role=role, workflow_stage=runtime.workflow_stage)
    if not query:
        return {"attached": False, "reason": "empty_query", "query": "", "source_count": 0}
    context_block = attach_feishu_knowledge_to_runtime(
        runtime=runtime,
        query=query,
        cache_dir=cache_dir,
        limit=limit,
        max_context_chars=max_context_chars,
    )
    feishu_ref = runtime.input_refs.get(FEISHU_KNOWLEDGE_INPUT_REF_KEY)
    if isinstance(feishu_ref, dict):
        feishu_ref["auto_retrieved"] = True
        feishu_ref["auto_skill_name"] = skill_name
        feishu_ref["auto_role"] = role
    return {
        "attached": True,
        "reason": "auto_retrieved",
        "query": query,
        "source_count": len(context_block.sources),
    }


def build_auto_feishu_knowledge_query(payload: dict[str, Any], skill_name: str, role: str, workflow_stage: str = "") -> str:
    parts: list[str] = []
    text_fragments = _payload_text_fragments(payload)
    parts.extend(text_fragments)
    if not text_fragments:
        parts.extend(SKILL_QUERY_HINTS.get(skill_name, []))
    parts.extend([role, workflow_stage, skill_name])
    return _compact_query(" ".join(part for part in parts if part))


def _payload_text_fragments(payload: dict[str, Any]) -> list[str]:
    fragments: list[str] = []
    for key in TEXT_FIELD_PRIORITY:
        if key in payload:
            _collect_text(payload[key], fragments)
    for key, value in payload.items():
        if key not in TEXT_FIELD_PRIORITY:
            _collect_text(value, fragments, key)
    return fragments[:12]


def _collect_text(value: Any, fragments: list[str], key: str = "") -> None:
    if len(fragments) >= 12:
        return
    if key in SKIP_TEXT_KEYS:
        return
    if isinstance(value, str):
        text = value.strip()
        if _is_semantic_text(text):
            fragments.append(text[:120])
        return
    if isinstance(value, dict):
        for field in TEXT_FIELD_PRIORITY:
            if field in value:
                _collect_text(value[field], fragments, field)
                if len(fragments) >= 12:
                    return
        for item_key, item in value.items():
            if item_key in TEXT_FIELD_PRIORITY:
                continue
            _collect_text(item, fragments, item_key)
            if len(fragments) >= 12:
                return
        return
    if isinstance(value, list):
        for item in value:
            _collect_text(item, fragments, key)
            if len(fragments) >= 12:
                return


def _compact_query(query: str) -> str:
    return re.sub(r"\s+", " ", query).strip()[:500]


def _is_semantic_text(text: str) -> bool:
    if not text:
        return False
    if len(text) <= 80 and all(character.isascii() and (character.isalnum() or character in "_-:.+/\\") for character in text):
        return False
    return True
