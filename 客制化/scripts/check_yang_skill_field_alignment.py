from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

YANG_MOCK_DIR = PROJECT_ROOT / "里程碑二_杨卓_交付推进与联调v1.0.0"
REPORT_PATH = PROJECT_ROOT / "references" / "yang_mock_skill_field_alignment.md"

from automage_agents.demo.factory import build_demo_contexts
from automage_agents.schemas.executive_v1 import coerce_task_v1_payload
from automage_agents.schemas.manager_v1 import coerce_manager_report_v1_payload
from automage_agents.schemas.staff_v1 import coerce_staff_report_v1_payload
from automage_agents.skills.common import agent_init
from automage_agents.skills.executive import commit_decision, dream_decision_engine
from automage_agents.skills.manager import generate_manager_report
from automage_agents.skills.staff import post_daily_report


def main() -> None:
    args = _parse_args()
    output = run_alignment_check(write_report=not args.no_write_report)
    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(_summary(output), ensure_ascii=False, indent=2))
    if args.strict and not output["strict_ok"]:
        raise SystemExit(1)
    if not output["ok"]:
        raise SystemExit(1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare Yang Zhuo standard mock fields with current AutoMage Skill outputs.")
    parser.add_argument("--json", action="store_true", help="Print full JSON result instead of summary.")
    parser.add_argument("--strict", action="store_true", help="Fail on documented placeholder/drift gaps as well.")
    parser.add_argument("--no-write-report", action="store_true", help="Do not update the markdown report file.")
    return parser.parse_args()


def run_alignment_check(*, write_report: bool = True) -> dict[str, Any]:
    contexts = build_demo_contexts(
        staff_user_path="examples/user.staff.example.toml",
        manager_user_path="examples/user.manager.example.toml",
        executive_user_path="examples/user.executive.example.toml",
    )
    for context in [contexts.staff, contexts.manager, contexts.executive]:
        agent_init(context)

    yang = _load_yang_payloads()
    adapter_outputs = {
        "staff_normal_adapter": coerce_staff_report_v1_payload(yang["staff_normal"], contexts.staff.identity, contexts.staff.runtime_payload()),
        "staff_high_risk_adapter": coerce_staff_report_v1_payload(yang["staff_high_risk"], contexts.staff.identity, contexts.staff.runtime_payload()),
        "manager_normal_adapter": coerce_manager_report_v1_payload(yang["manager_normal"], contexts.manager.identity, contexts.manager.runtime_payload()),
        "manager_need_executive_adapter": coerce_manager_report_v1_payload(yang["manager_need_executive"], contexts.manager.identity, contexts.manager.runtime_payload()),
    }
    skill_outputs = _run_current_skills(contexts, yang)

    comparisons = [
        _compare_fields("staff_normal", yang["staff_normal"], adapter_outputs["staff_normal_adapter"], required=True),
        _compare_fields("staff_high_risk", yang["staff_high_risk"], adapter_outputs["staff_high_risk_adapter"], required=True),
        _compare_fields("manager_normal", yang["manager_normal"], adapter_outputs["manager_normal_adapter"], required=True),
        _compare_fields("manager_need_executive", yang["manager_need_executive"], adapter_outputs["manager_need_executive_adapter"], required=True),
        _compare_fields("staff_skill_output_vs_yang_normal", yang["staff_normal"], skill_outputs["staff_report"], required=False),
        _compare_fields("manager_skill_output_vs_yang_need_executive", yang["manager_need_executive"], skill_outputs["manager_report"], required=False),
        _compare_fields("executive_dream_output_vs_yang_card", yang["executive_decision"], skill_outputs["dream_decision"], required=False),
        _compare_fields("generated_task_vs_yang_task", yang["generated_tasks"]["tasks"][0], skill_outputs["generated_task"], required=False),
    ]

    known_drifts = _known_drifts(comparisons)
    blocking_failures = [comparison for comparison in comparisons if comparison["required"] and comparison["missing_in_actual"]]
    output = {
        "ok": not blocking_failures,
        "strict_ok": not blocking_failures and not known_drifts,
        "scope": "yang-mock-to-current-skill-field-alignment",
        "yang_mock_dir": str(YANG_MOCK_DIR),
        "report_path": str(REPORT_PATH),
        "comparisons": comparisons,
        "known_drifts": known_drifts,
        "blocking_failures": blocking_failures,
        "recommendations": _recommendations(known_drifts),
    }
    if write_report:
        REPORT_PATH.write_text(_render_report(output), encoding="utf-8")
    return output


def _load_yang_payloads() -> dict[str, Any]:
    return {
        "staff_normal": _load_json("mock_staff_report_normal.json"),
        "staff_high_risk": _load_json("mock_staff_report_high_risk.json"),
        "manager_normal": _load_json("mock_manager_summary_normal.json"),
        "manager_need_executive": _load_json("mock_manager_summary_need_executive.json"),
        "executive_decision": _load_json("mock_executive_decision_card_ab_options.json"),
        "generated_tasks": _load_json("mock_generated_tasks.json"),
    }


def _run_current_skills(contexts: Any, yang: dict[str, Any]) -> dict[str, Any]:
    staff_result = post_daily_report(contexts.staff, yang["staff_normal"])
    manager_result = generate_manager_report(contexts.manager, yang["manager_need_executive"])
    dream_result = dream_decision_engine(contexts.executive, yang["executive_decision"])
    task_candidates = [
        coerce_task_v1_payload(task, contexts.executive.identity, contexts.executive.runtime_payload())
        for task in yang["generated_tasks"].get("tasks", [])
    ]
    decision_result = commit_decision(
        contexts.executive,
        {
            "selected_option_id": yang["executive_decision"].get("confirmed_option") or yang["executive_decision"].get("recommended_option"),
            "decision_summary": yang["executive_decision"].get("reasoning_summary") or yang["executive_decision"].get("business_summary"),
            "source_summary_ids": yang["executive_decision"].get("source_summary_ids", []),
            "source_incident_ids": yang["executive_decision"].get("source_incident_ids", []),
            "task_candidates": task_candidates,
        },
    )
    if not all([staff_result.ok, manager_result.ok, dream_result.ok, decision_result.ok]):
        raise RuntimeError(
            json.dumps(
                {
                    "staff_ok": staff_result.ok,
                    "manager_ok": manager_result.ok,
                    "dream_ok": dream_result.ok,
                    "decision_ok": decision_result.ok,
                },
                ensure_ascii=False,
            )
        )
    return {
        "staff_report": contexts.state.staff_reports[-1]["report"],
        "manager_report": contexts.state.manager_reports[-1]["report"],
        "dream_decision": dream_result.data,
        "decision_payload": decision_result.data["decision"]["decision"],
        "generated_task": decision_result.data["task_queue"][-1],
    }


def _compare_fields(name: str, expected: dict[str, Any], actual: dict[str, Any], *, required: bool) -> dict[str, Any]:
    expected_keys = set(expected.keys())
    actual_keys = set(actual.keys())
    return {
        "name": name,
        "required": required,
        "expected_field_count": len(expected_keys),
        "actual_field_count": len(actual_keys),
        "common_fields": sorted(expected_keys & actual_keys),
        "missing_in_actual": sorted(expected_keys - actual_keys),
        "extra_in_actual": sorted(actual_keys - expected_keys),
    }


def _known_drifts(comparisons: list[dict[str, Any]]) -> list[dict[str, Any]]:
    drifts: list[dict[str, Any]] = []
    for comparison in comparisons:
        name = comparison["name"]
        missing = set(comparison["missing_in_actual"])
        if name.startswith("executive_dream_output") and missing:
            drifts.append(
                {
                    "area": name,
                    "type": "placeholder_contract",
                    "fields": sorted(missing),
                    "reason": "Current `dream_decision_engine` returns `schema_v1_dream_decision` placeholder output, while Yang Zhuo mock uses `schema_v1_executive` decision card.",
                }
            )
        elif name.startswith("generated_task"):
            selected = sorted(field for field in missing if field not in {"task_id"})
            if selected:
                drifts.append(
                    {
                        "area": name,
                        "type": "task_payload_adapter_gap",
                        "fields": selected,
                        "reason": "Current `commit_decision` task candidates are lightweight task queue items, while Yang Zhuo task mock models formal task fields.",
                    }
                )
        elif name.endswith("skill_output_vs_yang_normal") or name.endswith("skill_output_vs_yang_need_executive"):
            if missing:
                drifts.append(
                    {
                        "area": name,
                        "type": "skill_enrichment_or_adapter_gap",
                        "fields": sorted(missing),
                        "reason": "Current Skill output may normalize or enrich payload fields instead of preserving all Yang Zhuo mock fields verbatim.",
                    }
                )
    return drifts


def _recommendations(known_drifts: list[dict[str, Any]]) -> list[str]:
    recommendations = [
        "Keep Staff and Manager adapter compatibility checks in regression because they should preserve Yang Zhuo top-level contract fields.",
        "After the database alignment report is added, map each drift field to its real database table and API endpoint.",
    ]
    if not known_drifts:
        recommendations.append("Keep `python scripts/check_yang_skill_field_alignment.py --strict` in regression; current Staff, Manager, Executive, and Task field alignment has no known drift.")
    if any(drift["type"] == "placeholder_contract" for drift in known_drifts):
        recommendations.append("Add a formal Executive decision card adapter or update `dream_decision_engine` to emit Yang Zhuo `schema_v1_executive` fields.")
    if any(drift["type"] == "task_payload_adapter_gap" for drift in known_drifts):
        recommendations.append("Add a task candidate adapter that maps Yang Zhuo `schema_v1_task` fields into `task_queue` and later formal `tasks` payloads.")
    return recommendations


def _render_report(output: dict[str, Any]) -> str:
    lines = [
        "# Yang Mock Skill Field Alignment",
        "",
        "## Summary",
        "",
        f"- **ok**: `{str(output['ok']).lower()}`",
        f"- **strict_ok**: `{str(output['strict_ok']).lower()}`",
        f"- **scope**: `{output['scope']}`",
        f"- **yang_mock_dir**: `{output['yang_mock_dir']}`",
        "",
        "## Comparison results",
        "",
        "| Area | Required | Expected fields | Actual fields | Missing in current output | Extra in current output |",
        "| ---- | -------- | --------------- | ------------- | ------------------------- | ----------------------- |",
    ]
    for comparison in output["comparisons"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    comparison["name"],
                    str(comparison["required"]).lower(),
                    str(comparison["expected_field_count"]),
                    str(comparison["actual_field_count"]),
                    _inline_list(comparison["missing_in_actual"]),
                    _inline_list(comparison["extra_in_actual"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Known drifts", ""])
    if output["known_drifts"]:
        for drift in output["known_drifts"]:
            lines.extend(
                [
                    f"### {drift['area']}",
                    "",
                    f"- **type**: `{drift['type']}`",
                    f"- **fields**: {_inline_list(drift['fields'])}",
                    f"- **reason**: {drift['reason']}",
                    "",
                ]
            )
    else:
        lines.append("No known drifts.")
    lines.extend(["", "## Recommendations", ""])
    for recommendation in output["recommendations"]:
        lines.append(f"- **Action**: {recommendation}")
    lines.extend(
        [
            "",
            "## Commands",
            "",
            "```powershell",
            "python scripts/check_yang_skill_field_alignment.py",
            "python scripts/check_yang_skill_field_alignment.py --strict",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def _inline_list(values: list[str]) -> str:
    if not values:
        return "-"
    return "<br>".join(f"`{value}`" for value in values)


def _summary(output: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": output["ok"],
        "strict_ok": output["strict_ok"],
        "report_path": output["report_path"],
        "blocking_failure_count": len(output["blocking_failures"]),
        "known_drift_count": len(output["known_drifts"]),
        "known_drift_types": sorted({drift["type"] for drift in output["known_drifts"]}),
    }


def _load_json(name: str) -> Any:
    path = YANG_MOCK_DIR / name
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
