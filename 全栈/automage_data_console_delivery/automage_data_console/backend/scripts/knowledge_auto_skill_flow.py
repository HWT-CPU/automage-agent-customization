from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.demo.factory import build_demo_contexts
from automage_agents.knowledge.runtime_context import FEISHU_KNOWLEDGE_INPUT_REF_KEY
from automage_agents.skills.common import agent_init
from automage_agents.skills.executive import commit_decision, dream_decision_engine
from automage_agents.skills.manager import generate_manager_report
from automage_agents.skills.staff import post_daily_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate automatic Feishu knowledge retrieval and skill payload enrichment.")
    parser.add_argument("query", nargs="?", default="OpenAPI 契约")
    args = parser.parse_args()

    contexts = build_demo_contexts(
        staff_user_path="examples/user.staff.example.toml",
        manager_user_path="examples/user.manager.example.toml",
        executive_user_path="examples/user.executive.example.toml",
    )
    checks: list[dict[str, Any]] = []

    for context in [contexts.staff, contexts.manager, contexts.executive]:
        init_result = agent_init(context)
        checks.append({"name": f"agent_init:{context.identity.role.value}", "ok": init_result.ok})

    staff_result = post_daily_report(
        contexts.staff,
        {
            "work_progress": f"围绕 {args.query} 继续推进接口联调和日报契约验证。",
            "issues_faced": "需要让知识库上下文进入 Skill 参数，而不只是保存引用。",
            "solution_attempt": "通过自动检索和 payload enrichment 补充上下文字段。",
            "next_day_plan": "验证 Manager 汇总和 Executive 决策参数补全。",
        },
    )
    manager_result = generate_manager_report(
        contexts.manager,
        {
            "dept_id": contexts.manager.identity.department_id or "dept-sales",
            "overall_health": "green",
            "aggregated_summary": f"团队正在基于 {args.query} 校准业务 Skill 参数生成。",
            "top_3_risks": ["自动检索结果需要在最终后端契约中保持可追溯"],
            "workforce_efficiency": 0.88,
            "pending_approvals": 0,
            "source_record_ids": [staff_result.data.get("work_record_id")],
        },
    )
    dream_result = dream_decision_engine(
        contexts.executive,
        {
            "stage_goal": f"基于 {args.query} 验证 Prompt 到 Skill 参数闭环",
            "manager_summary": contexts.state.manager_reports[-1]["report"] if contexts.state.manager_reports else {},
            "external_variables": {"requested_query": args.query},
        },
    )
    decision_result = commit_decision(
        contexts.executive,
        {
            "selected_option_id": "A",
            "decision_summary": f"确认基于 {args.query} 的自动知识检索和参数补全链路。",
            "task_candidates": [
                {
                    "assignee_user_id": contexts.staff.identity.user_id,
                    "title": "验证知识库驱动的 Skill 参数补全",
                    "description": "检查 Staff artifact、Manager adjustment、Dream external_variables 和 task meta。",
                }
            ],
        },
    )

    checks.extend(
        [
            {"name": "post_daily_report", "ok": staff_result.ok},
            {"name": "generate_manager_report", "ok": manager_result.ok},
            {"name": "dream_decision_engine", "ok": dream_result.ok},
            {"name": "commit_decision", "ok": decision_result.ok},
        ]
    )

    staff_report = contexts.state.staff_reports[-1]["report"]
    manager_report = contexts.state.manager_reports[-1]["report"]
    decision_payload = decision_result.data["decision"]["decision"]
    generated_task = decision_result.data["task_queue"][-1]
    auto_runtime_ok = all(
        FEISHU_KNOWLEDGE_INPUT_REF_KEY in context.runtime.input_refs
        for context in [contexts.staff, contexts.manager, contexts.executive]
    )
    enrichment_ok = all(
        [
            _staff_has_knowledge_artifact(staff_report),
            _manager_has_knowledge_adjustment(manager_report),
            FEISHU_KNOWLEDGE_INPUT_REF_KEY in dream_result.data["input"].get("external_variables", {}).get("knowledge_refs", {}),
            FEISHU_KNOWLEDGE_INPUT_REF_KEY in decision_payload.get("meta", {}).get("knowledge_refs", {}),
            FEISHU_KNOWLEDGE_INPUT_REF_KEY in generated_task.get("meta", {}).get("knowledge_refs", {}),
        ]
    )
    output = {
        "ok": all(check["ok"] for check in checks) and auto_runtime_ok and enrichment_ok,
        "checks": checks,
        "auto_runtime_ok": auto_runtime_ok,
        "enrichment_ok": enrichment_ok,
        "staff_artifacts": staff_report.get("artifacts", []),
        "manager_next_day_adjustment": manager_report.get("next_day_adjustment", []),
        "dream_external_variables": dream_result.data["input"].get("external_variables", {}),
        "decision_meta": decision_payload.get("meta", {}),
        "generated_task_meta": generated_task.get("meta", {}),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if not output["ok"]:
        raise SystemExit(1)


def _staff_has_knowledge_artifact(report: dict[str, Any]) -> bool:
    for artifact in report.get("artifacts", []):
        if not isinstance(artifact, dict):
            continue
        meta = artifact.get("meta", {})
        if isinstance(meta, dict) and meta.get("knowledge_ref_key") == FEISHU_KNOWLEDGE_INPUT_REF_KEY:
            return True
    return False


def _manager_has_knowledge_adjustment(report: dict[str, Any]) -> bool:
    return any(
        isinstance(item, dict) and item.get("title") == "按知识库资料校准执行口径"
        for item in report.get("next_day_adjustment", [])
    )


if __name__ == "__main__":
    main()
