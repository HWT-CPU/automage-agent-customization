from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


SECTION_HEADER_RE = re.compile(r"^##\s*(?:(\d+)\.)?\s*(.*)$")

SECTION_TITLE_ALIASES = {
    0: {"basicinfo", "基础信息", "基本信息"},
    1: {"todaytaskprogress", "今日任务进展", "今日任务进度", "任务进展"},
    2: {"todaycompleteditems", "今日完成事项", "今日完成项", "完成事项"},
    3: {"todayartifacts", "今日产出物", "今日交付物", "产出物"},
    4: {"todayblockers", "今日阻塞", "今日问题", "问题阻塞", "阻塞问题"},
    5: {"supportrequests", "支持请求", "需要支持", "支持事项"},
    6: {"decisionrequests", "决策请求", "需要决策", "决策事项"},
    7: {"tomorrowplans", "明日计划", "明天计划", "下一步计划"},
    8: {"crossmodulerequests", "跨模块请求", "跨部门请求", "协作请求"},
    9: {"riskassessment", "风险评估", "今日风险", "风险判断"},
    10: {"contextpromptworkflownotes", "上下文提示工作流备注", "工作流备注", "上下文备注"},
    11: {"dailysummary", "日报总结", "每日总结", "今日总结"},
    12: {"signoff", "签署确认", "确认签字", "提交确认"},
}


BASIC_INFO_ALIASES = {
    "report_date": {"日报日期", "report_date"},
    "submitted_by": {"提交人", "submitted_by"},
    "project_name": {"所属项目", "project_name"},
    "role_name": {"所属角色", "role_name"},
    "responsibility_module": {"负责模块", "responsibility_module"},
    "work_types": {"今日工作类型", "work_types"},
    "report_status": {"日报状态", "report_status"},
    "submitted_at": {"提交时间", "submitted_at"},
    "self_confirmed": {"本人确认", "self_confirmed"},
    "schema_id_ref": {"schema id", "schema_id", "schema_id_ref"},
    "schema_version_ref": {"schema版本", "schema_version", "schema_version_ref"},
    "org_id": {"组织id", "org_id"},
    "department_or_project_group": {"部门/项目组", "department_or_project_group"},
    "user_id": {"用户id", "user_id"},
    "agent_node_id": {"agent节点id", "agent_node_id"},
    "submission_channel": {"填报渠道", "submission_channel"},
    "related_template_name": {"关联日报模板", "related_template_name"},
}

RISK_ALIASES = {
    "overall_risk_level": {"今日整体风险等级", "overall_risk_level"},
    "primary_risk_sources": {"主要风险来源", "primary_risk_sources"},
    "impacted_deliverables": {"可能影响的交付物", "impacted_deliverables"},
    "impacted_workflow_nodes": {"可能影响的流程节点", "impacted_workflow_nodes"},
    "suggested_mitigation": {"建议处理方式", "suggested_mitigation"},
    "needs_escalation": {"是否需要上推", "needs_escalation"},
    "escalation_targets": {"上推对象", "escalation_targets"},
}

SUMMARY_ALIASES = {
    "most_important_progress": {"今日最重要进展", "most_important_progress"},
    "biggest_issue": {"今日最大问题", "biggest_issue"},
    "top_priority_tomorrow": {"明日最优先事项", "top_priority_tomorrow"},
    "team_attention_items": {"需要团队注意的事项", "team_attention_items"},
}

SIGN_OFF_ALIASES = {
    "submitter_confirmation_text": {"提交人确认", "submitter_confirmation_text"},
    "confirmation_status": {"确认状态", "confirmation_status"},
    "confirmed_by": {"确认人", "confirmed_by"},
    "confirmed_at": {"确认时间", "confirmed_at"},
}


def parse_staff_daily_report_file(path: str | Path, *, include_source_markdown: bool = True) -> dict[str, Any]:
    report_path = Path(path)
    content = _decode_markdown_bytes(report_path.read_bytes())
    return parse_staff_daily_report_markdown(
        content,
        include_source_markdown=include_source_markdown,
    )


def parse_staff_daily_report_bytes(raw: bytes, *, include_source_markdown: bool = True) -> dict[str, Any]:
    content = _decode_markdown_bytes(raw)
    return parse_staff_daily_report_markdown(
        content,
        include_source_markdown=include_source_markdown,
    )


