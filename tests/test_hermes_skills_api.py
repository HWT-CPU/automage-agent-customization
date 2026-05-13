from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from automage_agents.server.app import app


class HermesSkillsApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.abuse_enabled_patcher = patch("automage_agents.server.middleware._settings.abuse_protection_enabled", False)
        self.abuse_enabled_patcher.start()

    def tearDown(self) -> None:
        self.client.close()
        self.abuse_enabled_patcher.stop()

    def test_list_skills_includes_core_automage_skills(self) -> None:
        response = self.client.get("/hermes/skills")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["ok"])
        skill_names = {skill["name"] for skill in body["skills"]}
        self.assertIn("post_daily_report", skill_names)
        self.assertIn("search_feishu_knowledge", skill_names)
        self.assertIn("commit_decision", skill_names)

    def test_unknown_skill_returns_404(self) -> None:
        response = self.client.post(
            "/hermes/skills/not_a_skill/invoke",
            json={"actor_user_id": "user-001", "payload": {}},
        )
        self.assertEqual(response.status_code, 404)

    def test_invoke_search_knowledge_skill_returns_hermes_envelope(self) -> None:
        response = self.client.post(
            "/hermes/skills/search_feishu_knowledge/invoke",
            json={
                "actor_user_id": "user-001",
                "payload": {"query": "OpenAPI 契约", "limit": 1, "max_context_chars": 500},
                "trace": {"correlation_id": "test-correlation-001"},
            },
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["skill_name"], "search_feishu_knowledge")
        self.assertEqual(body["actor_user_id"], "user-001")
        self.assertEqual(body["trace"]["correlation_id"], "test-correlation-001")
        self.assertIn("ok", body["result"])
        self.assertIn("data", body["result"])


if __name__ == "__main__":
    unittest.main()
