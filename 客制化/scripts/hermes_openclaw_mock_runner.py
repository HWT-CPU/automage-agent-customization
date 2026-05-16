from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.integrations.feishu.events import FeishuEvent
from automage_agents.integrations.hermes import HermesOpenClawRuntime


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", choices=["daily_report", "task_query", "manager_feedback", "executive_decision", "dream"], default="daily_report")
    args = parser.parse_args()

    runtime = HermesOpenClawRuntime.from_config_files(user_mapping={"staff-open-id": "user-001", "executive-open-id": "executive-001"})
    outputs: list[dict[str, Any]] = []

    if args.event == "daily_report":
        outputs.append(runtime.handle_feishu_event(_daily_report_event(), reply_target_id="mock-chat-staff"))
    elif args.event == "task_query":
        _seed_task(runtime)
        outputs.append(runtime.handle_feishu_event(_task_query_event(), reply_target_id="mock-chat-staff"))
    elif args.event == "manager_feedback":
        outputs.append(runtime.handle_feishu_event(_manager_feedback_event(), reply_target_id="mock-chat-manager"))
    elif args.event == "executive_decision":
        outputs.append(runtime.handle_feishu_event(_executive_decision_event(), reply_target_id="mock-chat-executive"))
    elif args.event == "dream":
        result = runtime.run_dream_decision(
            {
                "stage_goal": "验证 Hermes/OpenClaw Dream 决策入口",
                "manager_summary": {"overall_health": "yellow", "summary": "本地 mock 验证"},
                "external_variables": {"mode": "mock"},
            }
        )
        outputs.append({"ok": result.ok, "message": result.message, "data": result.data})

    print(json.dumps({"ok": all(item.get("ok", False) for item in outputs), "outputs": outputs, "state": runtime.state_summary()}, ensure_ascii=False, indent=2))


def _daily_report_event() -> FeishuEvent:
    return FeishuEvent(
        event_type="daily_report_submit",
        open_id="staff-open-id",
        message_id="hermes-msg-001",
        payload={
            "timestamp": "2026-05-06T16:30:00+08:00",
            "work_progress": "完成 Hermes/OpenClaw 本地 mock runtime 验证。",
            "issues_faced": "真实 OpenClaw 生命周期还未接入 SDK。",
            "solution_attempt": "先用本地 runtime 固定输入输出契约。",
            "need_support": False,
            "next_day_plan": "接真实 Feishu websocket 与后端 API。",
            "resource_usage": {"source": "hermes_mock", "chat_id": "mock-chat-staff"},
        },
    )


def _task_query_event() -> FeishuEvent:
    return FeishuEvent(event_type="task_query", open_id="staff-open-id", message_id="hermes-msg-002", payload={"status": "pending"})


def _manager_feedback_event() -> FeishuEvent:
    return FeishuEvent(
        event_type="manager_feedback",
        open_id="manager-open-id",
        message_id="hermes-msg-003",
        payload={
            "dept_id": "dept-sales",
            "overall_health": "yellow",
            "aggregated_summary": "团队整体推进正常，Hermes/OpenClaw 联调需要继续接真实平台。",
            "top_3_risks": ["真实 OpenClaw SDK 未接入", "真实后端 API 未启动"],
            "workforce_efficiency": 0.8,
            "pending_approvals": 1,
        },
    )


def _executive_decision_event() -> FeishuEvent:
    return FeishuEvent(
        event_type="executive_decision",
        open_id="executive-open-id",
        message_id="hermes-msg-004",
        payload={
            "selected_option_id": "A",
            "decision_summary": "先稳定本地 Hermes/OpenClaw 契约，再接真实平台。",
            "task_candidates": [
                {
                    "assignee_user_id": "user-001",
                    "title": "整理真实 OpenClaw 接入参数",
                    "description": "确认 SDK、事件格式、鉴权方式和回调生命周期。",
                }
            ],
        },
    )


def _seed_task(runtime: HermesOpenClawRuntime) -> None:
    runtime.handle_feishu_event(_executive_decision_event(), reply_target_id="mock-chat-executive")


if __name__ == "__main__":
    main()
