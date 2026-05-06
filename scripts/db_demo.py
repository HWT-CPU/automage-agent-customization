from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.config import load_runtime_settings
from automage_agents.demo.factory import build_demo_contexts
from automage_agents.skills.common import agent_init
from automage_agents.skills.executive import commit_decision, dream_decision_engine
from automage_agents.skills.manager import generate_manager_report
from automage_agents.skills.staff import fetch_my_tasks, post_daily_report

def main() -> None:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "configs/automage.local.toml"
    settings = load_runtime_settings(config_path)
    contexts = build_demo_contexts(
        staff_user_path="examples/user.staff.example.toml",
        manager_user_path="examples/user.manager.example.toml",
        executive_user_path="examples/user.executive.example.toml",
        settings_path=config_path,
    )
    staff = contexts.staff
    manager = contexts.manager
    executive = contexts.executive

    output: dict[str, Any] = {"steps": []}
    output["backend_mode"] = settings.backend_mode

    for context in [staff, manager, executive]:
        result = agent_init(context)
        output["steps"].append({"step": f"agent_init:{context.identity.role.value}", "ok": result.ok, "message": result.message})

    staff_result = post_daily_report(
        staff,
        {
            "timestamp": "2026-05-06T09:30:00+08:00",
            "work_progress": "Completed daily customer follow-up and prepared two proposals.",
            "issues_faced": "Need a clearer delivery timeline for one enterprise customer.",
            "solution_attempt": "Collected timeline constraints and escalated to the manager.",
            "need_support": True,
            "next_day_plan": "Continue proposal follow-up and close delivery timeline questions.",
            "resource_usage": {"customer_calls": 8, "quotes_prepared": 2},
        },
    )
    output["steps"].append({"step": "post_staff_report", "ok": staff_result.ok, "message": staff_result.message})

    manager_result = generate_manager_report(
        manager,
        {
            "dept_id": "dept-sales",
            "overall_health": "yellow",
            "aggregated_summary": "Sales progress is stable but delivery clarification needs coordination.",
            "top_3_risks": ["Delivery timeline ambiguity", "Proposal bandwidth", "Slow decision cycles"],
            "workforce_efficiency": 0.83,
            "pending_approvals": 1,
        },
    )
    output["steps"].append({"step": "post_manager_report", "ok": manager_result.ok, "message": manager_result.message})

    draft = dream_decision_engine(
        executive,
        {
            "stage_goal": "Increase key account conversion while reducing delivery risk.",
            "manager_summary": {"department": "sales"},
            "external_variables": {"quarter": "Q2", "risk_tolerance": "medium"},
        },
    )
    output["steps"].append({"step": "dream_decision", "ok": draft.ok, "message": draft.message})

    decision_result = commit_decision(
        executive,
        {
            "selected_option_id": "A",
            "decision_summary": "Prioritize delivery clarification before pushing new commitments.",
            "task_candidates": [
                {
                    "assignee_user_id": staff.identity.user_id,
                    "title": "Prepare delivery FAQ for key accounts",
                    "description": "Summarize delivery constraints and communicate them in follow-up calls.",
                }
            ],
        },
    )
    output["steps"].append({"step": "commit_decision", "ok": decision_result.ok, "message": decision_result.message})

    tasks_result = fetch_my_tasks(staff, status="pending")
    output["steps"].append({"step": "fetch_tasks", "ok": tasks_result.ok, "message": tasks_result.message, "data": tasks_result.data})

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
