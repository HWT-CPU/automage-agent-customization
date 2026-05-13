from __future__ import annotations

import argparse
import io
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from automage_agents.integrations.feishu.events import FeishuEventAdapter
from automage_agents.integrations.feishu.messages import FeishuMessageAdapter
from automage_agents.core.enums import InternalEventType
from automage_agents.core.models import SkillResult
from automage_agents.integrations.hermes import HermesOpenClawRuntime
from scripts.feishu_event_listener import (
    _build_real_openclaw_agent_message,
    _extract_agent_reply_text,
    _extract_feishu_file_metadata,
    _extract_text_from_file_bytes,
    _extract_tool_text,
    _file_text_from_extraction,
    _find_tool_summary,
    _load_user_mapping,
    _parse_json_object,
    _prepare_feishu_file_event,
    _run_real_openclaw_agent,
    _tool_called,
    FeishuFileExtraction,
)


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

    def test_feishu_event_adapter_maps_manager_summary_request(self) -> None:
        adapter = FeishuEventAdapter(user_mapping={"ou_manager_001": "lijingli"})
        event = adapter.from_message_receive_v1(
            {
                "event": {
                    "sender": {"sender_id": {"open_id": "ou_manager_001"}},
                    "message": {"message_id": "om_manager_summary", "content": json.dumps({"text": "请汇总这个员工日报文件"}, ensure_ascii=False)},
                }
            }
        )
        internal_event = adapter.to_internal_event(event)

        self.assertEqual(internal_event.actor_user_id, "lijingli")
        self.assertEqual(internal_event.event_type.value, "manager_feedback_submitted")

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

    def test_extracts_feishu_file_metadata_from_file_message_content(self) -> None:
        metadata = _extract_feishu_file_metadata(
            {
                "message_type": "file",
                "content": json.dumps({"file_key": "file_v2_abc", "file_name": "daily.md"}, ensure_ascii=False),
            }
        )

        self.assertEqual(metadata["file_key"], "file_v2_abc")
        self.assertEqual(metadata["file_name"], "daily.md")

    def test_extracts_feishu_file_metadata_from_nested_attachment_content(self) -> None:
        metadata = _extract_feishu_file_metadata(
            {
                "message_type": "text",
                "content": json.dumps({"text": "Manager 汇总已生成，报告 ID：..."}, ensure_ascii=False),
                "attachments": [
                    {
                        "file": {
                            "file_key": "file_v2_nested",
                            "name": "胡文涛日报（5月5日）.md",
                        }
                    }
                ],
            }
        )

        self.assertEqual(metadata["file_key"], "file_v2_nested")
        self.assertEqual(metadata["file_name"], "胡文涛日报（5月5日）.md")

    def test_prepare_feishu_file_event_downloads_text_file_into_message_text(self) -> None:
        class FakeResponse:
            file_name = "daily.md"
            file = io.BytesIO("今天完成了文件解析。遇到的问题是需要验证。明天继续联调。".encode("utf-8"))

            def success(self) -> bool:
                return True

        class FakeResource:
            def get(self, request: object) -> FakeResponse:
                return FakeResponse()

        class FakeV1:
            message_resource = FakeResource()

        class FakeIm:
            v1 = FakeV1()

        class FakeClient:
            im = FakeIm()

        raw_event = {
            "event": {
                "sender": {"sender_id": {"open_id": "ou_staff_001"}},
                "message": {
                    "message_id": "om_file",
                    "chat_id": "oc_test",
                    "message_type": "file",
                    "content": json.dumps({"file_key": "file_v2_abc", "file_name": "daily.md"}, ensure_ascii=False),
                },
            }
        }

        updated, extraction = _prepare_feishu_file_event(
            FakeClient(),
            raw_event,
            max_bytes=2000,
            max_chars=2000,
        )
        content = json.loads(updated["event"]["message"]["content"])

        self.assertIsNotNone(extraction)
        self.assertTrue(extraction.ok)
        self.assertIn("今天完成了文件解析", content["text"])

    def test_file_text_is_not_wrapped_by_listener_as_manager_summary_request(self) -> None:
        text = _file_text_from_extraction(
            FeishuFileExtraction(ok=True, text="员工完成了客户跟进，风险是合同模板未确认。", file_name="员工日报.md"),
        )

        self.assertNotIn("经理汇总", text)
        self.assertIn("员工日报.md", text)

    def test_extract_text_from_docx_bytes(self) -> None:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr(
                "word/document.xml",
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>今天完成了 DOCX 解析。</w:t></w:r></w:p></w:body></w:document>',
            )

        text, truncated = _extract_text_from_file_bytes(buffer.getvalue(), "daily.docx", max_chars=2000)

        self.assertFalse(truncated)
        self.assertIn("今天完成了 DOCX 解析", text)

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

    def test_real_openclaw_agent_prompt_requires_automage_tool(self) -> None:
        prompt = _build_real_openclaw_agent_message(
            text="查知识库 OpenAPI 契约",
            actor_external_id="ou_staff_001",
            event_id="om_test",
            chat_id="oc_test",
        )

        self.assertIn("必须调用 automage_openclaw_event 工具", prompt)
        self.assertIn('"actorExternalId": "ou_staff_001"', prompt)
        self.assertIn('"channel": "feishu"', prompt)
        self.assertIn("不要调用 memory_search", prompt)

    def test_real_openclaw_agent_prompt_forwards_feishu_file_payload(self) -> None:
        prompt = _build_real_openclaw_agent_message(
            text="文件名：daily.md\n\n今天完成了文件解析。",
            actor_external_id="ou_manager_001",
            event_id="om_file",
            chat_id="oc_test",
            payload={"feishu_file": {"ok": True, "file_name": "daily.md"}},
        )

        self.assertIn('"payload": {"feishu_file": {"ok": true, "file_name": "daily.md"}}', prompt)

    def test_real_openclaw_agent_tool_summary_detection(self) -> None:
        stdout = 'noise\n{"result": {"toolSummary": {"calls": 1, "tools": ["automage_openclaw_event"], "failures": 0}, "response": "ok"}}'
        parsed = _parse_json_object(stdout)
        summary = _find_tool_summary(parsed)

        self.assertEqual(summary["calls"], 1)
        self.assertTrue(_tool_called(summary, stdout))

    def test_real_openclaw_agent_reply_prefers_visible_text_over_json_response(self) -> None:
        body = {
            "result": {
                "response": json.dumps({"ok": True, "reply": {"text": "不应该返回整段 JSON"}}, ensure_ascii=False),
                "finalAssistantVisibleText": "知识库命中：OpenAPI 契约",
            }
        }

        self.assertEqual(_extract_agent_reply_text(body), "知识库命中：OpenAPI 契约")

    def test_real_openclaw_agent_reply_extracts_reply_text_from_json_string(self) -> None:
        body = {
            "result": {
                "toolSummary": {"calls": 1, "tools": ["automage_openclaw_event"], "failures": 0},
                "response": json.dumps({"ok": True, "reply": {"text": "当前没有待处理任务。"}}, ensure_ascii=False),
            }
        }

        self.assertEqual(_extract_agent_reply_text(body), "当前没有待处理任务。")

    def test_tool_reply_text_preferred_over_agent_fallback_text(self) -> None:
        body = {
            "result": {
                "finalAssistantVisibleText": "OpenClaw Agent 已通过 automage_openclaw_event 处理该 Feishu 消息。",
                "toolResults": [
                    {
                        "output": json.dumps(
                            {"ok": True, "reply": {"text": "Manager 汇总已生成，报告 ID：SUM123"}},
                            ensure_ascii=False,
                        )
                    }
                ],
            }
        }

        self.assertEqual(_extract_tool_text(body), "Manager 汇总已生成，报告 ID：SUM123")

    def test_real_openclaw_agent_runner_invokes_wsl_agent_with_tool_prompt(self) -> None:
        args = SimpleNamespace(
            openclaw_wsl_path="/fake/bin",
            openclaw_bridge_url="http://127.0.0.1:8000",
            openclaw_wsl_distro="Ubuntu-22.04",
            openclaw_bin="/fake/openclaw",
            openclaw_agent="main",
            openclaw_timeout_seconds=3,
        )
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps(
                {
                    "result": {
                        "toolSummary": {"calls": 1, "tools": ["automage_openclaw_event"], "failures": 0},
                        "response": "知识库命中：OpenAPI 契约",
                    }
                },
                ensure_ascii=False,
            ),
            stderr="",
        )

        with patch("scripts.feishu_event_listener.subprocess.run", return_value=completed) as mocked_run:
            result = _run_real_openclaw_agent(
                args,
                text="查知识库 OpenAPI 契约",
                actor_external_id="ou_staff_001",
                event_id="om_test",
                chat_id="oc_test",
            )

        command = mocked_run.call_args.args[0]
        self.assertTrue(result.ok)
        self.assertTrue(result.tool_called)
        self.assertIn("/fake/openclaw", command)
        self.assertIn("AUTOMAGE_OPENCLAW_BRIDGE_URL=http://127.0.0.1:8000", command)
        self.assertIn("AUTOMAGE_OPENCLAW_ACTOR_ID=ou_staff_001", command)
        self.assertIn("AUTOMAGE_OPENCLAW_ACCOUNT_ID=oc_test", command)
        self.assertNotIn("OPENCLAW_ACCOUNT_ID=oc_test", command)
        self.assertIn("必须调用 automage_openclaw_event 工具", command[command.index("--message") + 1])


if __name__ == "__main__":
    unittest.main()
