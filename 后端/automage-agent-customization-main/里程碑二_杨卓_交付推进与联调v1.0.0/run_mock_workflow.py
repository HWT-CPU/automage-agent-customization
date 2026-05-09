#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoMage-2 MVP 里程碑二本地 Mock 闭环验证脚本。

目标：验证 Staff → Manager → Executive → Task → 下一轮 Staff 回流是否能在本地 Mock 数据下跑通。
本脚本默认不连接真实数据库、不写真实数据库，只读取本目录下的 mock_*.json 文件。

推荐放置文件：
- schema_v1_staff.json
- schema_v1_manager.json
- schema_v1_executive.json
- schema_v1_task.json
- mock_staff_report_normal.json
- mock_staff_report_high_risk.json
- mock_manager_summary_normal.json
- mock_manager_summary_need_executive.json
- mock_executive_decision_card_ab_options.json
- mock_generated_tasks.json
- mock_full_workflow_run.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


BASE_DIR = Path(__file__).resolve().parent

MOCK_FILES = {
    "staff_normal": "mock_staff_report_normal.json",
    "staff_high_risk": "mock_staff_report_high_risk.json",
    "manager_normal": "mock_manager_summary_normal.json",
    "manager_need_executive": "mock_manager_summary_need_executive.json",
    "executive_decision": "mock_executive_decision_card_ab_options.json",
    "generated_tasks": "mock_generated_tasks.json",
    "full_workflow_run": "mock_full_workflow_run.json",
}

SCHEMA_FILES = {
    "staff": "schema_v1_staff.json",
    "manager": "schema_v1_manager.json",
    "executive": "schema_v1_executive.json",
    "task": "schema_v1_task.json",
}


@dataclass
class StepResult:
    step_id: str
    step_name: str
    status: str
    input_files: List[str]
    output_schema: str
    api_endpoint: str
    read_tables: List[str]
    write_tables: List[str]
    notes: str


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"缺少文件：{path.name}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_schema_file(name: str) -> Optional[Path]:
    candidates = [BASE_DIR / name, Path.cwd() / name, Path("/mnt/data") / name]
    for p in candidates:
        if p.exists():
            return p
    return None


def validate_with_jsonschema(instance: Any, schema_name: str, label: str) -> Tuple[bool, str]:
    schema_path = find_schema_file(schema_name)
    if schema_path is None:
        return True, f"跳过严格校验：未找到 {schema_name}，仅执行最小字段校验。"
    try:
        import jsonschema  # type: ignore
    except Exception:
        return True, "跳过严格校验：未安装 jsonschema，已执行最小字段校验。"

    schema = load_json(schema_path)
    try:
        jsonschema.Draft202012Validator(schema).validate(instance)
        return True, f"{label} 通过 {schema_name} 校验。"
    except Exception as exc:
        return False, f"{label} 未通过 {schema_name} 校验：{exc}"


def require_fields(obj: Dict[str, Any], fields: List[str], label: str) -> None:
    missing = [f for f in fields if f not in obj]
    if missing:
        raise ValueError(f"{label} 缺少必填字段：{', '.join(missing)}")


def validate_staff(report: Dict[str, Any], label: str) -> str:
    require_fields(
        report,
        ["schema_id", "schema_version", "timestamp", "org_id", "department_id", "user_id", "node_id", "record_date", "work_progress", "need_support", "next_day_plan", "risk_level", "signature"],
        label,
    )
    if report["schema_id"] != "schema_v1_staff":
        raise ValueError(f"{label} schema_id 错误：{report['schema_id']}")
    ok, msg = validate_with_jsonschema(report, SCHEMA_FILES["staff"], label)
    if not ok:
        raise ValueError(msg)
    return msg


def validate_manager(summary: Dict[str, Any], label: str) -> str:
    require_fields(
        summary,
        ["schema_id", "schema_version", "timestamp", "org_id", "dept_id", "manager_user_id", "manager_node_id", "summary_date", "staff_report_count", "missing_report_count", "overall_health", "aggregated_summary", "top_3_risks", "pending_approvals", "source_record_ids", "signature"],
        label,
    )
    if summary["schema_id"] != "schema_v1_manager":
        raise ValueError(f"{label} schema_id 错误：{summary['schema_id']}")
    ok, msg = validate_with_jsonschema(summary, SCHEMA_FILES["manager"], label)
    if not ok:
        raise ValueError(msg)
    return msg


