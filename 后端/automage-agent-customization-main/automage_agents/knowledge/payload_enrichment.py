from __future__ import annotations

from copy import deepcopy
from typing import Any

from automage_agents.knowledge.runtime_context import FEISHU_KNOWLEDGE_INPUT_REF_KEY, knowledge_refs_from_runtime


def enrich_business_payload_with_knowledge(payload: dict[str, Any], runtime_context: dict[str, Any], target: str) -> dict[str, Any]:
    knowledge_refs = knowledge_refs_from_runtime(runtime_context)
    if FEISHU_KNOWLEDGE_INPUT_REF_KEY not in knowledge_refs:
        return dict(payload)
    result = deepcopy(payload)
    if target == "staff_report":
        _enrich_staff_report(result, knowledge_refs)
    elif target == "manager_report":
        _enrich_manager_report(result, knowledge_refs)
    elif target == "dream_input":
        _enrich_dream_input(result, knowledge_refs)
    elif target == "decision_payload":
        _enrich_decision_payload(result, knowledge_refs)
    return result


def _enrich_staff_report(payload: dict[str, Any], knowledge_refs: dict[str, Any]) -> None:
    artifacts = payload.setdefault("artifacts", [])
    if not isinstance(artifacts, list):
        artifacts = []
        payload["artifacts"] = artifacts
    if _has_knowledge_artifact(artifacts):
        return
    feishu_ref = knowledge_refs[FEISHU_KNOWLEDGE_INPUT_REF_KEY]
    artifacts.append(
        {
            "artifact_type": "context",
            "title": _title_from_ref(feishu_ref, "Feishu 知识库上下文"),
            "description": _description_from_ref(feishu_ref),
            "storage_type": "text",
            "meta": {
                "knowledge_ref_key": FEISHU_KNOWLEDGE_INPUT_REF_KEY,
                "knowledge_refs": knowledge_refs,
            },
        }
    )


def _enrich_manager_report(payload: dict[str, Any], knowledge_refs: dict[str, Any]) -> None:
    adjustments = payload.setdefault("next_day_adjustment", [])
    if not isinstance(adjustments, list):
        adjustments = []
        payload["next_day_adjustment"] = adjustments
    if any(isinstance(item, dict) and item.get("title") == "按知识库资料校准执行口径" for item in adjustments):
        return
    feishu_ref = knowledge_refs[FEISHU_KNOWLEDGE_INPUT_REF_KEY]
    adjustments.append(
        {
            "title": "按知识库资料校准执行口径",
            "description": _description_from_ref(feishu_ref),
            "target_role": "manager",
            "priority": "medium",
            "expected_output": "后续汇总、任务拆分和风险判断引用同一知识库来源。",
        }
    )


def _enrich_dream_input(payload: dict[str, Any], knowledge_refs: dict[str, Any]) -> None:
    external_variables = payload.setdefault("external_variables", {})
    if not isinstance(external_variables, dict):
        external_variables = {}
        payload["external_variables"] = external_variables
    external_variables.setdefault("knowledge_refs", knowledge_refs)
    feishu_ref = knowledge_refs[FEISHU_KNOWLEDGE_INPUT_REF_KEY]
    external_variables.setdefault("knowledge_context_query", feishu_ref.get("query", ""))
    external_variables.setdefault("knowledge_source_titles", _source_titles(feishu_ref))


def _enrich_decision_payload(payload: dict[str, Any], knowledge_refs: dict[str, Any]) -> None:
    meta = dict(payload.get("meta", {})) if isinstance(payload.get("meta"), dict) else {}
    meta.setdefault("knowledge_refs", knowledge_refs)
    payload["meta"] = meta
    task_candidates = payload.get("task_candidates")
    if not isinstance(task_candidates, list):
        return
    for task in task_candidates:
        if not isinstance(task, dict):
            continue
        task_meta = dict(task.get("meta", {})) if isinstance(task.get("meta"), dict) else {}
        task_meta.setdefault("knowledge_refs", knowledge_refs)
        task["meta"] = task_meta


def _has_knowledge_artifact(artifacts: list[Any]) -> bool:
    for item in artifacts:
        if not isinstance(item, dict):
            continue
        meta = item.get("meta", {})
        if isinstance(meta, dict) and meta.get("knowledge_ref_key") == FEISHU_KNOWLEDGE_INPUT_REF_KEY:
            return True
    return False


def _title_from_ref(feishu_ref: dict[str, Any], fallback: str) -> str:
    query = str(feishu_ref.get("query") or "").strip()
    return f"{fallback}: {query[:60]}" if query else fallback


def _description_from_ref(feishu_ref: dict[str, Any]) -> str:
    titles = _source_titles(feishu_ref)
    if titles:
        return "参考 Feishu 知识库来源：" + "、".join(titles)
    query = str(feishu_ref.get("query") or "").strip()
    return f"参考 Feishu 知识库查询：{query}" if query else "参考 Feishu 知识库自动检索上下文。"


def _source_titles(feishu_ref: dict[str, Any]) -> list[str]:
    sources = feishu_ref.get("sources", [])
    if not isinstance(sources, list):
        return []
    titles: list[str] = []
    for source in sources:
        if not isinstance(source, dict):
            continue
        title = str(source.get("title") or "").strip()
        if title and title not in titles:
            titles.append(title)
    return titles[:5]
