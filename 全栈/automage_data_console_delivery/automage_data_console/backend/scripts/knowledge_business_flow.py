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
from automage_agents.knowledge.runtime_context import FEISHU_KNOWLEDGE_INPUT_REF_KEY, attach_feishu_knowledge_to_runtime
from automage_agents.skills.common import agent_init
from automage_agents.skills.executive import commit_decision, dream_decision_engine
from automage_agents.skills.manager import generate_manager_report
from automage_agents.skills.staff import post_daily_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Feishu knowledge refs through Staff/Manager/Executive business skills.")
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=2)
    parser.add_argument("--max-context-chars", type=int, default=1500)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    contexts = build_demo_contexts(
        staff_user_path="examples/user.staff.example.toml",
        manager_user_path="examples/user.manager.example.toml",
        executive_user_path="examples/user.executive.example.toml",
    )
    checks: list[dict[str, Any]] = []

    for context in [contexts.staff, contexts.manager, contexts.executive]:
        attach_feishu_knowledge_to_runtime(
            runtime=context.runtime,
            query=args.query,
            limit=args.limit,
            max_context_chars=args.max_context_chars,
        )
        init_result = agent_init(context)
        checks.append({"name": f"agent_init:{context.identity.role.value}", "ok": init_result.ok})

    staff_result = post_daily_report(
        contexts.staff,
        {
            "work_progress": "根据知识库上下文继续推进 OpenAPI 契约联调。",
            "issues_faced": "需要确保日报 payload 能追溯知识库来源。",
            "solution_attempt": "在 meta.knowledge_refs 中保存轻量来源引用。",
            "next_day_plan": "继续验证 Manager 和 Executive 主链路。",
        },
    )
    manager_result = generate_manager_report(
        contexts.manager,
        {
            "dept_id": contexts.manager.identity.department_id or "dept-sales",
            "overall_health": "green",
            "aggregated_summary": "知识库来源引用已进入 Staff 日报和 Manager 汇总 mock 链路。",
            "top_3_risks": ["需要与最终后端 schema 持续对齐"],
            "workforce_efficiency": 0.86,
            "pending_approvals": 0,
            "source_record_ids": [staff_result.data.get("work_record_id")],
        },
    )
    dream_result = dream_decision_engine(
        contexts.executive,
        {
            "stage_goal": "验证知识库来源引用进入 Executive 决策链路",
            "manager_summary": contexts.state.manager_reports[-1]["report"] if contexts.state.manager_reports else {},
            "external_variables": {"query": args.query},
        },
    )
    decision_result = commit_decision(
        contexts.executive,
        {
            "selected_option_id": "A",
            "decision_summary": "确认知识库来源引用进入决策 meta。",
            "task_candidates": [],
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

    staff_refs = _knowledge_refs(contexts.state.staff_reports[-1]["report"])
    manager_refs = _knowledge_refs(contexts.state.manager_reports[-1]["report"])
    dream_refs = dream_result.data.get("knowledge_refs", {})
    decision_refs = decision_result.data["decision"]["decision"].get("meta", {}).get("knowledge_refs", {})
    refs_ok = all(
        FEISHU_KNOWLEDGE_INPUT_REF_KEY in refs
        for refs in [staff_refs, manager_refs, dream_refs, decision_refs]
    )
    output = {
        "ok": all(check["ok"] for check in checks) and refs_ok,
        "checks": checks,
        "refs_ok": refs_ok,
        "knowledge_ref_key": FEISHU_KNOWLEDGE_INPUT_REF_KEY,
        "staff_knowledge_refs": staff_refs,
        "manager_knowledge_refs": manager_refs,
        "dream_knowledge_refs": dream_refs,
        "decision_knowledge_refs": decision_refs,
        "state_counts": {
            "staff_reports": len(contexts.state.staff_reports),
            "manager_reports": len(contexts.state.manager_reports),
            "decision_logs": len(contexts.state.decision_logs),
            "audit_logs": len(contexts.state.audit_logs),
        },
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if not output["ok"]:
        raise SystemExit(1)


def _knowledge_refs(payload: dict[str, Any]) -> dict[str, Any]:
    meta = payload.get("meta", {})
    if not isinstance(meta, dict):
        return {}
    knowledge_refs = meta.get("knowledge_refs", {})
    return knowledge_refs if isinstance(knowledge_refs, dict) else {}


if __name__ == "__main__":
    main()
