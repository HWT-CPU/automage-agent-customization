from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from automage_agents.core.enums import AgentLevel, AgentRole
from automage_agents.core.models import AgentIdentity
from automage_agents.db.models import DepartmentModel, StaffReportModel, SummaryModel, TaskModel, UserModel, WorkRecordModel
from automage_agents.schemas.staff_daily_report_persistence import load_staff_daily_report
from automage_agents.server.service import create_manager_report


@dataclass(slots=True)
class StaffReminderResult:
    record_date: str
    missing_user_ids: list[str]


@dataclass(slots=True)
class ManagerReminderResult:
    summary_date: str
    pending_manager_user_ids: list[str]


@dataclass(slots=True)
class ManagerAutoSummaryResult:
    summary_date: str
    generated_summary_ids: list[int | str]
    generated_department_ids: list[str]
    skipped_department_ids: list[str]
    source_record_count: int
    errors: list[dict[str, str]]


def collect_missing_staff_daily_reports(
    db: Session,
    *,
    record_date: date,
    limit: int = 100,
) -> StaffReminderResult:
    staff_users = (
        db.query(UserModel)
        .filter(UserModel.deleted_at.is_(None), UserModel.manager_user_id.is_not(None))
        .order_by(UserModel.id.asc())
        .limit(limit)
        .all()
    )
    submitted_user_ids = {
        row.user_id
        for row in db.query(WorkRecordModel)
        .filter(WorkRecordModel.deleted_at.is_(None), WorkRecordModel.record_date == record_date)
        .all()
    }
    missing = [user.username for user in staff_users if user.id not in submitted_user_ids]
    return StaffReminderResult(record_date=record_date.isoformat(), missing_user_ids=missing)


def collect_pending_manager_summaries(
    db: Session,
    *,
    summary_date: date,
    limit: int = 100,
) -> ManagerReminderResult:
    departments = (
        db.query(DepartmentModel)
        .filter(DepartmentModel.deleted_at.is_(None), DepartmentModel.manager_user_id.is_not(None))
        .order_by(DepartmentModel.id.asc())
        .limit(limit)
        .all()
    )
    existing_department_ids = {
        row.department_id
        for row in db.query(SummaryModel)
        .filter(SummaryModel.deleted_at.is_(None), SummaryModel.summary_date == summary_date)
        .all()
    }
    pending_manager_ids: list[str] = []
    manager_ids = {department.manager_user_id for department in departments if department.id not in existing_department_ids}
    if manager_ids:
        managers = db.query(UserModel).filter(UserModel.id.in_(manager_ids)).all()
        pending_manager_ids = [row.username for row in managers]
    return ManagerReminderResult(summary_date=summary_date.isoformat(), pending_manager_user_ids=pending_manager_ids)


def collect_overdue_tasks(
    db: Session,
    *,
    limit: int = 100,
) -> list[str]:
    rows = (
        db.query(TaskModel)
        .filter(TaskModel.deleted_at.is_(None), TaskModel.status.in_([1, 2]))
        .order_by(TaskModel.id.asc())
        .limit(limit)
        .all()
    )
    return [row.public_id for row in rows]


def generate_pending_manager_summaries(
    db: Session,
    *,
    summary_date: date,
    limit: int = 100,
) -> ManagerAutoSummaryResult:
    departments = (
        db.query(DepartmentModel)
        .filter(DepartmentModel.deleted_at.is_(None), DepartmentModel.manager_user_id.is_not(None))
        .order_by(DepartmentModel.id.asc())
        .limit(limit)
        .all()
    )
    existing_department_ids = {
        row.department_id
        for row in db.query(SummaryModel)
        .filter(SummaryModel.deleted_at.is_(None), SummaryModel.summary_date == summary_date)
        .all()
    }

    generated_summary_ids: list[int | str] = []
    generated_department_ids: list[str] = []
    skipped_department_ids: list[str] = []
    errors: list[dict[str, str]] = []
    source_record_count = 0

    for department in departments:
        department_id = _department_public_id(department)
        if department.id in existing_department_ids:
            skipped_department_ids.append(department_id)
            continue

        records = _department_work_records(db, department, summary_date=summary_date)
        if not records:
            skipped_department_ids.append(department_id)
            continue

        manager = db.get(UserModel, department.manager_user_id)
        if manager is None or manager.deleted_at is not None:
            skipped_department_ids.append(department_id)
            errors.append({"department_id": department_id, "error": "manager_not_found"})
            continue

        try:
            report = _build_manager_report_payload(db, department, manager, records, summary_date=summary_date)
            identity = _build_manager_identity(department, manager, report)
            response = create_manager_report(
                db,
                identity,
                report,
                request_id=f"scheduler-manager-summary-{summary_date.isoformat()}-{department.public_id}",
            )
        except Exception as exc:
            db.rollback()
            skipped_department_ids.append(department_id)
            errors.append({"department_id": department_id, "error": str(exc)})
            continue

        generated_summary_ids.append(response.get("summary_public_id") or response.get("summary_id"))
        generated_department_ids.append(department_id)
        source_record_count += len(records)

    return ManagerAutoSummaryResult(
        summary_date=summary_date.isoformat(),
        generated_summary_ids=generated_summary_ids,
        generated_department_ids=generated_department_ids,
        skipped_department_ids=skipped_department_ids,
        source_record_count=source_record_count,
        errors=errors,
    )


