from __future__ import annotations

import unittest
from datetime import date
from typing import Any
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from automage_agents.db.base import Base
from automage_agents.db.models import (
    AuditLogModel,
    DecisionRecordModel,
    DepartmentModel,
    ManagerReportModel,
    FormalDecisionLogModel,
    OrganizationModel,
    SummaryModel,
    SummarySourceLinkModel,
    TaskAssignmentModel,
    TaskModel,
    TaskQueueModel,
    TaskUpdateModel,
    UserModel,
    WorkRecordModel,
)
from automage_agents.server.app import app
from automage_agents.server.deps import get_db_session


class ManagerDecisionTaskFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.auth_enabled_patcher = patch("automage_agents.server.auth._settings.auth_enabled", True)
        self.auth_token_patcher = patch("automage_agents.server.auth._settings.auth_token", "test-token")
        self.auth_enabled_patcher.start()
        self.auth_token_patcher.start()

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

        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            future=True,
            class_=TestSession,
        )
        Base.metadata.create_all(self.engine)
        self._seed_reference_data()

        def override_get_db_session():
            session = self.SessionLocal()
            try:
                yield session
            finally:
                session.close()

        app.dependency_overrides[get_db_session] = override_get_db_session
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()
        app.dependency_overrides.clear()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()
        self.auth_token_patcher.stop()
        self.auth_enabled_patcher.stop()

    def _seed_reference_data(self) -> None:
        with self.SessionLocal() as session:
            org = OrganizationModel(
                id=1,
                public_id="org_automage_mvp",
                name="AutoMage MVP",
                code="automage-mvp",
            )
            executive = UserModel(
                id=10,
                public_id="USR_EXEC_001",
                org_id=1,
                manager_user_id=None,
                username="user_executive_001",
                display_name="Executive User",
                status=1,
                meta={},
            )
            manager = UserModel(
                id=20,
                public_id="USR_MGR_001",
                org_id=1,
                manager_user_id=None,
                username="user_manager_001",
                display_name="Manager User",
                status=1,
                meta={},
            )
            ops_manager = UserModel(
                id=21,
                public_id="USR_MGR_002",
                org_id=1,
                manager_user_id=None,
                username="user_manager_ops_001",
                display_name="Ops Manager",
                status=1,
                meta={},
            )
            staff = UserModel(
                id=30,
                public_id="USR_STAFF_001",
                org_id=1,
                manager_user_id=20,
                username="user_backend_001",
                display_name="Backend User",
                status=1,
                meta={},
            )
            other_staff = UserModel(
                id=31,
                public_id="USR_STAFF_002",
                org_id=1,
                manager_user_id=20,
                username="user_other_001",
                display_name="Other Staff",
                status=1,
                meta={},
            )
            ops_staff = UserModel(
                id=32,
                public_id="USR_STAFF_003",
                org_id=1,
                manager_user_id=21,
                username="user_ops_001",
                display_name="Ops Staff",
                status=1,
                meta={},
            )
            department = DepartmentModel(
                id=100,
                public_id="dept_mvp_core",
                org_id=1,
                manager_user_id=20,
                name="Core Delivery",
                code="core-delivery",
                status=1,
                meta={},
            )
            ops_department = DepartmentModel(
                id=101,
                public_id="dept_mvp_ops",
                org_id=1,
                manager_user_id=21,
                name="Ops Delivery",
                code="ops-delivery",
                status=1,
                meta={},
            )
            work_record = WorkRecordModel(
                id=1000,
                public_id="WR20260506CORE0000000001",
                org_id=1,
                department_id=100,
                template_id=1,
                user_id=30,
                record_date=date(2026, 5, 6),
                title="Seeded backend report",
                status=1,
                source_type=1,
                created_by=30,
                updated_by=30,
                meta={"seeded": True},
            )
            ops_work_record = WorkRecordModel(
                id=1001,
                public_id="WR20260506OPS00000000001",
                org_id=1,
                department_id=101,
                template_id=1,
                user_id=32,
                record_date=date(2026, 5, 6),
                title="Seeded ops report",
                status=1,
                source_type=1,
                created_by=32,
                updated_by=32,
                meta={"seeded": True},
            )
            session.add_all(
                [
                    org,
                    executive,
                    manager,
                    ops_manager,
                    staff,
                    other_staff,
                    ops_staff,
                    department,
                    ops_department,
                    work_record,
                    ops_work_record,
                ]
            )
            session.commit()

    def _auth_headers(
        self,
        *,
        user_id: str,
        role: str,
        node_id: str,
        level: str,
        department_id: str | None = "dept_mvp_core",
        manager_node_id: str | None = None,
    ) -> dict[str, str]:
        headers = {
            "Authorization": "Bearer test-token",
            "X-User-Id": user_id,
            "X-Role": role,
            "X-Node-Id": node_id,
            "X-Level": level,
        }
        if department_id is not None:
            headers["X-Department-Id"] = department_id
        if manager_node_id is not None:
            headers["X-Manager-Node-Id"] = manager_node_id
        return headers

    def _identity_payload(
        self,
        *,
        user_id: str,
        role: str,
        node_id: str,
        level: str,
        department_id: str | None = "dept_mvp_core",
        manager_node_id: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "node_id": node_id,
            "user_id": user_id,
            "role": role,
            "level": level,
            "department_id": department_id,
            "manager_node_id": manager_node_id,
            "metadata": {"display_name": user_id},
        }
        return payload

    def _create_committed_task_flow(self) -> dict[str, Any]:
        manager_data = self._create_manager_report(
            user_id="user_manager_001",
            node_id="manager_agent_mvp_001",
            department_id="dept_mvp_core",
            manager_node_id="executive_agent_boss_001",
            aggregated_summary="Need executive confirmation for backend follow-up tasks.",
            pending_approvals=1,
        )

        dream_response = self.client.post(
            "/internal/dream/run",
            json={"summary_id": manager_data["summary_public_id"]},
            headers=self._auth_headers(
                user_id="user_executive_001",
                role="executive",
                node_id="executive_agent_boss_001",
                level="l3_executive",
            ),
        )
        self.assertEqual(dream_response.status_code, 200)
        dream_data = dream_response.json()["data"]

        aggressive_option = next(
            option for option in dream_data["decision_options"] if option["option_id"] == "B"
        )
        task_candidate = dict(aggressive_option["task_candidates"][0])
        task_candidate.update(
            {
                "task_id": "TASK-REAL-FLOW-001",
                "org_id": "org_automage_mvp",
                "department_id": "dept_mvp_core",
                "source_summary_id": manager_data["summary_public_id"],
                "manager_user_id": "user_manager_001",
                "manager_node_id": "manager_agent_mvp_001",
                "assignee_user_id": "user_backend_001",
                "assignee_node_id": "staff_agent_backend_001",
            }
        )

        executive_identity = self._identity_payload(
            user_id="user_executive_001",
            role="executive",
            node_id="executive_agent_boss_001",
            level="l3_executive",
        )
        decision_response = self.client.post(
            "/api/v1/decision/commit",
            json={
                "identity": executive_identity,
                "decision": {
                    "org_id": "org_automage_mvp",
                    "department_id": "dept_mvp_core",
                    "summary_id": manager_data["summary_public_id"],
                    "title": "Promote manager summary actions",
                    "decision_summary": "Convert the dream option into an executable backend task.",
                    "selected_option_id": aggressive_option["option_id"],
                    "selected_option_label": aggressive_option["title"],
                    "decision_options": dream_data["decision_options"],
                    "priority": "critical",
                    "task_candidates": [task_candidate],
                },
            },
            headers=self._auth_headers(
                user_id="user_executive_001",
                role="executive",
                node_id="executive_agent_boss_001",
                level="l3_executive",
            ),
        )
        self.assertEqual(decision_response.status_code, 200)
        decision_data = decision_response.json()["data"]

        return {
            "manager": manager_data,
            "dream": dream_data,
            "decision": decision_data,
            "task_id": decision_data["task_ids"][0],
            "decision_public_id": decision_data["decision"]["decision_record_public_id"],
        }

    def _create_manager_report(
        self,
        *,
        user_id: str,
        node_id: str,
        department_id: str,
        manager_node_id: str,
        aggregated_summary: str,
        pending_approvals: int = 0,
        summary_date: str = "2026-05-06",
    ) -> dict[str, Any]:
        identity = self._identity_payload(
            user_id=user_id,
            role="manager",
            node_id=node_id,
            level="l2_manager",
            department_id=department_id,
            manager_node_id=manager_node_id,
        )
        response = self.client.post(
            "/api/v1/report/manager",
            json={
                "identity": identity,
                "report": {
                    "schema_id": "schema_v1_manager",
                    "schema_version": "1.0.0",
                    "timestamp": f"{summary_date}T18:00:00+08:00",
                    "org_id": "org_automage_mvp",
                    "dept_id": department_id,
                    "manager_user_id": user_id,
                    "manager_node_id": node_id,
                    "summary_date": summary_date,
                    "staff_report_count": 1,
                    "missing_report_count": 0,
                    "overall_health": "yellow",
                    "aggregated_summary": aggregated_summary,
                    "top_3_risks": ["Follow-up owner alignment"],
                    "pending_approvals": pending_approvals,
                },
            },
            headers=self._auth_headers(
                user_id=user_id,
                role="manager",
                node_id=node_id,
                level="l2_manager",
                department_id=department_id,
                manager_node_id=manager_node_id,
            ),
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["record"]

    def _create_task(
        self,
        *,
        task_id: str,
        department_id: str,
        manager_user_id: str,
        manager_node_id: str,
        assignee_user_id: str,
        assignee_node_id: str,
        actor_user_id: str = "user_executive_001",
        actor_role: str = "executive",
        actor_node_id: str = "executive_agent_boss_001",
        actor_level: str = "l3_executive",
    ) -> dict[str, Any]:
        response = self.client.post(
            "/api/v1/tasks",
            json={
                "tasks": [
                    {
                        "schema_id": "schema_v1_task",
                        "schema_version": "1.0.0",
                        "task_id": task_id,
                        "org_id": "org_automage_mvp",
                        "department_id": department_id,
                        "task_title": f"Task {task_id}",
                        "task_description": f"Description for {task_id}",
                        "source_type": "executive_decision",
                        "creator_user_id": "user_executive_001",
                        "created_by_node_id": "executive_agent_boss_001",
                        "manager_user_id": manager_user_id,
                        "manager_node_id": manager_node_id,
                        "assignee_user_id": assignee_user_id,
                        "assignee_node_id": assignee_node_id,
                        "priority": "high",
                        "status": "pending",
                    }
                ]
            },
            headers=self._auth_headers(
                user_id=actor_user_id,
                role=actor_role,
                node_id=actor_node_id,
                level=actor_level,
                department_id="dept_mvp_core" if actor_role != "executive" else None,
            ),
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["tasks"][0]

    def test_manager_to_dream_to_decision_to_task_flow_persists_real_records(self) -> None:
        flow = self._create_committed_task_flow()

        self.assertEqual(flow["dream"]["summary_public_id"], flow["manager"]["summary_public_id"])
        self.assertEqual({item["option_id"] for item in flow["dream"]["decision_options"]}, {"A", "B"})
        self.assertGreaterEqual(flow["manager"]["source_count"], 1)

        task_list_response = self.client.get(
            "/api/v1/tasks",
            params={"user_id": "user_someone_else"},
            headers=self._auth_headers(
                user_id="user_backend_001",
                role="staff",
                node_id="staff_agent_backend_001",
                level="l1_staff",
                manager_node_id="manager_agent_mvp_001",
            ),
        )
        self.assertEqual(task_list_response.status_code, 200)
        tasks = task_list_response.json()["data"]["tasks"]
        created_task = next(task for task in tasks if task["task_id"] == flow["task_id"])
        self.assertEqual(created_task["assignee_user_id"], "user_backend_001")
        self.assertEqual(created_task["status"], "pending")

        patch_response = self.client.patch(
            f"/api/v1/tasks/{flow['task_id']}",
            json={
                "status": "in_progress",
                "title": "Accelerate summary actions",
                "description": "Backend owner started execution from the executive decision.",
                "task_payload": {"execution_note": "picked_up"},
            },
            headers=self._auth_headers(
                user_id="user_backend_001",
                role="staff",
                node_id="staff_agent_backend_001",
                level="l1_staff",
                manager_node_id="manager_agent_mvp_001",
            ),
        )
        self.assertEqual(patch_response.status_code, 200)
        updated_task = patch_response.json()["data"]["task"]
        self.assertEqual(updated_task["status"], "in_progress")
        self.assertEqual(updated_task["task_payload"]["execution_note"], "picked_up")

        audit_response = self.client.get(
            "/api/v1/audit-logs",
            params={"limit": 50},
            headers=self._auth_headers(
                user_id="user_executive_001",
                role="executive",
                node_id="executive_agent_boss_001",
                level="l3_executive",
            ),
        )
        self.assertEqual(audit_response.status_code, 200)
        actions = {item["action"] for item in audit_response.json()["data"]["items"]}
        self.assertTrue(
            {"create_manager_report", "dream_run", "commit_decision", "create_task", "update_task"}.issubset(actions)
        )

        with self.SessionLocal() as session:
            summary_row = session.query(SummaryModel).filter(SummaryModel.id == flow["manager"]["summary_id"]).one()
            manager_snapshot = session.query(ManagerReportModel).filter(
                ManagerReportModel.id == flow["manager"]["manager_report_snapshot_id"]
            ).one()
            decision_record = (
                session.query(DecisionRecordModel)
                .filter(DecisionRecordModel.public_id == flow["decision_public_id"])
                .one()
            )
            task_row = session.query(TaskModel).filter(TaskModel.public_id == flow["task_id"]).one()
            queue_row = session.query(TaskQueueModel).filter(TaskQueueModel.task_id == flow["task_id"]).one()
            assignment_row = session.query(TaskAssignmentModel).filter(TaskAssignmentModel.task_id == task_row.id).one()
            formal_logs = (
                session.query(FormalDecisionLogModel)
                .filter(FormalDecisionLogModel.decision_record_id == decision_record.id)
                .all()
            )
            task_updates = session.query(TaskUpdateModel).filter(TaskUpdateModel.task_id == task_row.id).all()
            summary_links = (
                session.query(SummarySourceLinkModel)
                .filter(SummarySourceLinkModel.summary_id == flow["manager"]["summary_id"])
                .all()
            )
            audit_logs = session.query(AuditLogModel).all()

        self.assertTrue(summary_row.meta["need_executive_decision"])
        self.assertEqual(manager_snapshot.report_json["summary_public_id"], flow["manager"]["summary_public_id"])
        self.assertEqual(queue_row.status, "in_progress")
        self.assertEqual(assignment_row.user_id, 30)
        self.assertEqual(decision_record.source_summary_id, flow["manager"]["summary_id"])
        self.assertGreaterEqual(len(formal_logs), 2)
        self.assertGreaterEqual(len(task_updates), 2)
        self.assertGreaterEqual(len(summary_links), 1)
        self.assertGreaterEqual(len(audit_logs), 5)

    def test_unrelated_staff_cannot_see_or_update_task_from_decision_flow(self) -> None:
        flow = self._create_committed_task_flow()

        task_list_response = self.client.get(
            "/api/v1/tasks",
            params={"user_id": "user_backend_001"},
            headers=self._auth_headers(
                user_id="user_other_001",
                role="staff",
                node_id="staff_agent_other_001",
                level="l1_staff",
                manager_node_id="manager_agent_mvp_001",
            ),
        )
        self.assertEqual(task_list_response.status_code, 200)
        self.assertEqual(task_list_response.json()["data"]["tasks"], [])

        patch_response = self.client.patch(
            f"/api/v1/tasks/{flow['task_id']}",
            json={"status": "done"},
            headers=self._auth_headers(
                user_id="user_other_001",
                role="staff",
                node_id="staff_agent_other_001",
                level="l1_staff",
                manager_node_id="manager_agent_mvp_001",
            ),
        )
        self.assertEqual(patch_response.status_code, 403)
        self.assertIn("not allowed", patch_response.json()["detail"])

    def test_other_department_manager_cannot_view_core_department_task(self) -> None:
        flow = self._create_committed_task_flow()
        task_list_response = self.client.get(
            "/api/v1/tasks",
            params={"user_id": "user_backend_001"},
            headers=self._auth_headers(
                user_id="user_manager_ops_001",
                role="manager",
                node_id="manager_agent_ops_001",
                level="l2_manager",
                department_id="dept_mvp_ops",
                manager_node_id="executive_agent_boss_001",
            ),
        )
        self.assertEqual(task_list_response.status_code, 200)
        task_ids = [item["task_id"] for item in task_list_response.json()["data"]["tasks"]]
        self.assertNotIn(flow["task_id"], task_ids)

    def test_only_executive_can_run_dream_or_commit_decision(self) -> None:
        summary_public_id = self._create_manager_report(
            user_id="user_manager_001",
            node_id="manager_agent_mvp_001",
            department_id="dept_mvp_core",
            manager_node_id="executive_agent_boss_001",
            aggregated_summary="Manager-only draft",
            pending_approvals=1,
        )["summary_public_id"]
        manager_identity = self._identity_payload(
            user_id="user_manager_001",
            role="manager",
            node_id="manager_agent_mvp_001",
            level="l2_manager",
            manager_node_id="executive_agent_boss_001",
        )

        dream_response = self.client.post(
            "/internal/dream/run",
            json={"summary_id": summary_public_id},
            headers=self._auth_headers(
                user_id="user_manager_001",
                role="manager",
                node_id="manager_agent_mvp_001",
                level="l2_manager",
                manager_node_id="executive_agent_boss_001",
            ),
        )
        self.assertEqual(dream_response.status_code, 403)

        decision_response = self.client.post(
            "/api/v1/decision/commit",
            json={
                "identity": manager_identity,
                "decision": {
                    "org_id": "org_automage_mvp",
                    "department_id": "dept_mvp_core",
                    "summary_id": summary_public_id,
                    "selected_option_id": "A",
                },
            },
            headers=self._auth_headers(
                user_id="user_manager_001",
                role="manager",
                node_id="manager_agent_mvp_001",
                level="l2_manager",
                manager_node_id="executive_agent_boss_001",
            ),
        )
        self.assertEqual(decision_response.status_code, 403)

    def test_manager_cannot_submit_or_create_tasks_for_other_department(self) -> None:
        manager_identity = self._identity_payload(
            user_id="user_manager_001",
            role="manager",
            node_id="manager_agent_mvp_001",
            level="l2_manager",
            department_id="dept_mvp_core",
            manager_node_id="executive_agent_boss_001",
        )

        report_response = self.client.post(
            "/api/v1/report/manager",
            json={
                "identity": manager_identity,
                "report": {
                    "schema_id": "schema_v1_manager",
                    "org_id": "org_automage_mvp",
                    "dept_id": "dept_mvp_ops",
                    "manager_user_id": "user_manager_001",
                    "manager_node_id": "manager_agent_mvp_001",
                    "summary_date": "2026-05-06",
                    "aggregated_summary": "Attempt cross-department submit",
                },
            },
            headers=self._auth_headers(
                user_id="user_manager_001",
                role="manager",
                node_id="manager_agent_mvp_001",
                level="l2_manager",
                department_id="dept_mvp_core",
                manager_node_id="executive_agent_boss_001",
            ),
        )
        self.assertEqual(report_response.status_code, 403)
        self.assertIn("outside your RBAC scope", report_response.json()["detail"])

        task_response = self.client.post(
            "/api/v1/tasks",
            json={
                "tasks": [
                    {
                        "schema_id": "schema_v1_task",
                        "schema_version": "1.0.0",
                        "task_id": "TASK-CROSS-DEPT-001",
                        "org_id": "org_automage_mvp",
                        "department_id": "dept_mvp_ops",
                        "task_title": "Cross department task",
                        "task_description": "Manager should not create this",
                        "source_type": "manager_manual",
                        "creator_user_id": "user_executive_001",
                        "created_by_node_id": "executive_agent_boss_001",
                        "manager_user_id": "user_manager_001",
                        "manager_node_id": "manager_agent_mvp_001",
                        "assignee_user_id": "user_ops_001",
                        "assignee_node_id": "staff_agent_ops_001",
                        "priority": "high",
                        "status": "pending",
                    }
                ]
            },
            headers=self._auth_headers(
                user_id="user_manager_001",
                role="manager",
                node_id="manager_agent_mvp_001",
                level="l2_manager",
                department_id="dept_mvp_core",
                manager_node_id="executive_agent_boss_001",
            ),
        )
        self.assertEqual(task_response.status_code, 403)
        self.assertIn("outside your RBAC scope", task_response.json()["detail"])

        with self.SessionLocal() as session:
            denied_logs = session.query(AuditLogModel).filter(AuditLogModel.action == "permission_denied").all()

        self.assertGreaterEqual(len(denied_logs), 2)

    def test_manager_identity_department_mismatch_is_rejected_before_cross_department_submit(self) -> None:
        manager_identity = self._identity_payload(
            user_id="user_manager_001",
            role="manager",
            node_id="manager_agent_mvp_001",
            level="l2_manager",
            department_id="dept_other",
            manager_node_id="executive_agent_boss_001",
        )

        report_response = self.client.post(
            "/api/v1/report/manager",
            json={
                "identity": manager_identity,
                "report": {
                    "schema_id": "schema_v1_manager",
                    "org_id": "org_automage_mvp",
                    "dept_id": "dept_other",
                    "manager_user_id": "user_manager_001",
                    "manager_node_id": "manager_agent_mvp_001",
                    "summary_date": "2026-05-06",
                    "aggregated_summary": "Attempt submit with forged department identity",
                },
            },
            headers=self._auth_headers(
                user_id="user_manager_001",
                role="manager",
                node_id="manager_agent_mvp_001",
                level="l2_manager",
                department_id="dept_mvp_core",
                manager_node_id="executive_agent_boss_001",
            ),
        )
        self.assertEqual(report_response.status_code, 403)
        self.assertIn("outside your RBAC scope", report_response.json()["detail"])

        with self.SessionLocal() as session:
            denied_logs = session.query(AuditLogModel).filter(AuditLogModel.action == "permission_denied").all()

        self.assertGreaterEqual(len(denied_logs), 1)

    def test_manager_report_visibility_is_limited_to_actor_department(self) -> None:
        core_report = self._create_manager_report(
            user_id="user_manager_001",
            node_id="manager_agent_mvp_001",
            department_id="dept_mvp_core",
            manager_node_id="executive_agent_boss_001",
            aggregated_summary="Core summary",
            pending_approvals=1,
        )
        ops_report = self._create_manager_report(
            user_id="user_manager_ops_001",
            node_id="manager_agent_ops_001",
            department_id="dept_mvp_ops",
            manager_node_id="executive_agent_boss_001",
            aggregated_summary="Ops summary",
            pending_approvals=1,
        )

        visible_response = self.client.get(
            "/api/v1/report/manager",
            headers=self._auth_headers(
                user_id="user_manager_001",
                role="manager",
                node_id="manager_agent_mvp_001",
                level="l2_manager",
                department_id="dept_mvp_core",
                manager_node_id="executive_agent_boss_001",
            ),
        )
        self.assertEqual(visible_response.status_code, 200)
        visible_ids = {item["summary_public_id"] for item in visible_response.json()["data"]["reports"]}
        self.assertIn(core_report["summary_public_id"], visible_ids)
        self.assertNotIn(ops_report["summary_public_id"], visible_ids)

        filtered_other_dept_response = self.client.get(
            "/api/v1/report/manager",
            params={"dept_id": "dept_mvp_ops", "manager_user_id": "user_manager_ops_001"},
            headers=self._auth_headers(
                user_id="user_manager_001",
                role="manager",
                node_id="manager_agent_mvp_001",
                level="l2_manager",
                department_id="dept_mvp_core",
                manager_node_id="executive_agent_boss_001",
            ),
        )
        self.assertEqual(filtered_other_dept_response.status_code, 200)
        self.assertEqual(filtered_other_dept_response.json()["data"]["reports"], [])

    def test_staff_task_query_scope_is_forced_to_self_even_with_other_user_filters(self) -> None:
        own_task = self._create_task(
            task_id="TASK-STAFF-SCOPE-SELF",
            department_id="dept_mvp_core",
            manager_user_id="user_manager_001",
            manager_node_id="manager_agent_mvp_001",
            assignee_user_id="user_backend_001",
            assignee_node_id="staff_agent_backend_001",
        )
        other_task = self._create_task(
            task_id="TASK-STAFF-SCOPE-OTHER",
            department_id="dept_mvp_core",
            manager_user_id="user_manager_001",
            manager_node_id="manager_agent_mvp_001",
            assignee_user_id="user_other_001",
            assignee_node_id="staff_agent_other_001",
        )

        response = self.client.get(
            "/api/v1/tasks",
            params={"user_id": "user_other_001", "assignee_user_id": "user_other_001"},
            headers=self._auth_headers(
                user_id="user_backend_001",
                role="staff",
                node_id="staff_agent_backend_001",
                level="l1_staff",
                department_id="dept_mvp_core",
                manager_node_id="manager_agent_mvp_001",
            ),
        )
        self.assertEqual(response.status_code, 200)
        task_ids = {item["task_id"] for item in response.json()["data"]["tasks"]}
        self.assertIn(own_task["task_id"], task_ids)
        self.assertNotIn(other_task["task_id"], task_ids)

    def test_staff_cannot_query_manager_reports_or_update_cross_department_task(self) -> None:
        self._create_manager_report(
            user_id="user_manager_ops_001",
            node_id="manager_agent_ops_001",
            department_id="dept_mvp_ops",
            manager_node_id="executive_agent_boss_001",
            aggregated_summary="Ops summary",
            pending_approvals=1,
        )
        ops_task = self._create_task(
            task_id="TASK-OPS-001",
            department_id="dept_mvp_ops",
            manager_user_id="user_manager_ops_001",
            manager_node_id="manager_agent_ops_001",
            assignee_user_id="user_ops_001",
            assignee_node_id="staff_agent_ops_001",
        )

        report_response = self.client.get(
            "/api/v1/report/manager",
            headers=self._auth_headers(
                user_id="user_backend_001",
                role="staff",
                node_id="staff_agent_backend_001",
                level="l1_staff",
                department_id="dept_mvp_core",
                manager_node_id="manager_agent_mvp_001",
            ),
        )
        self.assertEqual(report_response.status_code, 403)

        patch_response = self.client.patch(
            f"/api/v1/tasks/{ops_task['task_id']}",
            json={"status": "done"},
            headers=self._auth_headers(
                user_id="user_backend_001",
                role="staff",
                node_id="staff_agent_backend_001",
                level="l1_staff",
                department_id="dept_mvp_core",
                manager_node_id="manager_agent_mvp_001",
            ),
        )
        self.assertEqual(patch_response.status_code, 403)
        self.assertIn("not allowed", patch_response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
