from __future__ import annotations

import json
import unittest

from automage_agents.integrations.hermes import HermesOpenClawRuntime
from automage_agents.integrations.production_loop import FeishuProductionLoop, ProductionLoopOptions


class FeishuProductionLoopTests(unittest.TestCase):
    def test_staff_report_generates_manager_dream_and_task_when_auto_confirmed(self) -> None:
        runtime = HermesOpenClawRuntime.from_demo_configs(
            settings_path="configs/automage.example.toml",
            user_mapping={"ou_staff_prod": "user-001"},
        )
        loop = FeishuProductionLoop(runtime, ProductionLoopOptions(auto_confirm_decision=True, option_id="B"))

        result = loop.handle_staff_daily_report(
            _raw_text_event(
                "ou_staff_prod",
                "今天完成了 Feishu 生产闭环联调。遇到的问题是需要自动生成 Manager 汇总。已处理编排。明天继续部署。",
            )
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["stage"], "executive_decision")
        self.assertTrue(result["staff_report"]["ok"])
        self.assertTrue(result["manager_summary"]["ok"])
        self.assertTrue(result["executive_dream"]["ok"])
        self.assertTrue(result["executive_decision"]["ok"])
        self.assertEqual(len(runtime.contexts.state.staff_reports), 1)
        self.assertEqual(len(runtime.contexts.state.manager_reports), 1)
        self.assertEqual(len(runtime.contexts.state.decision_logs), 1)
        self.assertEqual(len(runtime.contexts.state.task_queue), 1)
        self.assertEqual(runtime.contexts.state.task_queue[0]["task_id"], "mock-dream-mock-summary-1-B-1")

    def test_staff_report_notifies_manager_and_executive_without_auto_confirm(self) -> None:
        runtime = HermesOpenClawRuntime.from_demo_configs(
            settings_path="configs/automage.example.toml",
            user_mapping={"ou_staff_prod": "user-001"},
        )
        loop = FeishuProductionLoop(
            runtime,
            ProductionLoopOptions(manager_target_id="manager-user", executive_target_id="executive-user"),
        )

        result = loop.handle_staff_daily_report(_raw_text_event("ou_staff_prod", "今天完成了日报闭环。遇到的问题是需要老板看决策。已处理。明天继续。"))

        self.assertTrue(result["ok"])
        self.assertEqual(result["stage"], "executive_dream")
        self.assertEqual(len(result["notifications"]), 2)
        self.assertEqual(result["notifications"][0]["channel"], "feishu_mock")
        self.assertEqual(result["notifications"][1]["target_user_id"], "executive-user")
        self.assertEqual(len(runtime.contexts.state.task_queue), 0)


def _raw_text_event(open_id: str, text: str) -> dict:
    return {
        "event": {
            "sender": {"sender_id": {"open_id": open_id}},
            "message": {
                "message_id": "om_prod_test",
                "chat_id": "oc_prod_test",
                "chat_type": "p2p",
                "message_type": "text",
                "content": json.dumps({"text": text}, ensure_ascii=False),
            },
        }
    }


if __name__ == "__main__":
    unittest.main()
