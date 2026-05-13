from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from automage_agents.integrations.openclaw.config import load_openclaw_config
from automage_agents.integrations.openclaw.parser import OpenClawCommandParser
from automage_agents.server.app import app
from automage_agents.server.openclaw_bridge_api import DEFAULT_USER_MAPPING, get_openclaw_runtime, load_openclaw_user_mapping


class OpenClawBridgeApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.abuse_enabled_patcher = patch("automage_agents.server.middleware._settings.abuse_protection_enabled", False)
        self.abuse_enabled_patcher.start()

    def tearDown(self) -> None:
        self.client.close()
        self.abuse_enabled_patcher.stop()

    def test_healthz(self) -> None:
        response = self.client.get("/openclaw/healthz")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["mode"], "http_channel_bridge")

    def test_submit_openclaw_channel_message_to_knowledge_skill(self) -> None:
        response = self.client.post(
            "/openclaw/events",
            json={
                "channel": "feishu",
                "accountId": "acct-test",
                "message": {
                    "id": "msg-test-001",
                    "text": "查知识库 OpenAPI 契约",
                    "from": {"id": "staff-open-id", "name": "Staff User"},
                    "timestamp": 1740000000000,
                    "attachments": [],
                },
            },
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["ok"])
        self.assertIn("text", body["reply"])
        self.assertEqual(body["response"]["event"]["event_id"], "msg-test-001")
        self.assertEqual(body["response"]["event"]["channel"], "feishu")
        self.assertEqual(body["response"]["skill_name"], "search_feishu_knowledge")
        self.assertEqual(body["response"]["hermes"]["actor_user_id"], "user-001")
        self.assertEqual(body["response"]["hermes"]["trace"]["correlation_id"], "msg-test-001")

    def test_submit_openclaw_channel_message_defaults_to_openclaw_channel(self) -> None:
        response = self.client.post(
            "/openclaw/events",
            json={
                "channel": "telegram",
                "message": {
                    "id": "msg-test-002",
                    "text": "查任务",
                    "from": {"id": "staff-open-id", "name": "Staff User"},
                },
            },
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["response"]["event"]["channel"], "openclaw")
        self.assertEqual(body["response"]["skill_name"], "fetch_my_tasks")

    def test_openclaw_bridge_merges_local_feishu_user_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "feishu_user_map.local.json"
            path.write_text(json.dumps({"ou_real_staff": "zhangsan"}), encoding="utf-8")

            mapping = load_openclaw_user_mapping(path)

        self.assertEqual(mapping["staff-open-id"], DEFAULT_USER_MAPPING["staff-open-id"])
        self.assertEqual(mapping["ou_real_staff"], "zhangsan")

    def test_openclaw_bridge_uses_configured_hermes_config_path(self) -> None:
        get_openclaw_runtime.cache_clear()
        with patch("automage_agents.server.openclaw_bridge_api.HermesOpenClawRuntime.from_config_files") as mocked_factory:
            with patch.dict("os.environ", {"AUTOMAGE_HERMES_CONFIG": "configs/hermes.local.toml"}, clear=False):
                get_openclaw_runtime()

        self.assertEqual(mocked_factory.call_args.kwargs["hermes_config_path"], "configs/hermes.local.toml")
        get_openclaw_runtime.cache_clear()

    def test_manager_command_payload_does_not_hardcode_demo_department(self) -> None:
        parser = OpenClawCommandParser(load_openclaw_config("configs/openclaw.example.toml"))

        parsed = parser.parse("manager summary: staff completed customer follow-up.")

        self.assertEqual(parsed.skill_name, "generate_manager_report")
        self.assertNotIn("dept_id", parsed.payload["report"])

    def test_manager_summary_request_routes_to_manager_skill(self) -> None:
        parser = OpenClawCommandParser(load_openclaw_config("configs/openclaw.example.toml"))

        parsed = parser.parse("请汇总这个员工日报文件")

        self.assertEqual(parsed.event_type, "manager_feedback")
        self.assertEqual(parsed.skill_name, "generate_manager_report")
        self.assertIn("请汇总这个员工日报文件", parsed.payload["report"]["aggregated_summary"])

    def test_manager_feishu_file_payload_routes_to_manager_skill(self) -> None:
        parser = OpenClawCommandParser(load_openclaw_config("configs/openclaw.example.toml"))

        parsed = parser.parse(
            "文件名：daily.md\n\n今天完成了文件解析。遇到的问题是需要验证。",
            actor_user_id="lijingli",
            manager_user_id="lijingli",
            payload={"feishu_file": {"ok": True, "file_name": "daily.md"}},
        )

        self.assertEqual(parsed.event_type, "manager_feedback")
        self.assertEqual(parsed.skill_name, "generate_manager_report")
        self.assertEqual(parsed.payload["report"]["feishu_file"]["file_name"], "daily.md")

    def test_staff_feishu_file_payload_still_routes_to_staff_daily_report(self) -> None:
        parser = OpenClawCommandParser(load_openclaw_config("configs/openclaw.example.toml"))

        parsed = parser.parse(
            "文件名：daily.md\n\n今天完成了文件解析。遇到的问题是需要验证。",
            actor_user_id="zhangsan",
            manager_user_id="lijingli",
            payload={"feishu_file": {"ok": True, "file_name": "daily.md"}},
        )

        self.assertEqual(parsed.skill_name, "post_daily_report")

    def test_bridge_forwards_feishu_file_payload_into_manager_skill(self) -> None:
        response = self.client.post(
            "/openclaw/events",
            json={
                "channel": "feishu",
                "accountId": "oc-test",
                "message": {
                    "id": "om-file-manager",
                    "text": "文件名：daily.md\n\n今天完成了文件解析。遇到的问题是需要验证。",
                    "from": {"id": "manager-open-id", "name": "Manager User"},
                    "attachments": [],
                },
                "payload": {"feishu_file": {"ok": True, "file_name": "daily.md"}},
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["response"]["skill_name"], "generate_manager_report")
        self.assertEqual(body["response"]["hermes"]["actor_user_id"], "manager-001")
        self.assertEqual(body["response"]["event"]["payload"]["feishu_file"]["file_name"], "daily.md")

    def test_bridge_returns_openclaw_missing_file_response_without_listener_reply(self) -> None:
        response = self.client.post(
            "/openclaw/events",
            json={
                "channel": "feishu",
                "message": {
                    "id": "om-file-missing",
                    "text": "请汇总这个员工日报文件",
                    "from": {"id": "manager-open-id", "name": "Manager User"},
                },
                "payload": {"feishu_file": {"ok": False, "requested": True, "error": "missing_attachment"}},
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["ok"])
        self.assertEqual(body["response"]["error_code"], "feishu_file_missing")
        self.assertIn("没有收到可汇总的文件附件", body["reply"]["text"])


if __name__ == "__main__":
    unittest.main()
