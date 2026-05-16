from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import func
from sqlalchemy.orm import Session

from automage_agents.config import load_runtime_settings
from automage_agents.db import (
    AgentSessionModel,
    AuditLogModel,
    DecisionLogModel,
    DecisionRecordModel,
    DepartmentModel,
    FormalDecisionLogModel,
    ManagerReportModel,
    OrganizationModel,
    StaffReportModel,
    SummaryModel,
    SummarySourceLinkModel,
    TaskAssignmentModel,
    TaskModel,
    TaskQueueModel,
    TaskUpdateModel,
    UserModel,
    WorkRecordItemModel,
    WorkRecordModel,
    create_session_factory,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    args = _parse_args()
    settings = load_runtime_settings(args.settings)
    SessionLocal = create_session_factory(settings.postgres)
    with SessionLocal() as session:
        result = verify_backend_acceptance(session, verify_date=args.date)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["ok"]:
        raise SystemExit(1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify AutoMage backend formal-table acceptance state without printing secrets.")
    parser.add_argument("--settings", default="configs/automage.local.toml", help="Runtime settings TOML path.")
    parser.add_argument("--date", type=_parse_date, default=date.today(), help="Business date to verify, e.g. 2026-05-08.")
    return parser.parse_args()


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def verify_backend_acceptance(session: Session, *, verify_date: date) -> dict[str, Any]:
    base = _base_counts(session)
    staff = _staff_report_counts(session, verify_date=verify_date)
    manager = _manager_summary_counts(session, verify_date=verify_date)
    decision = _decision_counts(session)
    task = _task_counts(session)
    audit = _audit_counts(session)
    checks = {
        "base_seed_data": all(base[key] > 0 for key in ["organizations", "departments", "users"]),
        "staff_reports_written": staff["work_records"] > 0 and staff["work_record_items"] > 0,
        "manager_summaries_written": manager["summaries"] > 0 and manager["summary_source_links"] > 0,
        "decision_chain_written": decision["decision_records"] > 0 and decision["decision_logs"] > 0,
        "task_chain_written": task["tasks"] > 0 and task["task_assignments"] > 0,
        "audit_logs_written": audit["audit_logs"] > 0,
    }
    return {
        "ok": all(checks.values()),
        "scope": "backend_formal_table_acceptance",
        "date": verify_date.isoformat(),
        "checks": checks,
        "counts": {
            "base": base,
            "staff_reports": staff,
            "manager_summaries": manager,
            "decisions": decision,
            "tasks": task,
            "audit": audit,
        },
        "notes": [
            "Formal daily report source is work_records/work_record_items; staff_reports is a compatibility snapshot.",
            "Formal manager summary source is summaries/summary_source_links; manager_reports is a compatibility snapshot.",
            "Formal task source is tasks/task_assignments/task_updates; task_queue is a compatibility mirror.",
        ],
    }


def _base_counts(session: Session) -> dict[str, int]:
    return {
        "organizations": _count(session, OrganizationModel),
        "departments": _count(session, DepartmentModel),
        "users": _count(session, UserModel),
        "agent_sessions": _count(session, AgentSessionModel),
    }


def _staff_report_counts(session: Session, *, verify_date: date) -> dict[str, int]:
    work_record_ids = [
        row[0]
        for row in session.query(WorkRecordModel.id)
        .filter(WorkRecordModel.deleted_at.is_(None), WorkRecordModel.record_date == verify_date)
        .all()
    ]
    item_count = 0
    if work_record_ids:
        item_count = session.query(func.count(WorkRecordItemModel.id)).filter(WorkRecordItemModel.work_record_id.in_(work_record_ids)).scalar() or 0
    return {
        "work_records": len(work_record_ids),
        "work_record_items": int(item_count),
        "staff_reports_snapshots": _count(session, StaffReportModel),
    }


def _manager_summary_counts(session: Session, *, verify_date: date) -> dict[str, int]:
    summary_ids = [
        row[0]
        for row in session.query(SummaryModel.id)
        .filter(SummaryModel.deleted_at.is_(None), SummaryModel.summary_date == verify_date)
        .all()
    ]
    link_count = 0
    if summary_ids:
        link_count = session.query(func.count(SummarySourceLinkModel.id)).filter(SummarySourceLinkModel.summary_id.in_(summary_ids)).scalar() or 0
    return {
        "summaries": len(summary_ids),
        "summary_source_links": int(link_count),
        "manager_reports_snapshots": _count(session, ManagerReportModel),
    }


def _decision_counts(session: Session) -> dict[str, int]:
    return {
        "decision_records": _count(session, DecisionRecordModel),
        "decision_logs": _count(session, FormalDecisionLogModel),
        "agent_decision_logs_snapshots": _count(session, DecisionLogModel),
    }


def _task_counts(session: Session) -> dict[str, int]:
    return {
        "tasks": _count(session, TaskModel),
        "task_assignments": _count(session, TaskAssignmentModel),
        "task_updates": _count(session, TaskUpdateModel),
        "task_queue_mirror": _count(session, TaskQueueModel),
    }


def _audit_counts(session: Session) -> dict[str, int]:
    critical_targets = ["work_records", "summaries", "decision_records", "tasks"]
    return {
        "audit_logs": _count(session, AuditLogModel),
        "critical_target_audit_logs": int(
            session.query(func.count(AuditLogModel.id)).filter(AuditLogModel.target_type.in_(critical_targets)).scalar() or 0
        ),
    }


def _count(session: Session, model: type[Any]) -> int:
    return int(session.query(func.count(model.id)).scalar() or 0)


if __name__ == "__main__":
    main()