def parse_staff_daily_report_markdown(markdown: str, *, include_source_markdown: bool = True) -> dict[str, Any]:
    sections = _split_sections(markdown)
    report = _build_default_report(markdown if include_source_markdown else None)

    _parse_basic_info(report, sections.get(0, []))
    report["today_task_progress"] = _parse_section_rows(sections.get(1, []), _parse_task_progress_row)
    report["today_completed_items"] = _parse_section_rows(sections.get(2, []), _parse_completed_item_row)
    report["today_artifacts"] = _parse_section_rows(sections.get(3, []), _parse_artifact_row)
    report["today_blockers"] = _parse_section_rows(sections.get(4, []), _parse_blocker_row)
    report["support_requests"] = _parse_section_rows(sections.get(5, []), _parse_support_request_row)
    report["decision_requests"] = _parse_section_rows(sections.get(6, []), _parse_decision_request_row)
    report["tomorrow_plans"] = _parse_section_rows(sections.get(7, []), _parse_tomorrow_plan_row)
    report["cross_module_requests"] = _parse_section_rows(sections.get(8, []), _parse_cross_module_request_row)
    _parse_risk_assessment(report, sections.get(9, []))
    report["workflow_notes"] = _parse_section_rows(sections.get(10, []), _parse_workflow_note_row)
    _parse_daily_summary(report, sections.get(11, []))
    _parse_sign_off(report, sections.get(12, []))
    report["legacy_projection"] = build_legacy_projection(report)
    return report


def build_legacy_projection(report: dict[str, Any]) -> dict[str, Any]:
    basic_info = report["basic_info"]
    work_progress_lines = [item["today_result"] for item in report["today_task_progress"] if item["today_result"]]
    work_progress_lines.extend(
        item["completion_detail"] for item in report["today_completed_items"] if item["completion_detail"]
    )
    issues_lines = [item["issue_description"] for item in report["today_blockers"] if item["issue_description"]]
    solution_lines = [item["attempted_solution"] for item in report["today_blockers"] if item["attempted_solution"]]
    tomorrow_lines = [item["plan"] for item in report["tomorrow_plans"] if item["plan"]]

    timestamp = basic_info["submitted_at"] or f'{basic_info["report_date"]}T18:00:00+08:00'
    need_support = any(item["need_support"] for item in report["support_requests"]) or any(
        item["is_blocking"] for item in report["today_blockers"]
    )

    return {
        "schema_id": "schema_v1_staff",
        "timestamp": timestamp,
        "work_progress": "\n".join(work_progress_lines),
        "issues_faced": "\n".join(issues_lines),
        "solution_attempt": "\n".join(solution_lines),
        "need_support": need_support,
        "next_day_plan": "\n".join(tomorrow_lines),
        "resource_usage": {
            "task_count": len(report["today_task_progress"]),
            "completed_item_count": len(report["today_completed_items"]),
            "artifact_count": len(report["today_artifacts"]),
            "blocker_count": len(report["today_blockers"]),
            "decision_count": len(report["decision_requests"]),
        },
    }


def _build_default_report(source_markdown: str | None) -> dict[str, Any]:
    report = {
        "schema_id": "schema_v1_staff_daily",
        "schema_version": "v1.0.0",
        "template_name": "AutoMage_2_Staff日报模板",
        "basic_info": {
            "report_date": "",
            "submitted_by": "",
            "project_name": "AutoMage-2 MVP",
            "role_name": "",
            "responsibility_module": "",
            "work_types": [],
            "report_status": "draft",
            "submitted_at": None,
            "self_confirmed": False,
            "schema_id_ref": "schema_v1_staff",
            "schema_version_ref": "v1.0.0",
            "org_id": "",
            "department_or_project_group": "",
            "user_id": "",
            "agent_node_id": "",
            "submission_channel": "manual",
            "related_template_name": "Staff Daily Report Template",
        },
        "today_task_progress": [],
        "today_completed_items": [],
        "today_artifacts": [],
        "today_blockers": [],
        "support_requests": [],
        "decision_requests": [],
        "tomorrow_plans": [],
        "cross_module_requests": [],
        "risk_assessment": {
            "overall_risk_level": "low",
            "primary_risk_sources": [],
            "impacted_deliverables": [],
            "impacted_workflow_nodes": [],
            "suggested_mitigation": None,
            "needs_escalation": False,
            "escalation_targets": [],
        },
        "workflow_notes": [],
        "daily_summary": {
            "most_important_progress": "",
            "biggest_issue": "",
            "top_priority_tomorrow": "",
            "team_attention_items": "",
        },
        "sign_off": {
            "submitter_confirmation_text": "我确认以上内容为今日真实工作记录",
            "confirmation_status": "unconfirmed",
            "confirmed_by": None,
            "confirmed_at": None,
        },
    }
    if source_markdown is not None:
        report["source_markdown"] = source_markdown
    return report


