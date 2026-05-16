from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.demo.factory import build_demo_contexts
from automage_agents.integrations.feishu.events import FeishuEvent, FeishuEventAdapter
from automage_agents.integrations.feishu.messages import FeishuMessageAdapter
from automage_agents.integrations.openclaw.adapter import OpenClawAdapter
from automage_agents.integrations.router import InternalEventRouter
from automage_agents.skills.common import agent_init
from automage_agents.skills.manager import analyze_team_reports, generate_manager_report


def main() -> None:
    contexts = build_demo_contexts(
        staff_user_path="examples/user.staff.example.toml",
        manager_user_path="examples/user.manager.example.toml",
        executive_user_path="examples/user.executive.example.toml",
    )
    router = InternalEventRouter(contexts.staff, contexts.manager, contexts.executive)
    openclaw = OpenClawAdapter(router)
    feishu_events = FeishuEventAdapter(user_mapping={"staff-open-id": "user-001"})
    feishu_messages = FeishuMessageAdapter()

    output: dict[str, Any] = {"steps": []}

    for context in [contexts.staff, contexts.manager, contexts.executive]:
        result = agent_init(context)
        output["steps"].append({"step": f"agent_init:{context.identity.role.value}", "ok": result.ok, "message": result.message})

    daily_card = feishu_messages.build_daily_report_card(contexts.staff.identity.user_id)
    output["steps"].append({"step": "send_daily_report_card", "result": feishu_messages.send_message(daily_card)})

    staff_event = FeishuEvent(
        event_type="daily_report_submit",
        open_id="staff-open-id",
        message_id="msg-001",
        payload={
            "timestamp": "2026-05-02T18:30:00+08:00",
            "work_progress": "完成 12 个客户线索跟进，推进 3 个重点客户进入报价阶段。",
            "issues_faced": "两个客户需要更明确的交付周期说明。",
            "solution_attempt": "已整理交付周期问题并同步给部门经理。",
            "need_support": True,
            "next_day_plan": "继续跟进重点客户报价，并补充交付周期说明。",
            "resource_usage": {"customer_calls": 12, "quotes_prepared": 3},
        },
    )
    staff_result = openclaw.handle_event(feishu_events.to_internal_event(staff_event))
    output["steps"].append({"step": "staff_daily_report_submitted", "ok": staff_result.ok, "message": staff_result.message})

    team_reports_result = analyze_team_reports(contexts.manager, date="2026-05-02")
    team_report_count = len(team_reports_result.data.get("items", []))
    output["steps"].append(
        {
            "step": "manager_fetch_team_reports",
            "ok": team_reports_result.ok,
            "message": team_reports_result.message,
            "report_count": team_report_count,
        }
    )

    manager_result = generate_manager_report(
        contexts.manager,
        {
            "dept_id": "dept-sales",
            "overall_health": "yellow",
            "aggregated_summary": "销售部门整体推进正常，但重点客户交付周期解释需要跨部门支持。",
            "top_3_risks": ["交付周期不清晰", "报价资源不足", "重点客户等待时间过长"],
            "workforce_efficiency": 0.82,
            "pending_approvals": 1,
        },
    )
    output["steps"].append({"step": "manager_report_generated", "ok": manager_result.ok, "message": manager_result.message})

    dream_result = router.run_dream_decision(
        {
            "stage_goal": "提高重点客户转化率并降低交付不确定性",
            "manager_summary": contexts.state.manager_reports[-1]["report"],
            "external_variables": {"quarter": "Q2", "risk_tolerance": "medium"},
        }
    )
    output["steps"].append({"step": "executive_dream_decision", "ok": dream_result.ok, "message": dream_result.message})

    decision_card = feishu_messages.build_decision_card(
        target_user_id=contexts.executive.identity.user_id,
        decision_options=dream_result.data["decision_options"],
    )
    output["steps"].append({"step": "send_executive_decision_card", "result": feishu_messages.send_message(decision_card)})

    executive_event = FeishuEvent(
        event_type="executive_decision",
        open_id="executive-open-id",
        message_id="msg-002",
        payload={
            "selected_option_id": "A",
            "decision_summary": "优先补齐交付周期说明，稳妥推进重点客户报价。",
            "task_candidates": [
                {
                    "assignee_user_id": "user-001",
                    "title": "补充重点客户交付周期说明",
                    "description": "整理交付周期 FAQ，并在明日客户跟进中使用。",
                }
            ],
        },
    )
    decision_result = openclaw.handle_event(feishu_events.to_internal_event(executive_event))
    output["steps"].append({"step": "executive_decision_committed", "ok": decision_result.ok, "message": decision_result.message})

    task_query_event = FeishuEvent(event_type="task_query", open_id="staff-open-id", message_id="msg-003", payload={})
    task_result = openclaw.handle_event(feishu_events.to_internal_event(task_query_event))
    output["steps"].append({"step": "staff_fetch_tasks", "ok": task_result.ok, "message": task_result.message, "data": task_result.data})

    output["state"] = {
        "agent_sessions": len(contexts.state.agent_sessions),
        "staff_reports": len(contexts.state.staff_reports),
        "form_templates": len(contexts.state.form_templates),
        "work_records": len(contexts.state.work_records),
        "work_record_items": len(contexts.state.work_record_items),
        "manager_reports": len(contexts.state.manager_reports),
        "agent_decision_logs": len(contexts.state.agent_decision_logs),
        "decision_logs": len(contexts.state.decision_logs),
        "task_queue": len(contexts.state.task_queue),
        "audit_logs": len(contexts.state.audit_logs),
        "runtime_contexts": [item["context"] for item in contexts.state.initialized_agents],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
