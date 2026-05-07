from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime
from typing import Callable

from sqlalchemy.orm import Session

from automage_agents.scheduler.services import (
    collect_missing_staff_daily_reports,
    collect_overdue_tasks,
    collect_pending_manager_summaries,
    generate_pending_manager_summaries,
)

logger = logging.getLogger("automage.scheduler")


@dataclass(slots=True)
class SchedulerJob:
    name: str
    interval_seconds: int
    handler: Callable[[], None]
    enabled: bool = True


def health_check_job() -> None:
    logger.info("scheduler_job=health_check_job status=ok timestamp=%s", datetime.now().isoformat())


def build_staff_daily_reminder_job(
    session_factory: Callable[[], Session],
    *,
    limit: int,
) -> Callable[[], None]:
    def handler() -> None:
        session = session_factory()
        try:
            result = collect_missing_staff_daily_reports(session, record_date=date.today(), limit=limit)
            logger.info(
                "scheduler_job=staff_daily_reminder_job record_date=%s missing_count=%s missing_users=%s",
                result.record_date,
                len(result.missing_user_ids),
                result.missing_user_ids,
            )
        finally:
            session.close()

    return handler


def build_manager_summary_reminder_job(
    session_factory: Callable[[], Session],
    *,
    limit: int,
) -> Callable[[], None]:
    def handler() -> None:
        session = session_factory()
        try:
            summary_result = collect_pending_manager_summaries(session, summary_date=date.today(), limit=limit)
            overdue_tasks = collect_overdue_tasks(session, limit=limit)
            logger.info(
                "scheduler_job=manager_summary_reminder_job summary_date=%s pending_manager_count=%s pending_managers=%s overdue_task_count=%s overdue_tasks=%s",
                summary_result.summary_date,
                len(summary_result.pending_manager_user_ids),
                summary_result.pending_manager_user_ids,
                len(overdue_tasks),
                overdue_tasks,
            )
        finally:
            session.close()

    return handler


def build_manager_summary_auto_generate_job(
    session_factory: Callable[[], Session],
    *,
    limit: int,
) -> Callable[[], None]:
    def handler() -> None:
        session = session_factory()
        try:
            result = generate_pending_manager_summaries(session, summary_date=date.today(), limit=limit)
            logger.info(
                "scheduler_job=manager_summary_auto_generate_job summary_date=%s generated_count=%s generated_departments=%s skipped_departments=%s source_record_count=%s errors=%s",
                result.summary_date,
                len(result.generated_summary_ids),
                result.generated_department_ids,
                result.skipped_department_ids,
                result.source_record_count,
                result.errors,
            )
        finally:
            session.close()

    return handler