def _department_work_records(db: Session, department: DepartmentModel, *, summary_date: date) -> list[WorkRecordModel]:
    return (
        db.query(WorkRecordModel)
        .filter(
            WorkRecordModel.deleted_at.is_(None),
            WorkRecordModel.org_id == department.org_id,
            WorkRecordModel.department_id == department.id,
            WorkRecordModel.record_date == summary_date,
        )
        .order_by(WorkRecordModel.id.asc())
        .all()
    )


def _build_manager_report_payload(
    db: Session,
    department: DepartmentModel,
    manager: UserModel,
    records: list[WorkRecordModel],
    *,
    summary_date: date,
) -> dict[str, Any]:
    staff_reports = [_extract_staff_report(db, record) for record in records]
    missing_staff_ids = _missing_staff_ids(db, department, records)
    risk_items = _risk_items(staff_reports, records)
    blocked_items = _blocked_items(staff_reports, records)
    support_count = sum(1 for report in staff_reports if bool(report.get("need_support")))
    decision_count = sum(1 for report in staff_reports if bool(report.get("need_decision")))
    staff_report_count = len(records)
    missing_report_count = len(missing_staff_ids)
    return {
        "timestamp": f"{summary_date.isoformat()}T20:00:00+08:00",
        "org_id": str(department.org_id),
        "dept_id": department.public_id,
        "manager_user_id": manager.username,
        "manager_node_id": f"manager-node-{manager.username}",
        "summary_date": summary_date.isoformat(),
        "staff_report_count": staff_report_count,
        "missing_report_count": missing_report_count,
        "missing_staff_ids": missing_staff_ids,
        "overall_health": _overall_health(risk_items, support_count, missing_report_count),
        "aggregated_summary": _aggregated_summary(department, staff_reports, records, missing_report_count),
        "top_3_risks": risk_items[:3],
        "workforce_efficiency": _workforce_efficiency(staff_report_count, missing_report_count, support_count, decision_count),
        "pending_approvals": support_count + decision_count,
        "highlight_staff": _highlight_staff(staff_reports, records),
        "blocked_items": blocked_items,
        "manager_decisions": [],
        "need_executive_decision": [item for item in blocked_items if item.get("need_executive_decision")],
        "next_day_adjustment": _next_day_adjustments(staff_reports),
        "source_record_ids": [record.public_id for record in records],
        "source_task_ids": [],
        "source_incident_ids": [],
        "title": f"{department.name} {summary_date.isoformat()} 自动汇总",
        "meta": {
            "source": "scheduler",
            "generator": "manager_summary_auto_generate_job",
            "source_record_count": staff_report_count,
        },
    }


def _extract_staff_report(db: Session, record: WorkRecordModel) -> dict[str, Any]:
    snapshot_id = dict(record.meta or {}).get("staff_report_snapshot_id")
    if snapshot_id is not None:
        snapshot = db.get(StaffReportModel, snapshot_id)
        if snapshot is not None:
            return dict(snapshot.report_json or {})
    try:
        hydrated = load_staff_daily_report(db, record.id)
    except (KeyError, TypeError, ValueError):
        hydrated = None
    if hydrated is not None:
        return dict(hydrated.report.get("legacy_projection") or {})
    return {
        "record_date": record.record_date.isoformat(),
        "work_progress": record.title,
        "issues_faced": "",
        "solution_attempt": "",
        "need_support": bool(dict(record.meta or {}).get("need_support")),
        "next_day_plan": "",
        "risk_level": dict(record.meta or {}).get("risk_level", "low"),
        "resource_usage": dict(record.meta or {}),
    }


def _missing_staff_ids(db: Session, department: DepartmentModel, records: list[WorkRecordModel]) -> list[str]:
    submitted_user_ids = {record.user_id for record in records}
    staff_users = (
        db.query(UserModel)
        .filter(UserModel.deleted_at.is_(None), UserModel.manager_user_id == department.manager_user_id)
        .order_by(UserModel.id.asc())
        .all()
    )
    return [user.username for user in staff_users if user.id not in submitted_user_ids]


