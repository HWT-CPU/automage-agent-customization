from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path

from automage_agents.integrations.feishu.events import FeishuEventAdapter
from automage_agents.integrations.feishu.messages import FeishuMessageAdapter
from automage_agents.core.enums import InternalEventType
from automage_agents.core.models import SkillResult
from automage_agents.integrations.hermes import HermesOpenClawRuntime
from scripts.feishu_event_listener import _load_user_mapping


class FeishuImFlowTests(unittest.TestCase):
    def test_message_receive_routes_to_actor_staff_report(self) -> None:
        runtime = HermesOpenClawRuntime.from_demo_configs(
            settings_path="configs/automage.example.toml",
            user_mapping={"ou_staff_001": "staff_im_user_001"},
        )
        raw_event = {
            "header": {"event_type": "im.message.receive_v1"},
            "event": {
                "sender": {"sender_id": {"open_id": "ou_staff_001"}},
                "message": {
                    "message_id": "om_test_001",
                    "chat_id": "oc_test_001",
                    "chat_type": "p2p",
                    "message_type": "text",
                    "content": json.dumps(
                        {
                            "text": "今天完成了后端联调。遇到的问题是接口字段还需要确认。已处理补齐 smoke test。明天继续 Docker 验收。"
                        },
                        ensure_ascii=False,
                    ),
                    "create_time": "1778151600000",
                },
            },
        }

        result = runtime.handle_feishu_message_receive_v1(raw_event)

        self.assertTrue(result["ok"])
        self.assertEqual(result["actor_user_id"], "staff_im_user_001")
        self.assertEqual(len(runtime.contexts.state.staff_reports), 1)
        record = runtime.contexts.state.staff_reports[0]
        self.assertEqual(record["identity"]["user_id"], "staff_im_user_001")
        self.assertEqual(record["report"]["user_id"], "staff_im_user_001")
        self.assertIn("feishu_im", record["report"]["resource_usage"].get("other", ""))

    def test_feishu_event_adapter_maps_task_query(self) -> None:
        adapter = FeishuEventAdapter(user_mapping={"ou_staff_001": "staff_im_user_001"})
        event = adapter.from_message_receive_v1(
            {
                "event": {
                    "sender": {"sender_id": {"open_id": "ou_staff_001"}},
                    "message": {"message_id": "om_task", "content": json.dumps({"text": "查任务"})},
                }
            }
        )
        internal_event = adapter.to_internal_event(event)

        self.assertEqual(internal_event.actor_user_id, "staff_im_user_001")
        self.assertEqual(internal_event.event_type.value, "task_query_requested")

    def test_feishu_event_adapter_maps_dream_decision_request(self) -> None:
        adapter = FeishuEventAdapter(user_mapping={"ou_exec_001": "chenzong"})
        event = adapter.from_message_receive_v1(
            {
                "event": {
                    "sender": {"sender_id": {"open_id": "ou_exec_001"}},
                    "message": {"message_id": "om_dream", "content": json.dumps({"text": "生成决策草案 SUM123ABC"})},
                }
            }
        )
        internal_event = adapter.to_internal_event(event)

        self.assertEqual(internal_event.actor_user_id, "chenzong")
        self.assertEqual(internal_event.event_type.value, "dream_decision_requested")
        self.assertEqual(internal_event.payload["summary_id"], "SUM123ABC")

    def test_feishu_event_adapter_maps_executive_decision(self) -> None:
        adapter = FeishuEventAdapter(user_mapping={"ou_exec_001": "chenzong"})
        event = adapter.from_message_receive_v1(
            {
                "event": {
                    "sender": {"sender_id": {"open_id": "ou_exec_001"}},
                    "message": {"message_id": "om_decision", "content": json.dumps({"text": "确认方案B SUM123ABC"})},
                }
            }
        )
        internal_event = adapter.to_internal_event(event)

        self.assertEqual(internal_event.event_type.value, "executive_decision_selected")
        self.assertEqual(internal_event.payload["summary_id"], "SUM123ABC")
        self.assertEqual(internal_event.payload["selected_option_id"], "B")

    def test_feishu_event_adapter_maps_task_update(self) -> None:
        adapter = FeishuEventAdapter(user_mapping={"ou_staff_001": "zhangsan"})
        event = adapter.from_message_receive_v1(
            {
                "event": {
                    "sender": {"sender_id": {"open_id": "ou_staff_001"}},
                    "message": {"message_id": "om_task_done", "content": json.dumps({"text": "完成任务 TASK-ABC-001"})},
                }
            }
        )
        internal_event = adapter.to_internal_event(event)

        self.assertEqual(internal_event.event_type.value, "task_update_requested")
        self.assertEqual(internal_event.payload["task_id"], "TASK-ABC-001")
        self.assertEqual(internal_event.payload["status"], "completed")

    def test_confirm_decision_then_complete_task_in_mock_runtime(self) -> None:
        runtime = HermesOpenClawRuntime.from_demo_configs(
            settings_path="configs/automage.example.toml",
            user_mapping={"ou_exec_001": "executive-001", "ou_staff_001": "user-001"},
        )
        decision_event = {
            "event": {
                "sender": {"sender_id": {"open_id": "ou_exec_001"}},
                "message": {
                    "message_id": "om_confirm_decision",
                    "chat_id": "oc_test_001",
                    "content": json.dumps({"text": "确认方案B SUM-MOCK-001"}),
                },
            }
        }

        decision_result = runtime.handle_feishu_message_receive_v1(decision_event)

        self.assertTrue(decision_result["ok"])
        self.assertEqual(decision_result["event_type"], "executive_decision_selected")
        self.assertIn("mock-dream-SUM-MOCK-001-B-1", decision_result["data"]["generated_task_ids"])
        self.assertEqual(runtime.contexts.state.task_queue[0]["assignee_user_id"], "user-001")
        self.assertEqual(runtime.contexts.state.task_queue[0]["schema_id"], "schema_v1_task")
        self.assertEqual(runtime.contexts.state.task_queue[0]["task_title"], "Accelerate summary actions")

        task_event = {
            "event": {
                "sender": {"sender_id": {"open_id": "ou_staff_001"}},
                "message": {
                    "message_id": "om_complete_task",
                    "chat_id": "oc_test_001",
                    "content": json.dumps({"text": "完成任务 mock-dream-SUM-MOCK-001-B-1"}),
                },
            }
        }
        task_result = runtime.handle_feishu_message_receive_v1(task_event)

        self.assertTrue(task_result["ok"])
        self.assertEqual(task_result["event_type"], "task_update_requested")
        self.assertEqual(runtime.contexts.state.task_queue[0]["status"], "completed")

    def test_staff_cannot_confirm_executive_decision(self) -> None:
        runtime = HermesOpenClawRuntime.from_demo_configs(
            settings_path="configs/automage.example.toml",
            user_mapping={"ou_staff_001": "user-001"},
        )
        decision_event = {
            "event": {
                "sender": {"sender_id": {"open_id": "ou_staff_001"}},
                "message": {
                    "message_id": "om_staff_confirm_decision",
                    "chat_id": "oc_test_001",
                    "content": json.dumps({"text": "确认方案B SUM-MOCK-001"}),
                },
            }
        }

        result = runtime.handle_feishu_message_receive_v1(decision_event)

        self.assertFalse(result["ok"])
        self.assertEqual(result["error_code"], "permission_denied")
        self.assertIn("只有 Executive", result["message"])

    def test_executive_dream_reply_uses_schema_v1_executive_contract(self) -> None:
        runtime = HermesOpenClawRuntime.from_demo_configs(
            settings_path="configs/automage.example.toml",
            user_mapping={"ou_exec_001": "executive-001"},
        )
        dream_event = {
            "event": {
                "sender": {"sender_id": {"open_id": "ou_exec_001"}},
                "message": {
                    "message_id": "om_exec_dream",
                    "chat_id": "oc_test_001",
                    "content": json.dumps({"text": "生成决策草案 SUM-MOCK-001"}),
                },
            }
        }

        result = runtime.handle_feishu_message_receive_v1(dream_event)

        self.assertTrue(result["ok"])
        self.assertEqual(result["data"]["schema_id"], "schema_v1_executive")
        self.assertEqual(result["data"]["executive_user_id"], "executive-001")
        self.assertIn("option_a", result["data"])
        self.assertIn("option_b", result["data"])

    def test_report_text_containing_task_query_phrase_is_daily_report(self) -> None:
        adapter = FeishuEventAdapter(user_mapping={"ou_staff_001": "staff_im_user_001"})
        event = adapter.from_message_receive_v1(
            {
                "event": {
                    "sender": {"sender_id": {"open_id": "ou_staff_001"}},
                    "message": {
                        "message_id": "om_report_with_task_phrase",
                        "content": json.dumps(
                            {
                                "text": "今天完成了 Feishu IM 联调。遇到的问题是首次没有配置 open_id 映射。已处理映射并验证查任务成功。明天继续验证 Manager 汇总自动生成。"
                            },
                            ensure_ascii=False,
                        ),
                    },
                }
            }
        )
        internal_event = adapter.to_internal_event(event)

        self.assertEqual(internal_event.event_type.value, "daily_report_submitted")

    def test_listener_user_mapping_merges_json_and_inline_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "user-map.json"
            path.write_text(json.dumps({"ou_json": "json_user"}), encoding="utf-8")
            args = argparse.Namespace(user_map_json=str(path), map=["ou_inline=inline_user"])

            mapping = _load_user_mapping(args)

        self.assertEqual(mapping, {"ou_json": "json_user", "ou_inline": "inline_user"})

    def test_daily_report_success_reply_mentions_real_backend(self) -> None:
        adapter = FeishuMessageAdapter()
        message = adapter.build_processing_result_reply(
            "oc_test",
            InternalEventType.DAILY_REPORT_SUBMITTED.value,
            SkillResult(ok=True, data={"record": {"work_record_public_id": "wr_test"}}, message="员工日报提交成功"),
        )

        self.assertIn("已写入 AutoMage 后端", message.body)
        self.assertIn("wr_test", message.body)
        self.assertNotIn("mock backend", message.body)

    def test_daily_report_conflict_reply_is_actionable(self) -> None:
        adapter = FeishuMessageAdapter()
        message = adapter.build_processing_result_reply(
            "oc_test",
            InternalEventType.DAILY_REPORT_SUBMITTED.value,
            SkillResult(
                ok=False,
                data={
                    "response": {
                        "msg": "员工日报提交冲突",
                        "error": {
                            "error_code": "staff_report_conflict",
                            "message": "同一员工同一日期的日报已存在，且内容不一致",
                        },
                    }
                },
                message="员工日报提交冲突",
                error_code="conflict",
            ),
        )

        self.assertIn("今天的日报已存在", message.body)
        self.assertIn("后端已拦截", message.body)
        self.assertIn("错误码：staff_report_conflict", message.body)


if __name__ == "__main__":
    unittest.main()
