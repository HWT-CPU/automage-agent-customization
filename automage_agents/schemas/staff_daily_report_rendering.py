from __future__ import annotations

from typing import Any


def render_staff_daily_report_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f'# {report.get("template_name", "AutoMage_2_Staff日报模板")}')
    lines.append("")
    _append_kv_section(lines, 0, "基础信息", _basic_info_rows(report["basic_info"]))
    _append_table_section(
        lines,
        1,
        "今日任务进展",
        ["编号", "关联任务ID", "任务名称", "今日处理结果", "原状态", "当前状态", "完成度", "是否需要继续跟进", "备注"],
        [
            [
                item["line_no"],
                item["related_task_id"] or "",
                item["task_name"],
                item["today_result"],
                item["previous_status"],
                item["current_status"],
                "" if item["completion_percent"] is None else f'{item["completion_percent"]}%',
                _bool_text(item["needs_follow_up"]),
                item["notes"] or "",
            ]
            for item in report["today_task_progress"]
        ],
    )
    _append_table_section(
        lines,
        2,
        "今日完成事项",
        ["编号", "事项名称", "事项类型", "具体完成内容", "当前状态", "事实依据/验收方式", "产出物", "产出物链接/路径", "关联模块", "是否可用于后续联动"],
        [
            [
                item["line_no"],
                item["item_name"],
                item["item_type"],
                item["completion_detail"],
                item["current_status"],
                item["evidence"] or "",
                item["artifact_title"] or "",
                item["artifact_uri"] or "",
                item["related_module"] or "",
                _bool_text(item["reusable_for_followup"]),
            ]
            for item in report["today_completed_items"]
        ],
    )
    _append_table_section(
        lines,
        3,
        "今日产出物清单",
        ["编号", "产出物名称", "产出物类型", "主要内容", "使用方", "当前版本", "是否已同步"],
        [
            [
                item["line_no"],
                item["artifact_name"],
                item["artifact_type"],
                item["main_content"] or "",
                item["usage_scope"] or "",
                item["current_version"] or "",
                _optional_bool_text(item["synced"]),
            ]
            for item in report["today_artifacts"]
        ],
    )
    _append_table_section(
        lines,
        4,
        "今日遇到的问题与阻塞",
        ["编号", "问题名称", "问题描述", "影响范围", "严重程度", "已尝试处理方式", "当前是否阻塞", "需要谁支持"],
        [
            [
                item["line_no"],
                item["issue_name"],
                item["issue_description"],
                item["impact_scope"],
                item["severity"],
                item["attempted_solution"] or "",
                _bool_text(item["is_blocking"]),
                item["support_owner"] or "",
            ]
            for item in report["today_blockers"]
        ],
    )
    _append_table_section(
        lines,
        5,
        "需要支持的事项",
        ["编号", "是否需要支持", "支持事项", "支持原因", "期望支持对象", "期望完成时间", "不处理的影响"],
        [
            [
                item["line_no"],
                _bool_text(item["need_support"]),
                item["support_item"] or "",
                item["support_reason"] or "",
                item["expected_support_target"] or "",
                item["expected_completion_at"] or "",
                item["impact_if_unresolved"] or "",
            ]
            for item in report["support_requests"]
        ],
    )
    _append_table_section(
        lines,
        6,
        "需要确认 / 决策的事项",
        ["编号", "待确认事项", "背景说明", "可选方案", "推荐方案", "决策等级", "建议上推对象", "不确认的影响", "期望确认时间", "确认人"],
        [
            [
                item["line_no"],
                item["decision_item"],
                item["background"] or "",
                _decision_options_text(item["options"]),
                item["recommended_option_key"] or "",
                item["decision_level"],
                item["suggested_escalation_target"] or "",
                item["impact_if_unconfirmed"] or "",
                item["expected_confirmation_at"] or "",
                item["confirmed_by"] or "",
            ]
            for item in report["decision_requests"]
        ],
    )
    _append_table_section(
        lines,
        7,
        "明日计划",
        ["编号", "明日计划", "预期产出物", "优先级", "预计完成时间", "依赖条件", "是否需要协作"],
        [
            [
                item["line_no"],
                item["plan"],
                item["expected_artifact"] or "",
                item["priority"],
                item["expected_completion_at"] or "",
                item["dependencies"] or "",
                _bool_text(item["needs_collaboration"]),
            ]
            for item in report["tomorrow_plans"]
        ],
    )
    _append_table_section(
        lines,
        8,
        "与其他模块的对接需求",
        ["编号", "对接对象", "对接内容", "需要对方提供", "我方可提供", "期望完成时间", "当前状态"],
        [
            [
                item["line_no"],
                item["counterpart"],
                item["request_content"] or "",
                item["need_from_other_side"] or "",
                item["available_from_me"] or "",
                item["expected_completion_at"] or "",
                item["current_status"],
            ]
            for item in report["cross_module_requests"]
        ],
    )
    _append_kv_section(lines, 9, "风险判断", _risk_rows(report["risk_assessment"]))
    _append_table_section(
        lines,
        10,
        "Context / Prompt / Workflow 相关补充",
        ["类型", "内容", "适用对象", "是否建议沉淀", "是否已验证", "备注"],
        [
            [
                item["note_type"],
                item["content"] or "",
                " / ".join(item["target_roles"]),
                _bool_text(item["recommend_persist"]),
                _bool_text(item["validated"]),
                item["notes"] or "",
            ]
            for item in report["workflow_notes"]
        ],
    )
    _append_kv_section(lines, 11, "今日总结", _summary_rows(report["daily_summary"]))
    _append_kv_section(lines, 12, "签名确认", _sign_off_rows(report["sign_off"]))
    return "\n".join(lines).rstrip() + "\n"


