from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from automage_agents.db.models import FormTemplateModel, StaffReportModel, WorkRecordItemModel, WorkRecordModel
from automage_agents.schemas.staff_daily_report_rendering import render_staff_daily_report_markdown


FORM_TEMPLATE_NAME = "Staff Daily Report Template"
FORM_TEMPLATE_SCHEMA_ID = "schema_v1_staff_daily"
FORM_TEMPLATE_SCHEMA_VERSION = "v1.0.0"
FORM_TEMPLATE_PUBLIC_ID = "tmpl_staff_daily_v100"


@dataclass(slots=True)
class PersistedStaffDailyReport:
    template_id: int
    work_record_id: int
    work_record_public_id: str
    staff_report_id: int | None
    item_count: int


@dataclass(slots=True)
class StaffDailyReportPersistenceOptions:
    org_id: int
    user_id: int
    department_id: int | None = None
    created_by: int | None = None
    include_staff_report_snapshot: bool = True
    staff_report_identity: dict[str, str] | None = None


@dataclass(slots=True)
class HydratedStaffDailyReport:
    work_record_id: int
    work_record_public_id: str
    report: dict[str, Any]
    markdown: str
    meta: dict[str, Any]


def persist_staff_daily_report(
    db: Session,
    report: dict[str, Any],
    *,
    options: StaffDailyReportPersistenceOptions,
    schema_path: str | Path | None = None,
) -> PersistedStaffDailyReport:
    template = ensure_staff_daily_template(
        db,
        org_id=options.org_id,
        created_by=options.created_by or options.user_id,
        schema_path=schema_path,
    )

    record_date = _parse_report_date(report["basic_info"]["report_date"])
    submitted_at = _parse_datetime(report["basic_info"].get("submitted_at"))
    title = _build_work_record_title(report)
    status = _map_report_status(report["basic_info"].get("report_status"))
    source_type = _map_submission_channel(report["basic_info"].get("submission_channel"))
    meta = _build_work_record_meta(report, options)
    public_id = _new_public_id("wr")

    work_record = WorkRecordModel(
        public_id=public_id,
        org_id=options.org_id,
        department_id=options.department_id,
        template_id=template.id,
        user_id=options.user_id,
        record_date=record_date,
        title=title,
        status=status,
        submitted_at=submitted_at,
        source_type=source_type,
        created_by=options.created_by or options.user_id,
        updated_by=options.created_by or options.user_id,
        meta=meta,
    )
    db.add(work_record)
    db.flush()

    items = _build_work_record_items(report, org_id=options.org_id, work_record_id=work_record.id)
    db.add_all(items)

    staff_report_id: int | None = None
    if options.include_staff_report_snapshot:
        identity = options.staff_report_identity or _build_default_staff_report_identity(report)
        snapshot = StaffReportModel(
            node_id=identity["node_id"],
            user_id=identity["user_id"],
            role=identity["role"],
            report_json=report["legacy_projection"],
        )
        db.add(snapshot)
        db.flush()
        staff_report_id = snapshot.id
        work_record.meta = {**work_record.meta, "staff_report_snapshot_id": staff_report_id}
        db.add(work_record)

    db.flush()
    db.refresh(work_record)
    return PersistedStaffDailyReport(
        template_id=template.id,
        work_record_id=work_record.id,
        work_record_public_id=work_record.public_id,
        staff_report_id=staff_report_id,
        item_count=len(items),
    )


def ensure_staff_daily_template(
    db: Session,
    *,
    org_id: int,
    created_by: int,
    schema_path: str | Path | None = None,
) -> FormTemplateModel:
    existing = (
        db.query(FormTemplateModel)
        .filter(
            FormTemplateModel.org_id == org_id,
            FormTemplateModel.name == FORM_TEMPLATE_NAME,
            FormTemplateModel.deleted_at.is_(None),
        )
        .order_by(FormTemplateModel.id.asc())
        .first()
    )
    schema_json = _load_schema_json(schema_path)
    if existing is not None:
        if existing.schema_json != schema_json:
            existing.schema_json = schema_json
            existing.updated_by = created_by
            existing.meta = {
                **dict(existing.meta),
                "schema_id": FORM_TEMPLATE_SCHEMA_ID,
                "schema_version": FORM_TEMPLATE_SCHEMA_VERSION,
            }
            db.add(existing)
            db.flush()
        return existing

    template = FormTemplateModel(
        public_id=FORM_TEMPLATE_PUBLIC_ID,
        org_id=org_id,
        name=FORM_TEMPLATE_NAME,
        scope=1,
        status=1,
        schema_json=schema_json,
        version=1,
        created_by=created_by,
        updated_by=created_by,
        meta={
            "schema_id": FORM_TEMPLATE_SCHEMA_ID,
            "schema_version": FORM_TEMPLATE_SCHEMA_VERSION,
        },
    )
    db.add(template)
    db.flush()
    return template


