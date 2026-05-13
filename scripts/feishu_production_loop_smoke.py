from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from typing import Any

from automage_agents.integrations.hermes import HermesOpenClawRuntime
from automage_agents.integrations.production_loop import FeishuProductionLoop, ProductionLoopOptions

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    args = _parse_args()
    runtime = HermesOpenClawRuntime.from_demo_configs(
        staff_user_path=args.staff_profile,
        manager_user_path=args.manager_profile,
        executive_user_path=args.executive_profile,
        settings_path=args.settings,
        user_mapping={args.staff_open_id: args.staff_user_id},
        auto_initialize=not args.skip_init,
    )
    loop = FeishuProductionLoop(
        runtime,
        ProductionLoopOptions(
            manager_target_id=args.manager_target_id,
            executive_target_id=args.executive_target_id,
            auto_confirm_decision=args.auto_confirm_decision,
            option_id=args.option_id,
        ),
    )
    result = loop.handle_staff_daily_report(_raw_feishu_text_event(args.staff_open_id, args.message_id, args.text, args.chat_id))
    summary = _summary(result, runtime)
    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as file:
            json.dump(result, file, ensure_ascii=False, indent=2)
    print(json.dumps(summary if args.summary_only else result, ensure_ascii=False, indent=2))
    if not result.get("ok"):
        raise SystemExit(1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test the Feishu staff report -> Manager summary -> Executive decision production loop.")
    parser.add_argument("--settings", default="configs/automage.example.toml")
    parser.add_argument("--staff-profile", default="examples/user.staff.example.toml")
    parser.add_argument("--manager-profile", default="examples/user.manager.example.toml")
    parser.add_argument("--executive-profile", default="examples/user.executive.example.toml")
    parser.add_argument("--staff-open-id", default="ou_staff_prod_001")
    parser.add_argument("--staff-user-id", default="user-001")
    parser.add_argument("--chat-id", default="oc_prod_loop")
    parser.add_argument("--message-id", default="om_prod_loop_001")
    parser.add_argument("--text", default="今天完成了真实 Feishu 员工日报到 Manager 汇总的联调。遇到的问题是需要把闭环自动编排起来。已处理 Hermes 和 OpenClaw 验证。明天继续做生产部署。")
    parser.add_argument("--manager-target-id")
    parser.add_argument("--executive-target-id")
    parser.add_argument("--auto-confirm-decision", action="store_true")
    parser.add_argument("--option-id", default="B")
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--output-json")
    parser.add_argument("--skip-init", action="store_true")
    return parser.parse_args()


def _raw_feishu_text_event(open_id: str, message_id: str, text: str, chat_id: str) -> dict[str, Any]:
    return {
        "header": {"event_type": "im.message.receive_v1"},
        "event": {
            "sender": {"sender_id": {"open_id": open_id}},
            "message": {
                "message_id": message_id,
                "chat_id": chat_id,
                "chat_type": "p2p",
                "message_type": "text",
                "content": json.dumps({"text": text}, ensure_ascii=False),
                "create_time": str(int(datetime.now().timestamp() * 1000)),
            },
        },
    }


def _summary(result: dict[str, Any], runtime: HermesOpenClawRuntime) -> dict[str, Any]:
    manager = result.get("manager_summary") or {}
    dream = result.get("executive_dream") or {}
    decision = result.get("executive_decision") or {}
    task_ids = decision.get("data", {}).get("generated_task_ids") or decision.get("data", {}).get("task_ids") or []
    return {
        "ok": result.get("ok"),
        "stage": result.get("stage"),
        "staff_report_ok": result.get("staff_report", {}).get("ok"),
        "manager_summary_ok": manager.get("ok"),
        "manager_summary_id": _summary_id(manager),
        "executive_dream_ok": dream.get("ok"),
        "decision_option_count": len(dream.get("data", {}).get("decision_options") or []),
        "executive_decision_ok": decision.get("ok") if decision else None,
        "generated_task_ids": task_ids,
        "notification_count": len(result.get("notifications") or []),
        "state": runtime.state_summary(),
    }


def _summary_id(manager_result: dict[str, Any]) -> str | None:
    data = manager_result.get("data", {})
    record = data.get("record") if isinstance(data.get("record"), dict) else {}
    report = record.get("report") if isinstance(record.get("report"), dict) else {}
    return data.get("summary_public_id") or data.get("summary_id") or report.get("summary_public_id") or report.get("summary_id")


if __name__ == "__main__":
    main()
