from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
YANG_MOCK_DIR = PROJECT_ROOT / "里程碑二_杨卓_交付推进与联调v1.0.0"
DATABASE_REPORT_DIR = PROJECT_ROOT / "里程碑二_杨卓_数据库测试对齐报告v1.0.0"
LOCAL_KB_DIR = PROJECT_ROOT / "AutoMage_2_MVP_KB_v1.0.0"


def main() -> None:
    args = _parse_args()
    yang_result = _run_yang_mock_workflow(write_output=args.write_yang_output)
    yang_checks = _validate_yang_result(yang_result)
    kb_status = _check_local_kb()
    database_report_status = _check_database_report()

    ok = (
        yang_checks["ok"]
        and (kb_status["ready"] or not args.require_local_kb)
        and (database_report_status["ready"] or not args.require_database_report)
    )
    output = {
        "ok": ok,
        "scope": "yang-milestone2-mock-workflow-and-local-kb-regression",
        "yang_mock_workflow": {
            "ok": yang_checks["ok"],
            "package_dir": str(YANG_MOCK_DIR),
            "overall_status": yang_result.get("overall_status"),
            "dag_run_id": yang_result.get("dag_run_id"),
            "checks": yang_result.get("checks", {}),
            "generated_task_ids": yang_result.get("generated_task_ids", []),
            "assertions": yang_checks["assertions"],
        },
        "local_architecture_kb": kb_status,
        "database_alignment_report": database_report_status,
        "notes": [
            "Yang Zhuo mock workflow is treated as the standard local M2 contract package.",
            "The local architecture KB is registered as a reference source, but later milestone documents take priority on conflicts.",
            "The database alignment report is not required by default because its local directory is currently empty.",
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if not ok:
        raise SystemExit(1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Yang Zhuo M2 mock workflow package and local architecture KB readiness.")
    parser.add_argument("--write-yang-output", action="store_true", help="Allow Yang workflow to write its runtime output file.")
    parser.add_argument("--require-local-kb", action="store_true", help="Fail if the optional local architecture KB package is missing.")
    parser.add_argument("--require-database-report", action="store_true", help="Fail if the database alignment report directory is empty.")
    return parser.parse_args()


def _run_yang_mock_workflow(*, write_output: bool) -> dict[str, Any]:
    workflow_path = YANG_MOCK_DIR / "run_mock_workflow.py"
    if not workflow_path.exists():
        raise FileNotFoundError(f"Yang mock workflow script not found: {workflow_path}")
    spec = importlib.util.spec_from_file_location("yang_mock_workflow", workflow_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load Yang mock workflow script: {workflow_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    result = module.run(write_output=write_output)
    if not isinstance(result, dict):
        raise TypeError("Yang mock workflow returned a non-dict result")
    return result


def _validate_yang_result(result: dict[str, Any]) -> dict[str, Any]:
    checks = result.get("checks", {})
    assertions = [
        _assert_equal("overall_status", result.get("overall_status"), "passed"),
        _assert_equal("staff_reports_count", checks.get("staff_reports_count"), 2),
        _assert_equal("has_high_risk_report", checks.get("has_high_risk_report"), True),
        _assert_equal("manager_needs_executive", checks.get("manager_needs_executive"), True),
        _assert_equal("executive_decision_required", checks.get("executive_decision_required"), True),
        _assert_equal("generated_tasks_count", checks.get("generated_tasks_count"), 3),
        _assert_equal("next_round_seed_present", checks.get("next_round_seed_present"), True),
        _assert_equal("steps_all_passed", all(step.get("status") == "passed" for step in result.get("steps", [])), True),
    ]
    return {"ok": all(assertion["ok"] for assertion in assertions), "assertions": assertions}


def _check_local_kb() -> dict[str, Any]:
    required_paths = [
        LOCAL_KB_DIR / "05_AGENT_SKILL" / "SKILL.md",
        LOCAL_KB_DIR / "03_INDEX" / "00_总导航.md",
        LOCAL_KB_DIR / "03_INDEX" / "01_章节目录索引.md",
        LOCAL_KB_DIR / "02_CHAPTERS",
        LOCAL_KB_DIR / "01_PAGES",
        LOCAL_KB_DIR / "00_SOURCE",
    ]
    missing = [str(path.relative_to(PROJECT_ROOT)) for path in required_paths if not path.exists()]
    return {
        "ready": not missing,
        "package_dir": str(LOCAL_KB_DIR),
        "skill_file": str(LOCAL_KB_DIR / "05_AGENT_SKILL" / "SKILL.md"),
        "reading_order": ["03_INDEX", "02_CHAPTERS", "01_PAGES", "00_SOURCE"],
        "missing": missing,
    }


def _check_database_report() -> dict[str, Any]:
    if not DATABASE_REPORT_DIR.exists():
        return {
            "ready": False,
            "status": "missing_directory",
            "package_dir": str(DATABASE_REPORT_DIR),
            "file_count": 0,
        }
    files = [path for path in DATABASE_REPORT_DIR.rglob("*") if path.is_file()]
    return {
        "ready": bool(files),
        "status": "ready" if files else "blocked_empty_directory",
        "package_dir": str(DATABASE_REPORT_DIR),
        "file_count": len(files),
        "files": [str(path.relative_to(DATABASE_REPORT_DIR)) for path in files[:20]],
    }


def _assert_equal(name: str, actual: Any, expected: Any) -> dict[str, Any]:
    return {"name": name, "ok": actual == expected, "actual": actual, "expected": expected}


if __name__ == "__main__":
    main()