def _parse_basic_info(report: dict[str, Any], lines: list[str]) -> None:
    table = _first_table(lines)
    if not table:
        return
    basic_info = report["basic_info"]
    for row in table[1:]:
        if len(row) < 2:
            continue
        key = _find_alias_key(row[0], BASIC_INFO_ALIASES)
        if key is None:
            continue
        value = row[1].strip()
        if key == "work_types":
            basic_info[key] = _normalize_work_types(value)
        elif key == "report_status":
            basic_info[key] = _normalize_report_status(value)
        elif key == "self_confirmed":
            basic_info[key] = _normalize_bool(value, default=False)
        elif key == "submission_channel":
            basic_info[key] = _normalize_submission_channel(value)
        elif key in {"submitted_at"}:
            basic_info[key] = value or None
        elif key in {"schema_id_ref"}:
            basic_info[key] = value or "schema_v1_staff"
        elif key in {"schema_version_ref"}:
            basic_info[key] = value or "v1.0.0"
        elif key in {"project_name"}:
            basic_info[key] = value or "AutoMage-2 MVP"
        elif key in {"related_template_name"}:
            basic_info[key] = value or "Staff Daily Report Template"
        else:
            basic_info[key] = _strip_placeholder_value(value)


def _parse_risk_assessment(report: dict[str, Any], lines: list[str]) -> None:
    table = _first_table(lines)
    if not table:
        return
    risk = report["risk_assessment"]
    for row in table[1:]:
        if len(row) < 2:
            continue
        key = _find_alias_key(row[0], RISK_ALIASES)
        if key is None:
            continue
        value = row[1].strip()
        if key == "overall_risk_level":
            risk[key] = _normalize_severity(value)
        elif key == "needs_escalation":
            risk[key] = _normalize_bool(value, default=False)
        elif key in {"primary_risk_sources", "impacted_deliverables", "escalation_targets"}:
            risk[key] = _split_text_list(value)
        elif key == "impacted_workflow_nodes":
            risk[key] = _normalize_workflow_nodes(value)
        else:
            risk[key] = _strip_placeholder_value(value) or None


def _parse_daily_summary(report: dict[str, Any], lines: list[str]) -> None:
    table = _first_table(lines)
    if not table:
        return
    summary = report["daily_summary"]
    for row in table[1:]:
        if len(row) < 2:
            continue
        key = _find_alias_key(row[0], SUMMARY_ALIASES)
        if key is None:
            continue
        summary[key] = row[1].strip()


def _parse_sign_off(report: dict[str, Any], lines: list[str]) -> None:
    table = _first_table(lines)
    if not table:
        return
    sign_off = report["sign_off"]
    for row in table[1:]:
        if len(row) < 2:
            continue
        key = _find_alias_key(row[0], SIGN_OFF_ALIASES)
        if key is None:
            continue
        value = row[1].strip()
        if key == "confirmation_status":
            sign_off[key] = _normalize_confirmation_status(value)
        elif key == "confirmed_at":
            sign_off[key] = value or None
        elif key == "submitter_confirmation_text":
            sign_off[key] = value or sign_off[key]
        else:
            sign_off[key] = value or None


def _parse_section_rows(lines: list[str], row_parser: Any) -> list[dict[str, Any]]:
    table = _first_table(lines)
    if not table:
        return []
    items: list[dict[str, Any]] = []
    for row in table[1:]:
        item = row_parser(row)
        if item is not None:
            items.append(item)
    return items