def load_staff_daily_report(db: Session, work_record_id: int) -> HydratedStaffDailyReport | None:
    work_record = db.get(WorkRecordModel, work_record_id)
    if work_record is None or work_record.deleted_at is not None:
        return None

    rows = (
        db.query(WorkRecordItemModel)
        .filter(WorkRecordItemModel.work_record_id == work_record_id)
        .order_by(WorkRecordItemModel.sort_order.asc(), WorkRecordItemModel.id.asc())
        .all()
    )
    report = _hydrate_report_from_items(rows)
    markdown = render_staff_daily_report_markdown(report)
    return HydratedStaffDailyReport(
        work_record_id=work_record.id,
        work_record_public_id=work_record.public_id,
        report=report,
        markdown=markdown,
        meta=dict(work_record.meta),
    )


def _build_work_record_items(report: dict[str, Any], *, org_id: int, work_record_id: int) -> list[WorkRecordItemModel]:
    sections = [
        ("basic_info", "基础信息", "object", report["basic_info"]),
        ("today_task_progress", "今日任务进展", "array", report["today_task_progress"]),
        ("today_completed_items", "今日完成事项", "array", report["today_completed_items"]),
        ("today_artifacts", "今日产出物清单", "array", report["today_artifacts"]),
        ("today_blockers", "今日问题与阻塞", "array", report["today_blockers"]),
        ("support_requests", "需要支持的事项", "array", report["support_requests"]),
        ("decision_requests", "需要确认或决策的事项", "array", report["decision_requests"]),
        ("tomorrow_plans", "明日计划", "array", report["tomorrow_plans"]),
        ("cross_module_requests", "与其他模块的对接需求", "array", report["cross_module_requests"]),
        ("risk_assessment", "风险判断", "object", report["risk_assessment"]),
        ("workflow_notes", "Context / Prompt / Workflow 补充", "array", report["workflow_notes"]),
        ("daily_summary", "今日总结", "object", report["daily_summary"]),
        ("sign_off", "签名确认", "object", report["sign_off"]),
    ]
    if "source_markdown" in report:
        sections.append(("source_markdown", "原始 Markdown 快照", "markdown", report["source_markdown"]))

    projections = _build_search_projection_items(report)
    items: list[WorkRecordItemModel] = []
    sort_order = 10
    for field_key, field_label, field_type, payload in sections:
        value_text, value_json = _split_item_payload(field_type, payload)
        items.append(
            WorkRecordItemModel(
                org_id=org_id,
                work_record_id=work_record_id,
                field_key=field_key,
                field_label=field_label,
                field_type=field_type,
                sort_order=sort_order,
                value_text=value_text,
                value_json=value_json,
                meta={},
            )
        )
        sort_order += 10

    for field_key, field_label, field_type, payload in projections:
        value_text, value_json = _split_item_payload(field_type, payload)
        items.append(
            WorkRecordItemModel(
                org_id=org_id,
                work_record_id=work_record_id,
                field_key=field_key,
                field_label=field_label,
                field_type=field_type,
                sort_order=sort_order,
                value_text=value_text,
                value_json=value_json,
                meta={"projection": True},
            )
        )
        sort_order += 10
    return items


def _build_search_projection_items(report: dict[str, Any]) -> list[tuple[str, str, str, Any]]:
    need_support = report["legacy_projection"]["need_support"]
    blocker_count = len(report["today_blockers"])
    decision_count = len(report["decision_requests"])
    risk_level = report["risk_assessment"]["overall_risk_level"]
    follow_up_task_count = sum(1 for item in report["today_task_progress"] if item["needs_follow_up"])
    artifact_count = len(report["today_artifacts"])
    return [
        ("search.need_support", "是否需要支持", "boolean", need_support),
        ("search.blocker_count", "阻塞数量", "integer", blocker_count),
        ("search.decision_count", "待决策数量", "integer", decision_count),
        ("search.risk_level", "总体风险等级", "enum", risk_level),
        ("search.follow_up_task_count", "需继续跟进任务数", "integer", follow_up_task_count),
        ("search.artifact_count", "产出物数量", "integer", artifact_count),
    ]


def _split_item_payload(field_type: str, payload: Any) -> tuple[str | None, Any]:
    if field_type in {"markdown", "boolean", "integer", "enum"}:
        return str(payload), None
    if field_type in {"object", "array"}:
        return None, payload
    return (payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)), None


