from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.demo.factory import build_demo_contexts
from automage_agents.skills.common import agent_init
from automage_agents.skills.executive import commit_decision
from automage_agents.skills.manager import generate_manager_report
from automage_agents.skills.staff import fetch_my_tasks, import_staff_daily_report_from_markdown, post_daily_report, read_staff_daily_report


def main() -> None:
    contexts = build_demo_contexts(
        staff_user_path="examples/user.staff.example.toml",
        manager_user_path="examples/user.manager.example.toml",
        executive_user_path="examples/user.executive.example.toml",
    )

    checks: list[dict[str, Any]] = []

    for context in [contexts.staff, contexts.manager, contexts.executive]:
        result = agent_init(context)
        checks.append({"name": f"agent_init:{context.identity.role.value}", "ok": result.ok, "message": result.message})

    snapshot_result = post_daily_report(
        contexts.staff,
        {
            "work_progress": "完成数据库 Skill mock 快照链路验证。",
            "issues_faced": "真实后端模块暂未出现在当前仓库。",
            "solution_attempt": "先使用 Agent 侧 mock 表映射验证交付链路。",
            "next_day_plan": "等后端 FastAPI/SQLAlchemy 模块就绪后接真实库。",
        },
    )
    checks.append({"name": "post_staff_report_snapshot", "ok": snapshot_result.ok, "data": snapshot_result.data})

    formal_result = import_staff_daily_report_from_markdown(
        contexts.staff,
        {
            "markdown": "# AutoMage Staff 日报\n\n今日完成 database-api-skill mock 验证。",
            "report_date": "2026-05-06",
            "items": [
                {"field_key": "summary", "field_value": "database-api-skill mock 验证通过"},
                {"field_key": "risk", "field_value": "缺少真实 server/db 模块，暂不能测真实 PostgreSQL"},
            ],
        },
    )
    checks.append({"name": "import_staff_daily_report_from_markdown", "ok": formal_result.ok, "data": formal_result.data})

    work_record_id = formal_result.data["work_record_id"]
    read_json_result = read_staff_daily_report(contexts.staff, work_record_id, "json")
    read_markdown_result = read_staff_daily_report(contexts.staff, work_record_id, "markdown")
    checks.append({"name": "read_staff_daily_report_json", "ok": read_json_result.ok, "data": read_json_result.data})
    checks.append({"name": "read_staff_daily_report_markdown", "ok": read_markdown_result.ok, "data": read_markdown_result.data})

    manager_result = generate_manager_report(
        contexts.manager,
        {
            "dept_id": "dept-sales",
            "overall_health": "green",
            "aggregated_summary": "database-api-skill mock 表映射正常。",
            "source_record_ids": [snapshot_result.data["work_record_id"], work_record_id],
        },
    )
    checks.append({"name": "post_manager_report", "ok": manager_result.ok, "data": manager_result.data})

    decision_result = commit_decision(
        contexts.executive,
        {
            "selected_option_id": "A",
            "decision_summary": "确认继续使用 mock 链路验证，等待真实后端。",
            "task_candidates": [
                {
                    "assignee_user_id": contexts.staff.identity.user_id,
                    "title": "准备真实后端数据库 Skill 联调清单",
                    "description": "确认 FastAPI 服务地址、PostgreSQL 连接和迁移状态。",
                }
            ],
        },
    )
    checks.append({"name": "commit_decision_and_generate_task", "ok": decision_result.ok, "data": decision_result.data})

    tasks_result = fetch_my_tasks(contexts.staff)
    checks.append({"name": "fetch_tasks", "ok": tasks_result.ok, "data": tasks_result.data})

    expected_counts = {
        "agent_sessions": 3,
        "staff_reports": 1,
        "form_templates": 1,
        "work_records": 1,
        "work_record_items": 2,
        "manager_reports": 1,
        "agent_decision_logs": 1,
        "task_queue": 1,
        "audit_logs": 7,
    }
    actual_counts = {name: len(getattr(contexts.state, name)) for name in expected_counts}
    table_counts_ok = actual_counts == expected_counts
    all_steps_ok = all(check["ok"] for check in checks)

    output = {
        "ok": all_steps_ok and table_counts_ok,
        "scope": "database-api-skill agent-side mock validation",
        "real_database_tested": False,
        "reason_real_database_not_tested": "Current repository does not contain FastAPI server/db/SQLAlchemy client modules required by the delivery docs.",
        "checks": checks,
        "expected_counts": expected_counts,
        "actual_counts": actual_counts,
        "table_counts_ok": table_counts_ok,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if not output["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