def _parse_task_progress_row(row: list[str]) -> dict[str, Any] | None:
    if len(row) < 9:
        return None
    anchor = [row[1], row[2], row[3], row[8]]
    if not _has_meaningful_anchor(anchor):
        return None
    return {
        "line_no": _parse_line_no(row[0]),
        "related_task_id": _nullable_text(row[1]),
        "task_name": row[2].strip(),
        "today_result": row[3].strip(),
        "previous_status": _normalize_status(row[4], default="not_started"),
        "current_status": _normalize_status(row[5], default="in_progress"),
        "completion_percent": _parse_percent(row[6]),
        "needs_follow_up": _normalize_bool(row[7], default=False),
        "notes": _nullable_text(row[8]),
    }


def _parse_completed_item_row(row: list[str]) -> dict[str, Any] | None:
    if len(row) < 10:
        return None
    anchor = [row[1], row[3], row[7]]
    if not _has_meaningful_anchor(anchor):
        return None
    return {
        "line_no": _parse_line_no(row[0]),
        "item_name": row[1].strip(),
        "item_type": _normalize_item_type(row[2]),
        "completion_detail": row[3].strip(),
        "current_status": _normalize_status(row[4], default="done"),
        "evidence": _nullable_text(row[5]),
        "artifact_title": _nullable_text(row[6]),
        "artifact_uri": _nullable_text(row[7]),
        "related_module": _nullable_text(row[8]),
        "reusable_for_followup": _normalize_bool(row[9], default=False),
    }


def _parse_artifact_row(row: list[str]) -> dict[str, Any] | None:
    if len(row) < 7:
        return None
    anchor = [row[1], row[3]]
    if not _has_meaningful_anchor(anchor):
        return None
    return {
        "line_no": _parse_line_no(row[0]),
        "artifact_name": row[1].strip(),
        "artifact_type": _normalize_artifact_type(row[2]),
        "main_content": _nullable_text(row[3]),
        "usage_scope": _nullable_text(row[4]),
        "current_version": _nullable_text(row[5]),
        "synced": _normalize_optional_bool(row[6]),
    }


def _parse_blocker_row(row: list[str]) -> dict[str, Any] | None:
    if len(row) < 8:
        return None
    anchor = [row[1], row[2], row[7]]
    if not _has_meaningful_anchor(anchor):
        return None
    return {
        "line_no": _parse_line_no(row[0]),
        "issue_name": row[1].strip(),
        "issue_description": row[2].strip(),
        "impact_scope": row[3].strip(),
        "severity": _normalize_severity(row[4]),
        "attempted_solution": _nullable_text(row[5]),
        "is_blocking": _normalize_bool(row[6], default=False),
        "support_owner": _nullable_text(row[7]),
    }


def _parse_support_request_row(row: list[str]) -> dict[str, Any] | None:
    if len(row) < 7:
        return None
    anchor = [row[1], row[2], row[3], row[4], row[6]]
    if not _has_meaningful_anchor(anchor):
        return None
    return {
        "line_no": _parse_line_no(row[0]),
        "need_support": _normalize_bool(row[1], default=False),
        "support_item": _nullable_text(row[2]),
        "support_reason": _nullable_text(row[3]),
        "expected_support_target": _nullable_text(row[4]),
        "expected_completion_at": _nullable_text(row[5]),
        "impact_if_unresolved": _nullable_text(row[6]),
    }


def _parse_decision_request_row(row: list[str]) -> dict[str, Any] | None:
    if len(row) < 10:
        return None
    anchor = [row[1], row[2], row[3], row[8]]
    if not _has_meaningful_anchor(anchor):
        return None
    options = _parse_decision_options(row[3])
    return {
        "line_no": _parse_line_no(row[0]),
        "decision_item": row[1].strip(),
        "background": _nullable_text(row[2]),
        "options": options,
        "recommended_option_key": _parse_recommended_option_key(row[4], options),
        "decision_level": _normalize_decision_level(row[5]),
        "suggested_escalation_target": _nullable_text(row[6]),
        "impact_if_unconfirmed": _nullable_text(row[7]),
        "expected_confirmation_at": _nullable_text(row[8]),
        "confirmed_by": _nullable_text(row[9]),
    }


