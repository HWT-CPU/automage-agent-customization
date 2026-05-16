from __future__ import annotations

import unittest
from typing import Any
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from automage_agents.db.base import Base
from automage_agents.db.models import (
    AuditLogModel,
    DepartmentModel,
    IncidentModel,
    OrganizationModel,
    StaffReportModel,
    TaskAssignmentModel,
    TaskModel,
    TaskQueueModel,
    TaskUpdateModel,
    UserModel,
    WorkRecordItemModel,
    WorkRecordModel,
)
from automage_agents.server.app import app
from automage_agents.server.deps import get_db_session


class IdempotencyFlowTests(unittest.TestCase):
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
            session.add_all(
                [
                    OrganizationModel(
                        id=1,
                        public_id="org_automage_mvp",
                        name="AutoMage MVP",
                        code="automage-mvp",
                    ),
                    UserModel(
                        id=10,
                        public_id="USR_EXEC_001",
                        org_id=1,
                        manager_user_id=None,
                        username="user_executive_001",
                        display_name="Executive User",
                        status=1,
                        meta={},
                    ),
                    UserModel(
                        id=20,
                        public_id="USR_MGR_001",
                        org_id=1,
                        manager_user_id=None,
                        username="user_manager_001",
                        display_name="Manager User",
                        status=1,
                        meta={},
                    ),
                    UserModel(
                        id=30,
                        public_id="USR_STAFF_001",
                        org_id=1,
                        manager_user_id=20,
                        username="user_agent_001",
                        display_name="Agent User",
                        status=1,
                        meta={},
                    ),
                    UserModel(
                        id=31,
                        public_id="USR_STAFF_002",
                        org_id=1,
                        manager_user_id=20,
                        username="user_backend_001",
                        display_name="Backend User",
                        status=1,
                        meta={},
                    ),
                    DepartmentModel(
                        id=100,
                        public_id="dept_mvp_core",
                        org_id=1,
                        manager_user_id=20,
                        name="Core Delivery",
                        code="core-delivery",
                        status=1,
                        meta={},
                    ),
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
        request_id: str | None = None,
        manager_node_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, str]:
        headers = {
            "Authorization": "Bearer test-token",
            "X-User-Id": user_id,
            "X-Role": role,
            "X-Node-Id": node_id,
            "X-Level": level,
            "X-Department-Id": "dept_mvp_core",
        }
        if request_id is not None:
            headers["X-Request-Id"] = request_id
        if manager_node_id is not None:
            headers["X-Manager-Node-Id"] = manager_node_id
        if idempotency_key is not None:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    def _staff_report_payload(self) -> dict[str, Any]:
        return {
            "identity": {
                "node_id": "staff_agent_mvp_001",
                "user_id": "user_agent_001",
                "role": "staff",
                "level": "l1_staff",
                "department_id": "dept_mvp_core",
                "manager_node_id": "manager_agent_mvp_001",
                "metadata": {"display_name": "张三"},
            },
            "report": {
                "schema_id": "schema_v1_staff",
                "schema_version": "1.0.0",
                "timestamp": "2026-05-07T10:30:00+08:00",
                "org_id": "org_automage_mvp",
                "department_id": "dept_mvp_core",
                "user_id": "user_agent_001",
                "node_id": "staff_agent_mvp_001",
                "record_date": "2026-05-07",
                "work_progress": "Completed idempotency verification for staff reports.",
                "issues_faced": [],
                "need_support": False,
                "next_day_plan": "Continue verifying task idempotency.",
                "risk_level": "low",
                "signature": {
                    "confirm_status": "confirmed",
                    "confirmed_by": "user_agent_001",
                },
            },
        }

    def _task_create_payload(self) -> dict[str, Any]:
        return {
            "tasks": [
                {
                    "schema_id": "schema_v1_task",
                    "schema_version": "1.0.0",
                    "task_id": "TASK-IDEMPOTENT-001",
                    "org_id": "org_automage_mvp",
                    "department_id": "dept_mvp_core",
                    "task_title": "Verify task create idempotency",
                    "task_description": "Retrying the same task create should return the existing row.",
                    "source_type": "executive_decision",
                    "source_id": "",
                    "creator_user_id": "user_manager_001",
                    "created_by_node_id": "manager_agent_mvp_001",
                    "manager_user_id": "user_manager_001",
                    "manager_node_id": "manager_agent_mvp_001",
                    "assignee_user_id": "user_backend_001",
                    "assignee_node_id": "staff_agent_backend_001",
                    "priority": "critical",
                    "status": "pending",
                }
            ]
        }

    def test_staff_report_duplicate_submit_returns_existing_record(self) -> None:
        payload = self._staff_report_payload()
        headers = self._auth_headers(
            user_id="user_agent_001",
            role="staff",
            node_id="staff_agent_mvp_001",
            level="l1_staff",
            request_id="staff-report-001",
            manager_node_id="manager_agent_mvp_001",
        )

        first = self.client.post("/api/v1/report/staff", json=payload, headers=headers)
        second = self.client.post("/api/v1/report/staff", json=payload, headers=headers)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)

        first_record = first.json()["data"]["record"]
        second_record = second.json()["data"]["record"]
        self.assertEqual(first_record["work_record_id"], second_record["work_record_id"])
        self.assertEqual(first_record["work_record_public_id"], second_record["work_record_public_id"])
        self.assertEqual(first_record["staff_report_id"], second_record["staff_report_id"])
        self.assertEqual(second_record["created_incidents"], [])

        with self.SessionLocal() as session:
            work_records = session.query(WorkRecordModel).all()
            self.assertEqual(len(work_records), 1)
            self.assertEqual(work_records[0].record_date.isoformat(), "2026-05-07")
            self.assertEqual(dict(work_records[0].meta or {}).get("request_id"), "staff-report-001")
            self.assertEqual(dict(work_records[0].meta or {}).get("source_user_id_text"), "user_agent_001")
            self.assertEqual(session.query(WorkRecordItemModel).count(), 19)
            self.assertEqual(session.query(StaffReportModel).count(), 1)
            self.assertEqual(session.query(IncidentModel).count(), 0)

            audit_logs = session.query(AuditLogModel).all()
            self.assertEqual(len(audit_logs), 1)
            self.assertEqual(dict(audit_logs[0].payload or {}).get("request_id"), "staff-report-001")

    def test_staff_report_duplicate_submit_with_different_content_returns_conflict(self) -> None:
        base_payload = self._staff_report_payload()
        headers = self._auth_headers(
            user_id="user_agent_001",
            role="staff",
            node_id="staff_agent_mvp_001",
            level="l1_staff",
            request_id="staff-report-002",
            manager_node_id="manager_agent_mvp_001",
        )

        first = self.client.post("/api/v1/report/staff", json=base_payload, headers=headers)
        self.assertEqual(first.status_code, 200)

        changed_payload = self._staff_report_payload()
        changed_payload["report"]["work_progress"] = "Changed content for the same business key."
        second = self.client.post("/api/v1/report/staff", json=changed_payload, headers=headers)

        self.assertEqual(second.status_code, 409)
        payload = second.json()
        self.assertEqual(payload["code"], 409)
        self.assertEqual(payload["msg"], "员工日报提交冲突")
        self.assertEqual(payload["error"]["error_code"], "staff_report_conflict")
        self.assertEqual(payload["error"]["conflict_target"], "staff_report:org_id+user_id+record_date")
        self.assertEqual(payload["error"]["request_id"], "staff-report-002")

        with self.SessionLocal() as session:
            self.assertEqual(session.query(WorkRecordModel).count(), 1)
            self.assertEqual(session.query(WorkRecordItemModel).count(), 19)
            self.assertEqual(session.query(StaffReportModel).count(), 1)
            self.assertEqual(session.query(AuditLogModel).count(), 1)

    def test_task_create_duplicate_submit_returns_existing_record_and_no_extra_rows(self) -> None:
        headers = self._auth_headers(
            user_id="user_manager_001",
            role="manager",
            node_id="manager_agent_mvp_001",
            level="l2_manager",
            request_id="task-create-001",
            manager_node_id="executive_agent_boss_001",
        )
        payload = self._task_create_payload()

        first = self.client.post("/api/v1/tasks", json=payload, headers=headers)
        second = self.client.post("/api/v1/tasks", json=payload, headers=headers)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.json()["data"]["tasks"][0]["task_id"], "TASK-IDEMPOTENT-001")
        self.assertEqual(first.json()["data"]["tasks"][0], second.json()["data"]["tasks"][0])

        with self.SessionLocal() as session:
            self.assertEqual(session.query(TaskModel).count(), 1)
            self.assertEqual(session.query(TaskAssignmentModel).count(), 1)
            self.assertEqual(session.query(TaskQueueModel).count(), 1)

            updates = session.query(TaskUpdateModel).order_by(TaskUpdateModel.id.asc()).all()
            self.assertEqual(len(updates), 1)
            self.assertEqual(dict(updates[0].meta or {}).get("event"), "task_created")
            self.assertEqual(dict(updates[0].meta or {}).get("request_id"), "task-create-001")

            audit_logs = session.query(AuditLogModel).order_by(AuditLogModel.id.asc()).all()
            self.assertEqual(len(audit_logs), 1)
            self.assertEqual(dict(audit_logs[0].payload or {}).get("request_id"), "task-create-001")

    def test_task_create_duplicate_submit_with_different_content_returns_conflict(self) -> None:
        headers = self._auth_headers(
            user_id="user_manager_001",
            role="manager",
            node_id="manager_agent_mvp_001",
            level="l2_manager",
            request_id="task-create-002",
            manager_node_id="executive_agent_boss_001",
        )
        payload = self._task_create_payload()

        first = self.client.post("/api/v1/tasks", json=payload, headers=headers)
        self.assertEqual(first.status_code, 200)

        changed_payload = self._task_create_payload()
        changed_payload["tasks"][0]["task_description"] = "Conflicting content for the same task id."
        second = self.client.post("/api/v1/tasks", json=changed_payload, headers=headers)

        self.assertEqual(second.status_code, 409)
        conflict = second.json()
        self.assertEqual(conflict["code"], 409)
        self.assertEqual(conflict["msg"], "任务创建冲突")
        self.assertEqual(conflict["error"]["error_code"], "task_create_conflict")
        self.assertEqual(conflict["error"]["conflict_target"], "task_create:task_id")
        self.assertEqual(conflict["error"]["request_id"], "task-create-002")

        with self.SessionLocal() as session:
            self.assertEqual(session.query(TaskModel).count(), 1)
            self.assertEqual(session.query(TaskAssignmentModel).count(), 1)
            self.assertEqual(session.query(TaskQueueModel).count(), 1)
            self.assertEqual(session.query(TaskUpdateModel).count(), 1)
            self.assertEqual(session.query(AuditLogModel).count(), 1)

    def test_task_update_same_request_id_replay_is_observable_and_does_not_duplicate_rows(self) -> None:
        create_headers = self._auth_headers(
            user_id="user_manager_001",
            role="manager",
            node_id="manager_agent_mvp_001",
            level="l2_manager",
            request_id="task-create-003",
            manager_node_id="executive_agent_boss_001",
        )
        create_response = self.client.post("/api/v1/tasks", json=self._task_create_payload(), headers=create_headers)
        self.assertEqual(create_response.status_code, 200)

        update_headers = self._auth_headers(
            user_id="user_backend_001",
            role="staff",
            node_id="staff_agent_backend_001",
            level="l1_staff",
            request_id="task-update-001",
            manager_node_id="manager_agent_mvp_001",
        )
        update_payload = {
            "status": "in_progress",
            "title": "Verify task create idempotency",
            "description": "Move the task into progress.",
            "task_payload": {"execution_note": "started"},
        }

        patch_first = self.client.patch("/api/v1/tasks/TASK-IDEMPOTENT-001", json=update_payload, headers=update_headers)
        patch_second = self.client.patch("/api/v1/tasks/TASK-IDEMPOTENT-001", json=update_payload, headers=update_headers)

        self.assertEqual(patch_first.status_code, 200)
        self.assertEqual(patch_second.status_code, 200)
        self.assertEqual(patch_first.json()["data"]["task"], patch_second.json()["data"]["task"])

        with self.SessionLocal() as session:
            task = session.query(TaskModel).one()
            self.assertEqual(task.status, 2)
            self.assertEqual(task.title, "Verify task create idempotency")
            self.assertEqual(task.description, "Move the task into progress.")
            self.assertEqual(dict(task.meta or {}).get("execution_note"), "started")

            updates = session.query(TaskUpdateModel).order_by(TaskUpdateModel.id.asc()).all()
            self.assertEqual(len(updates), 2)
            self.assertEqual(dict(updates[-1].meta or {}).get("request_id"), "task-update-001")
            self.assertEqual(dict(updates[-1].meta or {}).get("status"), "in_progress")
            self.assertEqual(dict(updates[-1].meta or {}).get("task_payload"), {"execution_note": "started"})

            audit_logs = session.query(AuditLogModel).order_by(AuditLogModel.id.asc()).all()
            self.assertEqual(len(audit_logs), 2)
            self.assertEqual(dict(audit_logs[-1].payload or {}).get("request_id"), "task-update-001")

    def test_task_update_same_request_id_with_different_content_returns_conflict(self) -> None:
        create_headers = self._auth_headers(
            user_id="user_manager_001",
            role="manager",
            node_id="manager_agent_mvp_001",
            level="l2_manager",
            request_id="task-create-004",
            manager_node_id="executive_agent_boss_001",
        )
        create_response = self.client.post("/api/v1/tasks", json=self._task_create_payload(), headers=create_headers)
        self.assertEqual(create_response.status_code, 200)

        update_headers = self._auth_headers(
            user_id="user_backend_001",
            role="staff",
            node_id="staff_agent_backend_001",
            level="l1_staff",
            request_id="task-update-002",
            manager_node_id="manager_agent_mvp_001",
        )
        first_payload = {
            "status": "in_progress",
            "title": "Verify task create idempotency",
            "description": "First version of the update.",
            "task_payload": {"execution_note": "started"},
        }
        second_payload = {
            "status": "done",
            "title": "Verify task create idempotency",
            "description": "Conflicting second version.",
            "task_payload": {"execution_note": "completed"},
        }

        first = self.client.patch("/api/v1/tasks/TASK-IDEMPOTENT-001", json=first_payload, headers=update_headers)
        self.assertEqual(first.status_code, 200)

        second = self.client.patch("/api/v1/tasks/TASK-IDEMPOTENT-001", json=second_payload, headers=update_headers)
        self.assertEqual(second.status_code, 409)
        conflict = second.json()
        self.assertEqual(conflict["code"], 409)
        self.assertEqual(conflict["msg"], "任务更新冲突")
        self.assertEqual(conflict["error"]["error_code"], "task_update_conflict")
        self.assertEqual(conflict["error"]["conflict_target"], "task_update:task_id+request_id")
        self.assertEqual(conflict["error"]["request_id"], "task-update-002")

        with self.SessionLocal() as session:
            task = session.query(TaskModel).one()
            self.assertEqual(task.status, 2)
            self.assertEqual(task.description, "First version of the update.")

            updates = session.query(TaskUpdateModel).order_by(TaskUpdateModel.id.asc()).all()
            self.assertEqual(len(updates), 2)
            self.assertEqual(dict(updates[-1].meta or {}).get("request_id"), "task-update-002")
            self.assertEqual(dict(updates[-1].meta or {}).get("description"), "First version of the update.")

            audit_logs = session.query(AuditLogModel).order_by(AuditLogModel.id.asc()).all()
            self.assertEqual(len(audit_logs), 2)

    def test_write_middleware_replays_idempotency_key_with_409_and_observable_headers(self) -> None:
        with patch("automage_agents.server.middleware._settings.abuse_protection_enabled", True):
            headers = self._auth_headers(
                user_id="user_manager_001",
                role="manager",
                node_id="manager_agent_mvp_001",
                level="l2_manager",
                request_id="task-create-005",
                manager_node_id="executive_agent_boss_001",
                idempotency_key="idem-task-create-001",
            )
            payload = self._task_create_payload()

            first = self.client.post("/api/v1/tasks", json=payload, headers=headers)
            second = self.client.post("/api/v1/tasks", json=payload, headers=headers)

            self.assertEqual(first.status_code, 200)
            self.assertEqual(first.headers.get("X-Idempotency-Key"), "idem-task-create-001")
            self.assertEqual(second.status_code, 409)
            self.assertEqual(second.json().get("idempotency_replayed"), True)
            self.assertEqual(second.json().get("request_id"), "task-create-005")

            with self.SessionLocal() as session:
                self.assertEqual(session.query(TaskModel).count(), 1)
                self.assertEqual(session.query(TaskAssignmentModel).count(), 1)
                self.assertEqual(session.query(TaskQueueModel).count(), 1)
                self.assertEqual(session.query(TaskUpdateModel).count(), 1)
                self.assertEqual(session.query(AuditLogModel).count(), 1)

    def test_write_middleware_rejects_same_idempotency_key_with_different_body(self) -> None:
        with patch("automage_agents.server.middleware._settings.abuse_protection_enabled", True), patch(
            "automage_agents.server.middleware._abuse_store", None
        ), patch("automage_agents.server.middleware._abuse_store_signature", None):
            headers = self._auth_headers(
                user_id="user_manager_001",
                role="manager",
                node_id="manager_agent_mvp_001",
                level="l2_manager",
                request_id="task-create-006",
                manager_node_id="executive_agent_boss_001",
                idempotency_key="idem-task-create-conflict-001",
            )
            first_payload = self._task_create_payload()
            second_payload = self._task_create_payload()
            second_payload["tasks"][0]["task_description"] = "Changed body for the same idempotency key."

            first = self.client.post("/api/v1/tasks", json=first_payload, headers=headers)
            second = self.client.post("/api/v1/tasks", json=second_payload, headers=headers)

            self.assertEqual(first.status_code, 200)
            self.assertEqual(second.status_code, 409)
            self.assertEqual(second.json().get("detail"), "idempotency_key_conflict")
            self.assertEqual(second.json().get("idempotency_conflict"), True)
            self.assertEqual(second.headers.get("X-Idempotency-Key"), "idem-task-create-conflict-001")

            with self.SessionLocal() as session:
                self.assertEqual(session.query(TaskModel).count(), 1)
                self.assertEqual(session.query(TaskAssignmentModel).count(), 1)
                self.assertEqual(session.query(TaskQueueModel).count(), 1)
                self.assertEqual(session.query(TaskUpdateModel).count(), 1)
                self.assertEqual(session.query(AuditLogModel).count(), 1)

    def test_write_middleware_rate_limits_write_protected_task_endpoint(self) -> None:
        with patch("automage_agents.server.middleware._settings.abuse_protection_enabled", True), patch(
            "automage_agents.server.middleware._settings.rate_limit_max_requests", 1
        ), patch("automage_agents.server.middleware._settings.rate_limit_window_seconds", 60), patch(
            "automage_agents.server.middleware._abuse_store", None
        ), patch("automage_agents.server.middleware._abuse_store_signature", None):
            first_headers = self._auth_headers(
                user_id="user_manager_001",
                role="manager",
                node_id="manager_agent_mvp_001",
                level="l2_manager",
                request_id="task-create-007",
                manager_node_id="executive_agent_boss_001",
            )
            second_headers = self._auth_headers(
                user_id="user_manager_001",
                role="manager",
                node_id="manager_agent_mvp_001",
                level="l2_manager",
                request_id="task-create-008",
                manager_node_id="executive_agent_boss_001",
            )
            second_payload = self._task_create_payload()
            second_payload["tasks"][0]["task_id"] = "TASK-IDEMPOTENT-002"

            first = self.client.post("/api/v1/tasks", json=self._task_create_payload(), headers=first_headers)
            second = self.client.post("/api/v1/tasks", json=second_payload, headers=second_headers)

            self.assertEqual(first.status_code, 200)
            self.assertEqual(second.status_code, 429)
            self.assertEqual(second.json().get("detail"), "rate_limit_exceeded")
            self.assertEqual(second.json().get("request_id"), "task-create-008")

            with self.SessionLocal() as session:
                self.assertEqual(session.query(TaskModel).count(), 1)
                self.assertEqual(session.query(TaskAssignmentModel).count(), 1)
                self.assertEqual(session.query(TaskQueueModel).count(), 1)
                self.assertEqual(session.query(TaskUpdateModel).count(), 1)
                self.assertEqual(session.query(AuditLogModel).count(), 1)


if __name__ == "__main__":
    unittest.main()
