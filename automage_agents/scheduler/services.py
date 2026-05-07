from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy.orm import Session

from automage_agents.db.models import DepartmentModel, SummaryModel, TaskModel, UserModel, WorkRecordModel


@dataclass(slots=True)
class StaffReminderResult:
    record_date: str
    missing_user_ids: list[str]


@dataclass(slots=True)
class ManagerReminderResult:
    summary_date: str
    pending_manager_user_ids: list[str]


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