def _parse_tomorrow_plan_row(row: list[str]) -> dict[str, Any] | None:
    if len(row) < 7:
        return None
    anchor = [row[1], row[2]]
    if not _has_meaningful_anchor(anchor):
        return None
    return {
        "line_no": _parse_line_no(row[0]),
        "plan": row[1].strip(),
        "expected_artifact": _nullable_text(row[2]),
        "priority": _normalize_priority(row[3]),
        "expected_completion_at": _nullable_text(row[4]),
        "dependencies": _nullable_text(row[5]),
        "needs_collaboration": _normalize_bool(row[6], default=False),
    }


def _parse_cross_module_request_row(row: list[str]) -> dict[str, Any] | None:
    if len(row) < 7:
        return None
    anchor = [row[1], row[2], row[3], row[4]]
    if not _has_meaningful_anchor(anchor):
        return None
    return {
        "line_no": _parse_line_no(row[0]),
        "counterpart": row[1].strip(),
        "request_content": _nullable_text(row[2]),
        "need_from_other_side": _nullable_text(row[3]),
        "available_from_me": _nullable_text(row[4]),
        "expected_completion_at": _nullable_text(row[5]),
        "current_status": _normalize_status(row[6], default="not_started"),
    }


def _parse_workflow_note_row(row: list[str]) -> dict[str, Any] | None:
    if len(row) < 6:
        return None
    anchor = [row[1]]
    if not _has_meaningful_anchor(anchor):
        return None
    return {
        "note_type": _normalize_workflow_note_type(row[0]),
        "content": _nullable_text(row[1]),
        "target_roles": _normalize_target_roles(row[2]),
        "recommend_persist": _normalize_bool(row[3], default=False),
        "validated": _normalize_bool(row[4], default=False),
        "notes": _nullable_text(row[5]),
    }


def _split_sections(markdown: str) -> dict[int, list[str]]:
    sections: dict[int, list[str]] = {}
    current_section: int | None = None
    for raw_line in markdown.splitlines():
        line = raw_line.rstrip("\n")
        match = SECTION_HEADER_RE.match(line.strip())
        if match:
            current_section = _section_number(match.group(1), match.group(2))
            if current_section is None:
                continue
            sections[current_section] = []
            continue
        if current_section is not None:
            sections[current_section].append(line)
    return sections


def _section_number(raw_number: str | None, raw_title: str) -> int | None:
    if raw_number:
        return int(raw_number)
    normalized = _normalize_section_title(raw_title)
    for section_number, aliases in SECTION_TITLE_ALIASES.items():
        if normalized in {_normalize_section_title(alias) for alias in aliases}:
            return section_number
    return None


def _normalize_section_title(value: str) -> str:
    return re.sub(r"[\s/_\-:：/]+", "", value.strip().lower())


def _extract_tables(lines: list[str]) -> list[list[list[str]]]:
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            row = [cell.strip() for cell in stripped.strip("|").split("|")]
            if _is_separator_row(row):
                continue
            current.append(row)
        elif current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    return tables


def _first_table(lines: list[str]) -> list[list[str]]:
    tables = _extract_tables(lines)
    return tables[0] if tables else []


def _is_separator_row(row: list[str]) -> bool:
    return bool(row) and all(re.fullmatch(r"[:\-\s]+", cell or "") for cell in row)


def _parse_line_no(value: str) -> int:
    match = re.search(r"\d+", value)
    return int(match.group(0)) if match else 1


def _parse_percent(value: str) -> float | None:
    cleaned = value.strip().replace("%", "")
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _nullable_text(value: str) -> str | None:
    cleaned = _strip_placeholder_value(value)
    return cleaned or None