def validate_executive(decision: Dict[str, Any], label: str) -> str:
    require_fields(
        decision,
        ["schema_id", "schema_version", "timestamp", "org_id", "executive_user_id", "executive_node_id", "summary_date", "business_summary", "key_risks", "decision_required", "source_summary_ids", "human_confirm_status"],
        label,
    )
    if decision["schema_id"] != "schema_v1_executive":
        raise ValueError(f"{label} schema_id 错误：{decision['schema_id']}")
    ok, msg = validate_with_jsonschema(decision, SCHEMA_FILES["executive"], label)
    if not ok:
        raise ValueError(msg)
    return msg


def validate_task(task: Dict[str, Any], label: str) -> str:
    require_fields(
        task,
        ["schema_id", "schema_version", "org_id", "task_title", "task_description", "source_type", "source_id", "creator_user_id", "created_by_node_id", "priority", "status", "confirm_required"],
        label,
    )
    if task["schema_id"] != "schema_v1_task":
        raise ValueError(f"{label} schema_id 错误：{task['schema_id']}")
    ok, msg = validate_with_jsonschema(task, SCHEMA_FILES["task"], label)
    if not ok:
        raise ValueError(msg)
    return msg


def build_runtime_result(data: Dict[str, Any], validation_messages: List[str]) -> Dict[str, Any]:
    staff_reports = [data["staff_normal"], data["staff_high_risk"]]
    manager_need_exec = data["manager_need_executive"]
    executive_decision = data["executive_decision"]
    tasks = data["generated_tasks"]["tasks"]

    any_high_risk = any(r.get("risk_level") in {"high", "critical"} for r in staff_reports)
    needs_exec = manager_need_exec.get("pending_approvals", 0) > 0 and bool(manager_need_exec.get("need_executive_decision"))
    has_tasks = len(tasks) > 0

    steps = [
        StepResult(
            step_id="S1",
            step_name="Staff 日报提交",
            status="passed" if len(staff_reports) >= 2 else "failed",
            input_files=[MOCK_FILES["staff_normal"], MOCK_FILES["staff_high_risk"]],
            output_schema="schema_v1_staff[]",
            api_endpoint="POST /api/v1/report/staff",
            read_tables=[],
            write_tables=["staff_reports", "work_records", "work_record_items", "artifacts", "incidents", "audit_logs"],
            notes="正常日报与高风险日报均为标准 JSON；高风险问题可转换为 incidents。",
        ),
        StepResult(
            step_id="M1",
            step_name="Manager 汇总与上推判断",
            status="passed" if needs_exec else "failed",
            input_files=[MOCK_FILES["manager_normal"], MOCK_FILES["manager_need_executive"]],
            output_schema="schema_v1_manager[]",
            api_endpoint="POST /api/v1/report/manager",
            read_tables=["staff_reports", "work_records", "work_record_items", "incidents", "tasks"],
            write_tables=["manager_reports", "summaries", "summary_source_links", "incidents", "audit_logs"],
            notes="Manager 可区分 normal 与 need_executive 两种汇总；高风险 API/Skill 问题被上推。",
        ),
        StepResult(
            step_id="X1",
            step_name="Executive / Dream 生成老板决策卡片",
            status="passed" if executive_decision.get("decision_required") else "failed",
            input_files=[MOCK_FILES["executive_decision"]],
            output_schema="schema_v1_executive",
            api_endpoint="POST /api/v1/decision/commit",
            read_tables=["manager_reports", "summaries", "summary_source_links", "incidents"],
            write_tables=["decision_records", "decision_logs", "agent_decision_logs", "audit_logs"],
            notes=f"推荐方案：{executive_decision.get('recommended_option')}；确认状态：{executive_decision.get('human_confirm_status')}。",
        ),
        StepResult(
            step_id="T1",
            step_name="老板确认后任务生成",
            status="passed" if has_tasks else "failed",
            input_files=[MOCK_FILES["generated_tasks"]],
            output_schema="schema_v1_task[]",
            api_endpoint="POST /api/v1/tasks",
            read_tables=["decision_records", "decision_logs"],
            write_tables=["task_queue", "tasks", "task_assignments", "task_updates", "audit_logs"],
            notes=f"生成任务数量：{len(tasks)}。",
        ),
        StepResult(
            step_id="S2",
            step_name="任务结果进入下一轮 Staff 日报样例",
            status="passed" if data["full_workflow_run"].get("next_round_staff_report_seed") else "failed",
            input_files=[MOCK_FILES["full_workflow_run"]],
            output_schema="schema_v1_staff.task_progress seed",
            api_endpoint="GET /api/v1/tasks -> POST /api/v1/report/staff",
            read_tables=["tasks", "task_assignments", "task_updates"],
            write_tables=["staff_reports", "work_records", "work_record_items", "artifacts", "audit_logs"],
            notes="mock_full_workflow_run.json 已包含 next_round_staff_report_seed。",
        ),
    ]

    passed = all(s.status == "passed" for s in steps)
    return {
        "schema_id": "mock_v1_workflow_runtime_result",
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dag_run_id": data["full_workflow_run"].get("dag_run_id"),
        "org_id": data["full_workflow_run"].get("org_id"),
        "run_date": data["full_workflow_run"].get("run_date"),
        "overall_status": "passed" if passed else "failed",
        "checks": {
            "staff_reports_count": len(staff_reports),
            "has_high_risk_report": any_high_risk,
            "manager_needs_executive": needs_exec,
            "executive_decision_required": executive_decision.get("decision_required"),
            "generated_tasks_count": len(tasks),
            "next_round_seed_present": bool(data["full_workflow_run"].get("next_round_staff_report_seed")),
        },
        "validation_messages": validation_messages,
        "steps": [asdict(s) for s in steps],
        "generated_task_ids": [t.get("task_id") for t in tasks],
        "next_round_staff_report_seed": data["full_workflow_run"].get("next_round_staff_report_seed"),
    }


