from __future__ import annotations

import base64
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from automage_agents.server.app import app
from tests.test_staff_daily_report_parser import SAMPLE_MARKDOWN


class DailyReportApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.auth_enabled_patcher = patch("automage_agents.server.auth._settings.auth_enabled", True)
        self.auth_token_patcher = patch("automage_agents.server.auth._settings.auth_token", "test-token")
        self.abuse_enabled_patcher = patch("automage_agents.server.middleware._settings.abuse_protection_enabled", False)
        self.auth_enabled_patcher.start()
        self.auth_token_patcher.start()
        self.abuse_enabled_patcher.start()

    def tearDown(self) -> None:
        self.client.close()
        self.auth_token_patcher.stop()
        self.auth_enabled_patcher.stop()
        self.abuse_enabled_patcher.stop()

    def _auth_headers(
        self,
        *,
        user_id: str = "user_agent_001",
        role: str = "staff",
        node_id: str = "staff_agent_mvp_001",
        level: str = "l1_staff",
        department_id: str | None = "dept_mvp_core",
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
        return headers

    def test_import_and_read_report(self) -> None:
        with patch(
            "automage_agents.server.daily_report_api.import_staff_daily_report_from_markdown",
            return_value={
                "template_id": 1,
                "work_record_id": 11,
                "work_record_public_id": "wr_demo",
                "item_count": 19,
                "staff_report_id": 7,
            },
        ), patch(
            "automage_agents.server.daily_report_api.read_staff_daily_report",
            side_effect=[
                {
                    "work_record_id": 11,
                    "work_record_public_id": "wr_demo",
                    "format": "json",
                    "meta": {"risk_level": "medium"},
                    "user_id": "user_agent_001",
                    "department_id": "dept_mvp_core",
                    "report": {
                        "basic_info": {"submitted_by": "Alice"},
                        "daily_summary": {"most_important_progress": "Parser schema aligned"},
                    },
                },
                {
                    "work_record_id": 11,
                    "work_record_public_id": "wr_demo",
                    "format": "markdown",
                    "meta": {"risk_level": "medium"},
                    "user_id": "user_agent_001",
                    "department_id": "dept_mvp_core",
                    "markdown": "# Staff Report\n\nAlice\n",
                },
            ],
        ):
            response = self.client.post(
                "/api/v1/report/staff/import-markdown",
                json={
                    "markdown": SAMPLE_MARKDOWN,
                    "org_id": 1,
                    "user_id": 1,
                    "department_id": 1,
                    "created_by": 1,
                    "include_staff_report_snapshot": True,
                    "include_source_markdown": True,
                    "snapshot_identity": {
                        "node_id": "staff-node-001",
                        "user_id": "user-001",
                        "role": "staff",
                    },
                },
                headers=self._auth_headers(),
            )
            self.assertEqual(response.status_code, 200)
            work_record_id = response.json()["data"]["record"]["work_record_id"]
            self.assertEqual(work_record_id, 11)

            json_response = self.client.get(
                f"/api/v1/report/staff/{work_record_id}?format=json",
                headers=self._auth_headers(),
            )
            self.assertEqual(json_response.status_code, 200)
            report = json_response.json()["data"]["report"]
            self.assertEqual(report["basic_info"]["submitted_by"], "Alice")

            markdown_response = self.client.get(
                f"/api/v1/report/staff/{work_record_id}?format=markdown",
                headers=self._auth_headers(),
            )
            self.assertEqual(markdown_response.status_code, 200)
            markdown = markdown_response.json()["data"]["markdown"]
            self.assertIn("Alice", markdown)

    def test_import_accepts_markdown_base64(self) -> None:
        encoded = base64.b64encode("# Example\n".encode("utf-8")).decode("ascii")
        with patch(
            "automage_agents.server.daily_report_api.import_staff_daily_report_from_markdown",
            return_value={
                "template_id": 1,
                "work_record_id": 12,
                "work_record_public_id": "wr_chinese",
                "item_count": 2,
                "staff_report_id": 8,
            },
        ) as import_mock:
            response = self.client.post(
                "/api/v1/report/staff/import-markdown",
                json={
                    "markdown_base64": encoded,
                    "org_id": 1,
                    "user_id": 2,
                    "department_id": 1,
                    "created_by": 2,
                    "include_staff_report_snapshot": True,
                    "include_source_markdown": True,
                },
                headers=self._auth_headers(),
            )
        self.assertEqual(response.status_code, 200)
        kwargs = import_mock.call_args.kwargs
        self.assertIsNone(kwargs["markdown"])
        self.assertEqual(kwargs["markdown_base64"], encoded)

    def test_import_requires_markdown_payload(self) -> None:
        response = self.client.post(
            "/api/v1/report/staff/import-markdown",
            json={"org_id": 1, "user_id": 2},
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 422)

    def test_staff_report_list_endpoint(self) -> None:
        with patch(
            "automage_agents.server.app.list_staff_reports",
            return_value=[
                {
                    "id": 1,
                    "node_id": "staff-node-001",
                    "user_id": "user_agent_001",
                    "role": "staff",
                    "report": {
                        "schema_id": "schema_v1_staff",
                        "org_id": "org_automage_mvp",
                        "department_id": "dept_mvp_core",
                        "record_date": "2026-05-06",
                    },
                }
            ],
        ) as report_mock:
            response = self.client.get(
                "/api/v1/report/staff",
                params={
                    "org_id": "org_automage_mvp",
                    "department_id": "dept_mvp_core",
                    "record_date": "2026-05-06",
                },
                headers=self._auth_headers(),
            )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["data"]["reports"][0]["report"]["schema_id"], "schema_v1_staff")
        self.assertEqual(report_mock.call_args.kwargs["department_id"], "dept_mvp_core")

    def test_manager_report_list_endpoint(self) -> None:
        with patch(
            "automage_agents.server.app.list_manager_reports",
            return_value=[
                {
                    "id": 2,
                    "node_id": "manager-node-001",
                    "user_id": "user_manager_001",
                    "role": "manager",
                    "report": {
                        "schema_id": "schema_v1_manager",
                        "org_id": "org_automage_mvp",
                        "dept_id": "dept_mvp_core",
                        "summary_date": "2026-05-06",
                        "manager_user_id": "user_manager_001",
                        "manager_node_id": "manager_agent_mvp_001",
                    },
                }
            ],
        ) as report_mock:
            response = self.client.get(
                "/api/v1/report/manager",
                params={
                    "org_id": "org_automage_mvp",
                    "summary_date": "2026-05-06",
                    "dept_id": "dept_mvp_core",
                },
                headers=self._auth_headers(
                    user_id="user_manager_001",
                    role="manager",
                    node_id="manager_agent_mvp_001",
                    level="l2_manager",
                ),
            )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["data"]["reports"][0]["report"]["schema_id"], "schema_v1_manager")
        self.assertEqual(report_mock.call_args.kwargs["dept_id"], "dept_mvp_core")

    def test_task_create_and_patch_endpoints(self) -> None:
        created_tasks = [
            {
                "id": 1,
                "task_id": "TASK-20260507-BACKEND-001",
                "assignee_user_id": "user_backend_001",
                "title": "Provide minimal API examples",
                "description": "Cover staff write, staff read and task read examples.",
                "status": "pending",
            }
        ]
        updated_task = {
            "id": 1,
            "task_id": "TASK-20260507-BACKEND-001",
            "assignee_user_id": "user_backend_001",
            "title": "Provide minimal API examples",
            "description": "Cover staff write, staff read and task read examples.",
            "status": "in_progress",
        }
        existing_task = type(
            "TaskRow",
            (),
            {
                "department_id": "dept_mvp_core",
                "meta": {"assignee_user_id": "user_backend_001", "department_id": "dept_mvp_core"},
            },
        )()

        with patch("automage_agents.server.app.create_tasks", return_value=created_tasks) as create_mock, patch(
            "automage_agents.server.app.update_task", return_value=updated_task
        ) as update_mock, patch(
            "automage_agents.server.app.get_task_by_task_id", return_value=existing_task
        ):
            create_response = self.client.post(
                "/api/v1/tasks",
                json={
                    "tasks": [
                        {
                            "schema_id": "schema_v1_task",
                            "schema_version": "1.0.0",
                            "task_id": "TASK-20260507-BACKEND-001",
                            "org_id": "org_automage_mvp",
                            "department_id": "dept_mvp_core",
                            "task_title": "Provide minimal API examples",
                            "task_description": "Cover staff write, staff read and task read examples.",
                            "source_type": "executive_decision",
                            "source_id": "DEC-20260506-001",
                            "creator_user_id": "user_executive_001",
                            "created_by_node_id": "executive_agent_boss_001",
                            "manager_user_id": "user_manager_001",
                            "manager_node_id": "manager_agent_mvp_001",
                            "assignee_user_id": "user_backend_001",
                            "priority": "critical",
                            "status": "pending",
                            "confirm_required": False,
                        }
                    ]
                },
                headers=self._auth_headers(
                    user_id="user_manager_001",
                    role="manager",
                    node_id="manager_agent_mvp_001",
                    level="l2_manager",
                ),
            )
            patch_response = self.client.patch(
                "/api/v1/tasks/TASK-20260507-BACKEND-001",
                json={"status": "in_progress"},
                headers=self._auth_headers(
                    user_id="user_backend_001",
                    role="staff",
                    node_id="staff_agent_backend_001",
                    level="l1_staff",
                ),
            )

        self.assertEqual(create_response.status_code, 200)
        self.assertEqual(create_response.json()["data"]["tasks"][0]["task_id"], "TASK-20260507-BACKEND-001")
        self.assertEqual(create_mock.call_args.kwargs["tasks"][0]["task_id"], "TASK-20260507-BACKEND-001")
        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(patch_response.json()["data"]["task"]["status"], "in_progress")
        self.assertEqual(update_mock.call_args.kwargs["task_id"], "TASK-20260507-BACKEND-001")

    def test_dream_run_endpoint(self) -> None:
        with patch(
            "automage_agents.server.app.run_dream_from_summary",
            return_value={
                "summary_id": 1,
                "summary_public_id": "SUM0001",
                "contract_status": "pending_dream_confirmation",
                "decision_options": [],
            },
        ) as dream_mock:
            response = self.client.post(
                "/internal/dream/run",
                json={"summary_id": "SUM0001"},
                headers=self._auth_headers(
                    user_id="user_executive_001",
                    role="executive",
                    node_id="executive_agent_boss_001",
                    level="l3_executive",
                ),
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["summary_public_id"], "SUM0001")
        self.assertEqual(dream_mock.call_args.kwargs["summary_id"], "SUM0001")

    def test_audit_log_list_endpoint(self) -> None:
        with patch(
            "automage_agents.server.app.list_audit_logs",
            return_value=[
                {
                    "id": 1,
                    "target_type": "tasks",
                    "action": "create_task",
                    "summary": "Created task",
                    "actor_user_id": "user_agent_001",
                    "payload": {"assignee_user_id": "user_agent_001"},
                }
            ],
        ) as audit_mock:
            response = self.client.get(
                "/api/v1/audit-logs",
                params={"target_type": "tasks", "limit": 20},
                headers=self._auth_headers(),
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["items"][0]["target_type"], "tasks")
        self.assertEqual(audit_mock.call_args.kwargs["target_type"], "tasks")

    def test_auth_requires_bearer_token_when_enabled(self) -> None:
        response = self.client.get("/api/v1/tasks")
        self.assertEqual(response.status_code, 401)
        self.assertIn("bearer token", response.json()["detail"])

    def test_staff_cannot_submit_manager_report(self) -> None:
        response = self.client.post(
            "/api/v1/report/manager",
            json={
                "identity": {
                    "node_id": "staff_agent_mvp_001",
                    "user_id": "user_agent_001",
                    "role": "staff",
                    "level": "l1_staff",
                    "department_id": "dept_mvp_core",
                    "manager_node_id": "manager_agent_mvp_001",
                },
                "report": {
                    "schema_id": "schema_v1_manager",
                    "org_id": "org_automage_mvp",
                    "dept_id": "dept_mvp_core",
                    "summary_date": "2026-05-06",
                    "aggregated_summary": "Need approval",
                },
            },
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 403)

    def test_staff_report_identity_must_match_authenticated_actor(self) -> None:
        response = self.client.post(
            "/api/v1/report/staff",
            json={
                "identity": {
                    "node_id": "staff_agent_mvp_001",
                    "user_id": "user_other_001",
                    "role": "staff",
                    "level": "l1_staff",
                    "department_id": "dept_mvp_core",
                    "manager_node_id": "manager_agent_mvp_001",
                },
                "report": {
                    "schema_id": "schema_v1_staff",
                    "org_id": "org_automage_mvp",
                    "department_id": "dept_mvp_core",
                    "record_date": "2026-05-06",
                    "work_progress": "done",
                    "risk_level": "medium",
                },
            },
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("does not match", response.json()["detail"])

    def test_staff_cannot_read_other_staff_report_detail(self) -> None:
        with patch(
            "automage_agents.server.daily_report_api.read_staff_daily_report",
            return_value={
                "work_record_id": 12,
                "work_record_public_id": "wr_other",
                "format": "json",
                "meta": {"risk_level": "low"},
                "user_id": "user_other_001",
                "department_id": "dept_other",
                "report": {"basic_info": {"submitted_by": "Other"}},
            },
        ):
            response = self.client.get(
                "/api/v1/report/staff/12?format=json",
                headers=self._auth_headers(),
            )
        self.assertEqual(response.status_code, 403)

    def test_invalid_staff_risk_level_returns_422(self) -> None:
        response = self.client.post(
            "/api/v1/report/staff",
            json={
                "identity": {
                    "node_id": "staff_agent_mvp_001",
                    "user_id": "user_agent_001",
                    "role": "staff",
                    "level": "l1_staff",
                    "department_id": "dept_mvp_core",
                    "manager_node_id": "manager_agent_mvp_001",
                },
                "report": {
                    "schema_id": "schema_v1_staff",
                    "org_id": "org_automage_mvp",
                    "department_id": "dept_mvp_core",
                    "record_date": "2026-05-06",
                    "work_progress": "done",
                    "risk_level": "urgent",
                },
            },
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 422)

    def test_staff_cannot_query_other_user_audit_logs(self) -> None:
        response = self.client.get(
            "/api/v1/audit-logs",
            params={"target_type": "tasks", "actor_user_id": "user_other_001"},
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 403)

    def test_idempotency_duplicate_write_returns_409_when_enabled(self) -> None:
        payload = {
            "tasks": [
                {
                    "schema_id": "schema_v1_task",
                    "schema_version": "1.0.0",
                    "task_id": "TASK-20260507-BACKEND-001",
                    "org_id": "org_automage_mvp",
                    "department_id": "dept_mvp_core",
                    "task_title": "Provide minimal API examples",
                    "task_description": "Cover staff write, staff read and task read examples.",
                    "source_type": "executive_decision",
                    "source_id": "DEC-20260506-001",
                    "creator_user_id": "user_executive_001",
                    "created_by_node_id": "executive_agent_boss_001",
                    "manager_user_id": "user_manager_001",
                    "manager_node_id": "manager_agent_mvp_001",
                    "assignee_user_id": "user_backend_001",
                    "priority": "critical",
                    "status": "pending",
                    "confirm_required": False,
                }
            ]
        }
        with patch("automage_agents.server.middleware._settings.abuse_protection_enabled", True), patch(
            "automage_agents.server.app.create_tasks",
            return_value=[{"task_id": "TASK-20260507-BACKEND-001"}],
        ):
            headers = self._auth_headers(
                user_id="user_manager_001",
                role="manager",
                node_id="manager_agent_mvp_001",
                level="l2_manager",
            )
            headers["Idempotency-Key"] = "dup-key-001"
            first = self.client.post("/api/v1/tasks", json=payload, headers=headers)
            second = self.client.post("/api/v1/tasks", json=payload, headers=headers)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 409)


if __name__ == "__main__":
    unittest.main()