def _append_kv_section(lines: list[str], index: int, title: str, rows: list[list[Any]]) -> None:
    lines.append(f"## {index}. {title}")
    lines.append("")
    lines.append("| 字段 | 填写内容 |")
    lines.append("| --- | --- |")
    for key, value in rows:
        lines.append(f"| {key} | {_cell(value)} |")
    lines.append("")


def _append_table_section(lines: list[str], index: int, title: str, headers: list[str], rows: list[list[Any]]) -> None:
    lines.append(f"## {index}. {title}")
    lines.append("")
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    if rows:
        for row in rows:
            lines.append("| " + " | ".join(_cell(value) for value in row) + " |")
    else:
        lines.append("| " + " | ".join([""] * len(headers)) + " |")
    lines.append("")


def _basic_info_rows(basic_info: dict[str, Any]) -> list[list[Any]]:
    work_types = basic_info.get("work_types") or []
    return [
        ["日报日期", basic_info.get("report_date", "")],
        ["提交人", basic_info.get("submitted_by", "")],
        ["所属项目", basic_info.get("project_name", "")],
        ["所属角色", basic_info.get("role_name", "")],
        ["负责模块", basic_info.get("responsibility_module", "")],
        ["今日工作类型", " / ".join(str(item) for item in work_types)],
        ["日报状态", basic_info.get("report_status", "")],
        ["提交时间", basic_info.get("submitted_at") or ""],
        ["本人确认", _bool_text(bool(basic_info.get("self_confirmed")))],
        ["Schema ID", basic_info.get("schema_id_ref", "")],
        ["Schema版本", basic_info.get("schema_version_ref", "")],
        ["组织ID", basic_info.get("org_id", "")],
        ["部门/项目组", basic_info.get("department_or_project_group", "")],
        ["用户ID", basic_info.get("user_id", "")],
        ["Agent节点ID", basic_info.get("agent_node_id", "")],
        ["填报渠道", basic_info.get("submission_channel", "")],
        ["关联日报模板", basic_info.get("related_template_name", "")],
    ]


def _risk_rows(risk: dict[str, Any]) -> list[list[Any]]:
    return [
        ["今日整体风险等级", risk["overall_risk_level"]],
        ["主要风险来源", " / ".join(risk["primary_risk_sources"])],
        ["可能影响的交付物", " / ".join(risk["impacted_deliverables"])],
        ["可能影响的流程节点", " / ".join(risk["impacted_workflow_nodes"])],
        ["建议处理方式", risk["suggested_mitigation"] or ""],
        ["是否需要上推", _bool_text(risk["needs_escalation"])],
        ["上推对象", " / ".join(risk["escalation_targets"])],
    ]


def _summary_rows(summary: dict[str, Any]) -> list[list[Any]]:
    return [
        ["今日最重要进展", summary["most_important_progress"]],
        ["今日最大问题", summary["biggest_issue"]],
        ["明日最优先事项", summary["top_priority_tomorrow"]],
        ["需要团队注意的事项", summary["team_attention_items"]],
    ]


def _sign_off_rows(sign_off: dict[str, Any]) -> list[list[Any]]:
    return [
        ["提交人确认", sign_off["submitter_confirmation_text"]],
        ["确认状态", sign_off["confirmation_status"]],
        ["确认人", sign_off["confirmed_by"] or ""],
        ["确认时间", sign_off["confirmed_at"] or ""],
    ]


def _decision_options_text(options: list[dict[str, Any]]) -> str:
    return "；".join(f'{item["key"]}: {item["label"]}' for item in options)


def _bool_text(value: bool) -> str:
    return "是" if value else "否"


def _optional_bool_text(value: bool | None) -> str:
    if value is None:
        return ""
    return _bool_text(value)


def _cell(value: Any) -> str:
    return ("" if value is None else str(value)).replace("|", "\\|").replace("\n", "<br>")
