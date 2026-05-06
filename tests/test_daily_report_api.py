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

    def tearDown(self) -> None:
        pass

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
                    "markdown": "# AutoMage_2_Staff日报模板\n\n## 0. 基础信息\n\n| 字段 | 填写内容 |\n| --- | --- |\n| 提交人 | Alice |\n",
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
            )
            self.assertEqual(response.status_code, 200)
            payload = response.json()
            work_record_id = payload["data"]["record"]["work_record_id"]
            self.assertEqual(work_record_id, 11)

            json_response = self.client.get(f"/api/v1/report/staff/{work_record_id}?format=json")
            self.assertEqual(json_response.status_code, 200)
            report = json_response.json()["data"]["report"]
            self.assertEqual(report["basic_info"]["submitted_by"], "Alice")
            self.assertEqual(report["daily_summary"]["most_important_progress"], "Parser schema aligned")

            markdown_response = self.client.get(f"/api/v1/report/staff/{work_record_id}?format=markdown")
            self.assertEqual(markdown_response.status_code, 200)
            markdown = markdown_response.json()["data"]["markdown"]
            self.assertIn("## 0. 基础信息", markdown)
            self.assertIn("Alice", markdown)

    def test_import_accepts_markdown_base64(self) -> None:
        chinese_markdown = """# 示例

## 0. Basic Info

| Field | Value |
| --- | --- |
| report_date | 2026-05-05 |
| submitted_by | 熊锦文 |
"""
        encoded = base64.b64encode(chinese_markdown.encode("utf-8")).decode("ascii")

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
            )

        self.assertEqual(response.status_code, 200)
        kwargs = import_mock.call_args.kwargs
        self.assertIsNone(kwargs["markdown"])
        self.assertEqual(kwargs["markdown_base64"], encoded)

    def test_import_requires_markdown_payload(self) -> None:
        response = self.client.post(
            "/api/v1/report/staff/import-markdown",
            json={
                "org_id": 1,
                "user_id": 2,
            },
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