def _risk_items(staff_reports: list[dict[str, Any]], records: list[WorkRecordModel]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for report, record in zip(staff_reports, records, strict=False):
        risk_level = str(report.get("risk_level") or "low").lower()
        issues = _text_lines(report.get("issues_faced"))
        if risk_level in {"medium", "high", "critical"} or report.get("need_support") or issues:
            description = issues[0] if issues else str(report.get("support_detail") or "需要 Manager 关注。")
            items.append(
                {
                    "risk_title": _clip(description, "日报风险"),
                    "description": description,
                    "severity": "high" if risk_level in {"high", "critical"} else "medium",
                    "source_type": "staff_report",
                    "suggested_action": str(report.get("solution_attempt") or "由 Manager 跟进确认。"),
                    "need_escalation": risk_level in {"high", "critical"} or bool(report.get("need_decision")),
                    "source_record_ids": [record.public_id],
                }
            )
    return items


def _blocked_items(staff_reports: list[dict[str, Any]], records: list[WorkRecordModel]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for report, record in zip(staff_reports, records, strict=False):
        for issue in _text_lines(report.get("issues_faced")):
            severity = "high" if str(report.get("risk_level") or "").lower() in {"high", "critical"} else "medium"
            items.append(
                {
                    "title": _clip(issue, "日报阻塞"),
                    "description": issue,
                    "severity": severity,
                    "source_record_ids": [record.public_id],
                    "need_executive_decision": severity == "high" or bool(report.get("need_decision")),
                    "suggested_action": str(report.get("solution_attempt") or "由 Manager 继续跟进。"),
                }
            )
    return items


def _highlight_staff(staff_reports: list[dict[str, Any]], records: list[WorkRecordModel]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for report, record in zip(staff_reports, records, strict=False):
        if report.get("need_support") or report.get("issues_faced"):
            continue
        progress = _first_text(report.get("work_progress"))
        if progress:
            items.append(
                {
                    "user_id": str(report.get("user_id") or record.user_id),
                    "display_name": str(report.get("user_id") or record.user_id),
                    "reason": _clip(progress, "按时提交日报且进展正常。"),
                    "evidence_record_ids": [record.public_id],
                }
            )
    return items[:5]


def _next_day_adjustments(staff_reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    plans = [_first_text(report.get("next_day_plan")) for report in staff_reports]
    return [
        {"title": _clip(plan, "明日计划"), "description": plan, "priority": "medium"}
        for plan in plans
        if plan
    ][:5]


def _aggregated_summary(
    department: DepartmentModel,
    staff_reports: list[dict[str, Any]],
    records: list[WorkRecordModel],
    missing_report_count: int,
) -> str:
    progress_lines = [_first_text(report.get("work_progress")) for report in staff_reports]
    issue_lines = [_first_text(report.get("issues_faced")) for report in staff_reports]
    parts = [
        f"{department.name} 当日共收到 {len(records)} 份日报。",
        f"主要进展：{'; '.join(line for line in progress_lines if line) or '暂无明确进展描述'}。",
    ]
    issues = "; ".join(line for line in issue_lines if line)
    if issues:
        parts.append(f"主要问题：{issues}。")
    if missing_report_count:
        parts.append(f"仍有 {missing_report_count} 名员工未提交日报。")
    return "\n".join(parts)


def _workforce_efficiency(staff_report_count: int, missing_report_count: int, support_count: int, decision_count: int) -> dict[str, Any]:
    total = staff_report_count + missing_report_count
    submission_score = 100.0 if total == 0 else staff_report_count / total * 100
    blocker_penalty = min(40.0, (support_count + decision_count) * 10.0)
    score = max(0.0, min(100.0, submission_score - blocker_penalty))
    if score >= 80:
        level = "high"
    elif score >= 50:
        level = "medium"
    else:
        level = "low"
    return {"score": round(score, 2), "level": level, "explanation": "由日报提交率、支持请求和待决策事项自动估算。"}


def _overall_health(risk_items: list[dict[str, Any]], support_count: int, missing_report_count: int) -> str:
    if any(item.get("severity") == "high" for item in risk_items):
        return "red"
    if risk_items or support_count or missing_report_count:
        return "yellow"
    return "green"


def _build_manager_identity(department: DepartmentModel, manager: UserModel, report: dict[str, Any]) -> AgentIdentity:
    return AgentIdentity(
        node_id=str(report["manager_node_id"]),
        user_id=manager.username,
        role=AgentRole.MANAGER,
        level=AgentLevel.L2_MANAGER,
        department_id=department.public_id,
        metadata={"org_id": str(report["org_id"]), "display_name": manager.display_name},
    )


def _text_lines(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item.get("description") if isinstance(item, dict) else item).strip() for item in value if str(item).strip()]
    text = str(value or "").strip()
    return [line.strip() for line in text.splitlines() if line.strip()]


def _first_text(value: Any) -> str:
    lines = _text_lines(value)
    return lines[0] if lines else ""


def _clip(value: str, fallback: str, limit: int = 40) -> str:
    text = str(value or "").strip()
    return text[:limit] or fallback


def _department_public_id(department: DepartmentModel) -> str:
    return department.public_id or str(department.id)