def _strip_placeholder_value(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        return ""
    if _looks_like_placeholder_options(cleaned):
        return ""
    if cleaned in {"A：；B：", "A:;B:"}:
        return ""
    return cleaned


def _has_meaningful_anchor(values: list[str]) -> bool:
    for value in values:
        cleaned = _strip_placeholder_value(value)
        if not cleaned:
            continue
        return True
    return False


def _looks_like_placeholder_options(value: str) -> bool:
    if not value:
        return False
    if value in {"是?/ 否?", "是？/ 否？", "高?/ 中?/ 低?", "高？/ 中？/ 低？"}:
        return True
    if re.fullmatch(r"[A-Za-z0-9]+\s*[：:]\s*[；;]?\s*[A-Za-z0-9]+\s*[：:]?", value):
        return True

    parts = _split_text_list(value)
    if len(parts) < 2:
        return False

    if any("?" in part or "？" in part for part in parts):
        return True

    if any("http" in part.lower() for part in parts):
        return False

    joined = "".join(parts)
    if any(ch.isdigit() for ch in joined):
        return False

    if len(parts) >= 3 and all(len(part) <= 16 for part in parts):
        return True

    return False


def _find_alias_key(raw_key: str, alias_map: dict[str, set[str]]) -> str | None:
    normalized = raw_key.strip().lower().replace(" ", "")
    for target_key, aliases in alias_map.items():
        if normalized in {alias.lower().replace(" ", "") for alias in aliases}:
            return target_key
    return None


def _normalize_bool(value: str, *, default: bool) -> bool:
    normalized = value.strip().lower()
    if normalized in {"是", "yes", "true", "y", "1", "已确认"}:
        return True
    if normalized in {"否", "no", "false", "n", "0", "未确认"}:
        return False
    return default


def _normalize_optional_bool(value: str) -> bool | None:
    cleaned = value.strip()
    if not cleaned:
        return None
    return _normalize_bool(cleaned, default=False)


def _normalize_status(value: str, *, default: str) -> str:
    normalized = value.strip().lower()
    mapping = {
        "待处理": "not_started",
        "未开始": "not_started",
        "not_started": "not_started",
        "pending": "not_started",
        "进行中": "in_progress",
        "进行": "in_progress",
        "in_progress": "in_progress",
        "in progress": "in_progress",
        "blocked": "blocked",
        "阻塞": "blocked",
        "卡住": "blocked",
        "done": "done",
        "已完成": "done",
        "completed": "done",
        "cancelled": "cancelled",
        "已取消": "cancelled",
        "草稿": "draft",
        "draft": "draft",
        "confirmed": "confirmed",
        "已确认": "confirmed",
    }
    return mapping.get(normalized, default)


def _normalize_report_status(value: str) -> str:
    return _normalize_status(value, default="draft")


def _normalize_confirmation_status(value: str) -> str:
    normalized = value.strip().lower()
    if normalized in {"已确认", "confirmed"}:
        return "confirmed"
    return "unconfirmed"


def _normalize_priority(value: str) -> str:
    normalized = value.strip().lower()
    mapping = {
        "高": "high",
        "high": "high",
        "中": "medium",
        "medium": "medium",
        "低": "low",
        "low": "low",
    }
    return mapping.get(normalized, "medium")


def _normalize_severity(value: str) -> str:
    normalized = value.strip().lower()
    mapping = {
        "高": "high",
        "high": "high",
        "中": "medium",
        "medium": "medium",
        "低": "low",
        "low": "low",
    }
    return mapping.get(normalized, "low")


def _normalize_submission_channel(value: str) -> str:
    normalized = value.strip().lower()
    mapping = {
        "im": "im",
        "web": "web",
        "agent": "agent",
        "手动": "manual",
        "manual": "manual",
    }
    return mapping.get(normalized, "manual")


def _normalize_work_types(value: str) -> list[str]:
    mapping = {
        "架构设计": "architecture_design",
        "architecture_design": "architecture_design",
        "schema": "schema",
        "dag": "dag",
        "后端": "backend",
        "backend": "backend",
        "agent定制化": "agent_customization",
        "agent客制化": "agent_customization",
        "agent_customization": "agent_customization",
        "prompt": "prompt",
        "context": "context",
        "数据库": "database",
        "database": "database",
        "api": "api",
        "联调": "integration",
        "integration": "integration",
        "文档": "documentation",
        "documentation": "documentation",
        "other": "other",
        "其他": "other",
    }
    values = _split_text_list(value)
    normalized = [mapping[item.lower()] for item in values if item.lower() in mapping]
    if len(normalized) >= 5:
        return []
    return list(dict.fromkeys(normalized))


def _normalize_item_type(value: str) -> str:
    normalized = value.strip().lower()
    mapping = {
        "文档": "document",
        "document": "document",
        "代码": "code",
        "code": "code",
        "接口": "interface",
        "interface": "interface",
        "数据库": "database",
        "database": "database",
        "prompt": "prompt",
        "context": "context",
        "联调": "integration",
        "integration": "integration",
        "测试": "test",
        "test": "test",
        "会议": "meeting",
        "meeting": "meeting",
        "决策": "decision",
        "decision": "decision",
        "其他": "other",
        "other": "other",
    }
    return mapping.get(normalized, "other")


def _normalize_artifact_type(value: str) -> str:
    normalized = value.strip().lower()
    mapping = {
        "文档": "document",
        "document": "document",
        "表格": "sheet",
        "sheet": "sheet",
        "图": "diagram",
        "diagram": "diagram",
        "代码": "code",
        "code": "code",
        "接口": "interface",
        "interface": "interface",
        "prompt": "prompt",
        "context": "context",
        "配置": "config",
        "config": "config",
        "其他": "other",
        "other": "other",
    }
    return mapping.get(normalized, "other")


def _normalize_decision_level(value: str) -> str:
    normalized = value.strip().lower()
    mapping = {
        "l1": "l1",
        "l2": "l2",
        "l3": "l3",
        "l4": "l4",
    }
    return mapping.get(normalized, "l1")


def _normalize_workflow_note_type(value: str) -> str:
    normalized = value.strip().lower()
    if "workflow" in normalized:
        return "workflow_change"
    if "prompt" in normalized:
        return "prompt_rule"
    return "context"


def _normalize_target_roles(value: str) -> list[str]:
    mapping = {
        "staff": "staff",
        "manager": "manager",
        "executive": "executive",
    }
    roles = [mapping[item.lower()] for item in _split_text_list(value) if item.lower() in mapping]
    return roles or ["staff"]


def _normalize_workflow_nodes(value: str) -> list[str]:
    mapping = {
        "staff日报": "staff_report",
        "staff_report": "staff_report",
        "manager汇总": "manager_summary",
        "manager_summary": "manager_summary",
        "executive决策": "executive_decision",
        "executive_decision": "executive_decision",
        "任务下发": "task_dispatch",
        "task_dispatch": "task_dispatch",
        "数据库写入": "database_write",
        "database_write": "database_write",
        "api联调": "api_integration",
        "api_integration": "api_integration",
        "agentprompt": "agent_prompt",
        "agent_prompt": "agent_prompt",
        "context": "context",
        "demo": "demo",
    }
    result = [mapping[item.lower().replace(" ", "")] for item in _split_text_list(value) if item.lower().replace(" ", "") in mapping]
    return list(dict.fromkeys(result))


def _parse_decision_options(value: str) -> list[dict[str, Any]]:
    cleaned = value.strip()
    if not cleaned:
        return []
    parts = re.split(r"[；;]\s*", cleaned)
    options: list[dict[str, Any]] = []
    for part in parts:
        match = re.match(r"([A-Za-z0-9]+)\s*[：:]\s*(.*)", part.strip())
        if match:
            key = match.group(1)
            label = match.group(2).strip()
            if label:
                options.append({"key": key, "label": label, "description": None})
    return options


def _parse_recommended_option_key(value: str, options: list[dict[str, Any]]) -> str | None:
    cleaned = value.strip()
    if not cleaned:
        return None
    for option in options:
        if cleaned == option["key"] or cleaned == option["label"]:
            return option["key"]
    match = re.search(r"[A-Za-z0-9]+", cleaned)
    return match.group(0) if match else None


def _split_text_list(value: str) -> list[str]:
    cleaned = value.strip()
    if not cleaned:
        return []
    parts = re.split(r"\s*(?:/|、|,|，|;|；|\n)\s*", cleaned)
    return [part.strip() for part in parts if part.strip()]


def _decode_markdown_bytes(raw: bytes) -> str:
    candidates: list[tuple[int, str]] = []
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "gbk", "utf-16", "utf-16-le"):
        try:
            text = raw.decode(encoding)
        except UnicodeDecodeError:
            continue
        score = _score_decoded_markdown(text)
        candidates.append((score, text))
    if not candidates:
        return raw.decode("utf-8", errors="replace")
    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def _score_decoded_markdown(text: str) -> int:
    score = 0
    score += text.count("## ") * 20
    score += text.count("|") * 2
    score -= text.count("\ufffd") * 50
    if "schema_v1_staff" in text:
        score += 20
    if "日报" in text:
        score += 20
    return score


def report_to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2)