def run(write_output: bool = True, output_dir: Optional[Path] = None) -> Dict[str, Any]:
    data = {key: load_json(BASE_DIR / filename) for key, filename in MOCK_FILES.items()}

    validation_messages: List[str] = []
    validation_messages.append(validate_staff(data["staff_normal"], "mock_staff_report_normal.json"))
    validation_messages.append(validate_staff(data["staff_high_risk"], "mock_staff_report_high_risk.json"))
    validation_messages.append(validate_manager(data["manager_normal"], "mock_manager_summary_normal.json"))
    validation_messages.append(validate_manager(data["manager_need_executive"], "mock_manager_summary_need_executive.json"))
    validation_messages.append(validate_executive(data["executive_decision"], "mock_executive_decision_card_ab_options.json"))

    generated_tasks = data["generated_tasks"]
    require_fields(generated_tasks, ["schema_id", "schema_version", "generated_at", "org_id", "tasks"], "mock_generated_tasks.json")
    for idx, task in enumerate(generated_tasks["tasks"], 1):
        validation_messages.append(validate_task(task, f"mock_generated_tasks.json/tasks[{idx}]"))

    require_fields(data["full_workflow_run"], ["schema_id", "schema_version", "dag_run_id", "org_id", "run_date", "steps", "next_round_staff_report_seed"], "mock_full_workflow_run.json")

    result = build_runtime_result(data, validation_messages)
    if write_output:
        out_dir = output_dir or (BASE_DIR / "mock_runtime_output")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "mock_workflow_runtime_result.json"
        out_file.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result["output_file"] = str(out_file)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AutoMage-2 M2 local mock workflow validation.")
    parser.add_argument("--no-write", action="store_true", help="只校验并打印结果，不写入 mock_runtime_output。")
    parser.add_argument("--output-dir", type=str, default=None, help="运行结果输出目录。")
    args = parser.parse_args()

    try:
        result = run(write_output=not args.no_write, output_dir=Path(args.output_dir) if args.output_dir else None)
    except Exception as exc:
        print(json.dumps({"overall_status": "failed", "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    print(json.dumps({
        "overall_status": result["overall_status"],
        "dag_run_id": result.get("dag_run_id"),
        "checks": result.get("checks"),
        "generated_task_ids": result.get("generated_task_ids"),
        "output_file": result.get("output_file"),
    }, ensure_ascii=False, indent=2))
    return 0 if result["overall_status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
