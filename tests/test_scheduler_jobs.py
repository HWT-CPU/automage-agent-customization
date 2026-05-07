from __future__ import annotations

import unittest
from datetime import date
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from automage_agents.db.base import Base
from automage_agents.db.models import DepartmentModel, ManagerReportModel, OrganizationModel, SummaryModel, SummarySourceLinkModel, TaskModel, UserModel, WorkRecordModel
from automage_agents.scheduler.services import (
    collect_missing_staff_daily_reports,
    collect_overdue_tasks,
    collect_pending_manager_summaries,
    generate_pending_manager_summaries,
)


class SchedulerJobServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            future=True,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

        class TestSession(Session):
            pass

        self._id_counters: dict[str, int] = {}

        @event.listens_for(TestSession, "before_flush")
        def assign_sqlite_ids(session: Session, flush_context: Any, instances: Any) -> None:
            del flush_context, instances
            for obj in session.new:
                if not hasattr(obj, "id") or getattr(obj, "id") is not None:
                    continue
                table_name = getattr(obj, "__tablename__", obj.__class__.__name__)
                next_id = self._id_counters.get(table_name, 0) + 1
                self._id_counters[table_name] = next_id
                setattr(obj, "id", next_id)

        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, future=True, class_=TestSession)
        Base.metadata.create_all(self.engine)
        self._seed()

    def tearDown(self) -> None:
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def _seed(self) -> None:
        with self.SessionLocal() as session:
            session.add_all(
                [
                    OrganizationModel(id=1, public_id="org_automage_mvp", name="AutoMage MVP", code="automage-mvp"),
                    UserModel(id=20, public_id="USR_MGR_001", org_id=1, manager_user_id=None, username="user_manager_001", display_name="Manager 1", status=1, meta={}),
                    UserModel(id=21, public_id="USR_MGR_002", org_id=1, manager_user_id=None, username="user_manager_ops_001", display_name="Manager 2", status=1, meta={}),
                    UserModel(id=30, public_id="USR_STAFF_001", org_id=1, manager_user_id=20, username="user_backend_001", display_name="Backend", status=1, meta={}),
                    UserModel(id=31, public_id="USR_STAFF_002", org_id=1, manager_user_id=20, username="user_other_001", display_name="Other", status=1, meta={}),
                    UserModel(id=32, public_id="USR_STAFF_003", org_id=1, manager_user_id=21, username="user_ops_001", display_name="Ops", status=1, meta={}),
                    DepartmentModel(id=100, public_id="dept_mvp_core", org_id=1, manager_user_id=20, name="Core", code="core", status=1, meta={}),
                    DepartmentModel(id=101, public_id="dept_mvp_ops", org_id=1, manager_user_id=21, name="Ops", code="ops", status=1, meta={}),
                    WorkRecordModel(
                        id=1000,
                        public_id="WR1",
                        org_id=1,
                        department_id=100,
                        template_id=1,
                        user_id=30,
                        record_date=date(2026, 5, 7),
                        title="submitted",
                        status=1,
                        source_type=1,
                        created_by=30,
                        updated_by=30,
                        meta={},
                    ),
                    WorkRecordModel(
                        id=1001,
                        public_id="WR_OPS_1",
                        org_id=1,
                        department_id=101,
                        template_id=1,
                        user_id=32,
                        record_date=date(2026, 5, 7),
                        title="ops submitted",
                        status=1,
                        source_type=1,
                        created_by=32,
                        updated_by=32,
                        meta={"risk_level": "low", "need_support": False},
                    ),
                    SummaryModel(
                        id=2000,
                        public_id="SUM1",
                        org_id=1,
                        department_id=100,
                        user_id=None,
                        summary_type=1,
                        scope_type=2,
                        summary_date=date(2026, 5, 7),
                        status=1,
                        title="core summary",
                        content="done",
                        source_count=1,
                        generated_by_type=2,
                        created_by=20,
                        updated_by=20,
                        meta={},
                    ),
                    TaskModel(
                        id=3000,
                        public_id="TASK1",
                        org_id=1,
                        department_id=100,
                        decision_record_id=None,
                        source_record_id=None,
                        creator_user_id=20,
                        title="pending task",
                        description="pending",
                        status=1,
                        priority=2,
                        created_by=20,
                        updated_by=20,
                        meta={},
                    ),
                ]
            )
            session.commit()

    def test_collect_missing_staff_daily_reports(self) -> None:
        with self.SessionLocal() as session:
            result = collect_missing_staff_daily_reports(session, record_date=date(2026, 5, 7), limit=100)
        self.assertEqual(sorted(result.missing_user_ids), ["user_other_001"])

    def test_collect_pending_manager_summaries(self) -> None:
        with self.SessionLocal() as session:
            result = collect_pending_manager_summaries(session, summary_date=date(2026, 5, 7), limit=100)
        self.assertEqual(result.pending_manager_user_ids, ["user_manager_ops_001"])

    def test_collect_overdue_tasks(self) -> None:
        with self.SessionLocal() as session:
            result = collect_overdue_tasks(session, limit=100)
        self.assertEqual(result, ["TASK1"])

    def test_generate_pending_manager_summaries(self) -> None:
        with self.SessionLocal() as session:
            result = generate_pending_manager_summaries(session, summary_date=date(2026, 5, 7), limit=100)
            self.assertEqual(result.generated_department_ids, ["dept_mvp_ops"])
            self.assertIn("dept_mvp_core", result.skipped_department_ids)
            self.assertEqual(result.source_record_count, 1)
            self.assertEqual(result.errors, [])
            summary = session.query(SummaryModel).filter(SummaryModel.department_id == 101).one()
            self.assertEqual(summary.source_count, 1)
            self.assertIn("ops submitted", summary.content)
            self.assertEqual(session.query(ManagerReportModel).count(), 1)
            link = session.query(SummarySourceLinkModel).filter(SummarySourceLinkModel.summary_id == summary.id).one()
            self.assertEqual(link.source_id, 1001)

            second_result = generate_pending_manager_summaries(session, summary_date=date(2026, 5, 7), limit=100)
            self.assertEqual(second_result.generated_department_ids, [])
            self.assertIn("dept_mvp_ops", second_result.skipped_department_ids)
            self.assertEqual(session.query(SummaryModel).filter(SummaryModel.department_id == 101).count(), 1)