def _build_work_record_meta(report: dict[str, Any], options: StaffDailyReportPersistenceOptions) -> dict[str, Any]:
    legacy = report["legacy_projection"]
    return {
        "schema_id": report["schema_id"],
        "schema_version": report["schema_version"],
        "template_name": report.get("template_name"),
        "submitted_by": report["basic_info"].get("submitted_by"),
        "need_support": legacy["need_support"],
        "risk_level": report["risk_assessment"]["overall_risk_level"],
        "blocker_count": len(report["today_blockers"]),
        "decision_count": len(report["decision_requests"]),
        "artifact_count": len(report["today_artifacts"]),
        "source_channel": report["basic_info"].get("submission_channel"),
        "source_user_id_text": report["basic_info"].get("user_id"),
        "source_department_text": report["basic_info"].get("department_or_project_group"),
        "persisted_by": options.created_by or options.user_id,
    }


def _build_default_staff_report_identity(report: dict[str, Any]) -> dict[str, str]:
    basic_info = report["basic_info"]
    return {
        "node_id": basic_info.get("agent_node_id") or f'staff-node-{basic_info.get("user_id") or "unknown"}',
        "user_id": basic_info.get("user_id") or "unknown",
        "role": "staff",
    }


def _build_work_record_title(report: dict[str, Any]) -> str:
    basic_info = report["basic_info"]
    submitted_by = basic_info.get("submitted_by") or basic_info.get("user_id") or "unknown"
    report_date = basic_info.get("report_date") or "unknown-date"
    return f"[日报] {submitted_by} {report_date}"


def _parse_report_date(value: str) -> date:
    if not value:
        return datetime.now().date()
    return date.fromisoformat(value)


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _map_report_status(value: str | None) -> int:
    mapping = {
        "draft": 0,
        "confirmed": 1,
    }
    return mapping.get(value or "draft", 0)


def _map_submission_channel(value: str | None) -> int:
    mapping = {
        "im": 1,
        "web": 2,
        "agent": 3,
        "manual": 4,
    }
    return mapping.get(value or "manual", 4)


def _load_schema_json(schema_path: str | Path | None) -> dict[str, Any]:
    target = Path(schema_path) if schema_path is not None else Path(__file__).with_name("staff_daily_report_v1.schema.json")
    return json.loads(target.read_text(encoding="utf-8"))


def _new_public_id(prefix: str) -> str:
    token = uuid4().hex[:22]
    return f"{prefix}_{token}"


def _hydrate_report_from_items(rows: list[WorkRecordItemModel]) -> dict[str, Any]:
    report = {
        "schema_id": FORM_TEMPLATE_SCHEMA_ID,
        "schema_version": FORM_TEMPLATE_SCHEMA_VERSION,
        "template_name": "AutoMage_2_Staff日报模板",
    }
    for row in rows:
        if row.field_key.startswith("search."):
            continue
        if row.field_key == "source_markdown":
            report["source_markdown"] = row.value_text or ""
            continue
        if row.field_type in {"object", "array"}:
            report[row.field_key] = row.value_json
        else:
            report[row.field_key] = row.value_text

    report.setdefault("basic_info", {})
    report.setdefault("today_task_progress", [])
    report.setdefault("today_completed_items", [])
    report.setdefault("today_artifacts", [])
    report.setdefault("today_blockers", [])
    report.setdefault("support_requests", [])
    report.setdefault("decision_requests", [])
    report.setdefault("tomorrow_plans", [])
    report.setdefault("cross_module_requests", [])
    report.setdefault("risk_assessment", {})
    report.setdefault("workflow_notes", [])
    report.setdefault("daily_summary", {})
    report.setdefault("sign_off", {})
    report["legacy_projection"] = {
        "schema_id": "schema_v1_staff",
        "timestamp": report["basic_info"].get("submitted_at") or "",
        "work_progress": "\n".join(
            item.get("today_result", "") for item in report["today_task_progress"] if item.get("today_result")
        ),
        "issues_faced": "\n".join(
            item.get("issue_description", "") for item in report["today_blockers"] if item.get("issue_description")
        ),
        "solution_attempt": "\n".join(
            item.get("attempted_solution", "") for item in report["today_blockers"] if item.get("attempted_solution")
        ),
        "need_support": any(item.get("need_support") for item in report["support_requests"]),
        "next_day_plan": "\n".join(item.get("plan", "") for item in report["tomorrow_plans"] if item.get("plan")),
        "resource_usage": {
            "task_count": len(report["today_task_progress"]),
            "completed_item_count": len(report["today_completed_items"]),
            "artifact_count": len(report["today_artifacts"]),
            "blocker_count": len(report["today_blockers"]),
            "decision_count": len(report["decision_requests"]),
        },
    }
    return report
