from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.config import load_runtime_settings
from automage_agents.db import SummaryModel, create_session_factory
from automage_agents.integrations.hermes import HermesOpenClawRuntime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    args = _parse_args()
    summary_id = args.summary_id or _latest_summary_public_id(args.settings, verify_date=args.date)
    if not summary_id:
        output = {
            "ok": False,
            "blocked": True,
            "mode": "dry_run" if not args.execute else "execute",
            "reason": "No Manager summary was found for the requested date. Run scheduler or pass --summary-id.",
            "date": args.date.isoformat(),
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        raise SystemExit(1)

    if not args.execute:
        output = {
            "ok": True,
            "blocked": False,
            "mode": "dry_run",
            "summary_id": summary_id,
            "would_run": [
                f"生成决策草案 {summary_id}",
                f"确认方案{args.option_id.upper()} {summary_id}",
                "完成任务 <generated_task_id>",
            ],
            "note": "No backend writes are performed without --execute.",
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    result = run_im_decision_task_flow(
        settings_path=args.settings,
        summary_id=summary_id,
        option_id=args.option_id.upper(),
        staff_profile=args.staff_profile,
        manager_profile=args.manager_profile,
        executive_profile=args.executive_profile,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["ok"]:
        raise SystemExit(1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify Feishu-IM-style Dream -> Executive decision -> Task update flow.")
    parser.add_argument("--settings", default="configs/automage.local.toml")
    parser.add_argument("--date", type=_parse_date, default=date.today(), help="Manager summary date used when --summary-id is omitted.")
    parser.add_argument("--summary-id", help="Manager summary public_id, e.g. SUM500E7D2114B9494EB6AD86.")
    parser.add_argument("--option-id", default="B", choices=["A", "B", "a", "b"], help="Dream option to confirm.")
    parser.add_argument("--staff-profile", default="examples/user.staff.local.example.toml")
    parser.add_argument("--manager-profile", default="examples/user.manager.local.example.toml")
    parser.add_argument("--executive-profile", default="examples/user.executive.local.example.toml")
    parser.add_argument("--execute", action="store_true", help="Actually call backend APIs and write decision/task records.")
    return parser.parse_args()


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _latest_summary_public_id(settings_path: str, *, verify_date: date) -> str:
    settings = load_runtime_settings(settings_path)
    SessionLocal = create_session_factory(settings.postgres)
    with SessionLocal() as session:
        row = (
            session.query(SummaryModel)
            .filter(SummaryModel.deleted_at.is_(None), SummaryModel.summary_date == verify_date)
            .order_by(SummaryModel.id.desc())
            .first()
        )
        return row.public_id if row is not None else ""


def run_im_decision_task_flow(
    *,
    settings_path: str,
    summary_id: str,
    option_id: str,
    staff_profile: str,
    manager_profile: str,
    executive_profile: str,
) -> dict[str, Any]:
    runtime = HermesOpenClawRuntime.from_demo_configs(
        settings_path=settings_path,
        staff_user_path=staff_profile,
        manager_user_path=manager_profile,
        executive_user_path=executive_profile,
        user_mapping={"ou_staff_verify": "zhangsan", "ou_exec_verify": "chenzong"},
        auto_initialize=False,
    )
    dream = runtime.handle_feishu_message_receive_v1(_raw_text_event("ou_exec_verify", "om_verify_dream", f"生成决策草案 {summary_id}"))
    if not dream.get("ok"):
        return {"ok": False, "failed_stage": "dream", "summary_id": summary_id, "dream": dream}

    decision = runtime.handle_feishu_message_receive_v1(
        _raw_text_event("ou_exec_verify", "om_verify_decision", f"确认方案{option_id} {summary_id}")
    )
    if not decision.get("ok"):
        return {"ok": False, "failed_stage": "decision", "summary_id": summary_id, "dream": dream, "decision": decision}

    task_ids = decision.get("data", {}).get("task_ids") or decision.get("data", {}).get("generated_task_ids") or []
    if not task_ids:
        return {"ok": False, "failed_stage": "task_generation", "summary_id": summary_id, "dream": dream, "decision": decision}

    task_id = str(task_ids[0])
    task_update = runtime.handle_feishu_message_receive_v1(
        _raw_text_event("ou_staff_verify", "om_verify_task_done", f"完成任务 {task_id}")
    )
    return {
        "ok": bool(dream.get("ok") and decision.get("ok") and task_update.get("ok")),
        "mode": "execute",
        "summary_id": summary_id,
        "option_id": option_id,
        "task_id": task_id,
        "dream": _compact_event_result(dream),
        "decision": _compact_event_result(decision),
        "task_update": _compact_event_result(task_update),
    }


def _raw_text_event(open_id: str, message_id: str, text: str) -> dict[str, Any]:
    return {
        "event": {
            "sender": {"sender_id": {"open_id": open_id}},
            "message": {
                "message_id": message_id,
                "chat_id": "oc_verify_im_flow",
                "chat_type": "p2p",
                "message_type": "text",
                "content": json.dumps({"text": text}, ensure_ascii=False),
            },
        }
    }


def _compact_event_result(result: dict[str, Any]) -> dict[str, Any]:
    data = result.get("data", {}) if isinstance(result.get("data"), dict) else {}
    return {
        "ok": result.get("ok"),
        "event_type": result.get("event_type"),
        "actor_user_id": result.get("actor_user_id"),
        "message": result.get("message"),
        "error_code": result.get("error_code"),
        "summary_public_id": data.get("summary_public_id"),
        "task_ids": data.get("task_ids") or data.get("generated_task_ids"),
        "reply_body": result.get("reply", {}).get("body") if isinstance(result.get("reply"), dict) else None,
    }


if __name__ == "__main__":
    main()
