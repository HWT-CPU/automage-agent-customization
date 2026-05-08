from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.config.settings import RuntimeSettings

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    args = _parse_args()
    settings = RuntimeSettings.from_env()
    base_url = (args.base_url or settings.api_base_url).rstrip("/")
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    checks = _build_checks(run_id)

    if args.dry_run:
        output = {
            "ok": True,
            "mode": "dry_run",
            "base_url": base_url,
            "run_id": run_id,
            "auth_header_configured": bool(settings.auth_token),
            "would_run": [_public_check(check) for check in checks],
            "note": "Backend API is not called in dry-run mode.",
        }
        if args.output_json:
            _write_json(Path(args.output_json), output)
        print(_json_dumps(output))
        return

    results = []
    for check in checks:
        results.append(_run_check(base_url, check, settings=settings, timeout=args.timeout_seconds))
        time.sleep(args.pause_seconds)

    blocked = any(result.get("blocked") for result in results)
    failed = any(not result.get("ok") for result in results)
    output = {
        "ok": not failed,
        "blocked": blocked,
        "mode": "real_api_smoke",
        "base_url": base_url,
        "run_id": run_id,
        "auth_header_configured": bool(settings.auth_token),
        "results": results,
    }
    if args.output_json:
        _write_json(Path(args.output_json), output)
    print_output = output
    if args.summary_only:
        print_output = {
            **{key: value for key, value in output.items() if key != "results"},
            "results": [_result_summary(result) for result in results],
            "output_json": args.output_json,
        }
    print(_json_dumps(print_output))
    if failed:
        raise SystemExit(2 if blocked else 1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test the real AutoMage CRUD API without printing secrets.")
    parser.add_argument("--base-url", help="Override AUTOMAGE_API_BASE_URL for this run.")
    parser.add_argument("--timeout-seconds", type=float, default=5.0)
    parser.add_argument("--pause-seconds", type=float, default=0.1)
    parser.add_argument("--dry-run", action="store_true", help="Print planned requests without calling the backend.")
    parser.add_argument("--run-id", help="Stable ASCII run id used for idempotency keys and generated task ids.")
    parser.add_argument("--summary-only", action="store_true", help="Print only per-step status summaries for real API runs.")
    parser.add_argument("--output-json", help="Write the full JSON result to this path without printing secrets.")
    return parser.parse_args()


def _build_checks(run_id: str) -> list[dict[str, Any]]:
    run_token = _safe_token(run_id)
    smoke_date = _record_date_from_run_id(run_token)
    task_suffix = _task_suffix(run_token)
    task_id = f"TASK-SMOKE-{task_suffix[-14:]}"
    direct_task_id = f"TASK-SMOKE-DIRECT-{task_suffix[-8:]}"
    runtime_context = {
        "org_id": "org_automage_mvp",
        "run_date": smoke_date,
        "workflow_name": "milestone2_real_api_smoke",
        "workflow_stage": "database_skill_smoke",
        "source_channel": "script",
    }
    staff_identity = {
        "node_id": "staff_agent_mvp_001",
        "user_id": "zhangsan",
        "role": "staff",
        "level": "l1_staff",
        "department_id": "dept_mvp_core",
        "manager_node_id": "manager_agent_mvp_001",
        "metadata": {"display_name": "张三", "org_id": "org_automage_mvp"},
    }
    manager_identity = {
        "node_id": "manager_agent_mvp_001",
        "user_id": "lijingli",
        "role": "manager",
        "level": "l2_manager",
        "department_id": "dept_mvp_core",
        "manager_node_id": "executive_agent_boss_001",
        "metadata": {"display_name": "李经理", "org_id": "org_automage_mvp"},
    }
    executive_identity = {
        "node_id": "executive_agent_boss_001",
        "user_id": "chenzong",
        "role": "executive",
        "level": "l3_executive",
        "department_id": "dept_mvp_core",
        "manager_node_id": None,
        "metadata": {"display_name": "陈总", "org_id": "org_automage_mvp"},
    }
    return [
        {
            "name": "agent_init_staff",
            "method": "POST",
            "path": "/api/v1/agent/init",
            "headers": _identity_headers(staff_identity, f"smoke-agent-init-{run_token}"),
            "body": {"identity": staff_identity, "context": runtime_context},
        },
        {
            "name": "post_staff_report",
            "method": "POST",
            "path": "/api/v1/report/staff",
            "headers": _identity_headers(
                staff_identity,
                f"smoke-staff-report-{run_token}",
                idempotency_key=f"smoke-staff-report-{run_token}",
            ),
            "body": {
                "identity": staff_identity,
                "report": {
                    "schema_id": "schema_v1_staff",
                    "schema_version": "1.0.0",
                    "timestamp": f"{smoke_date}T15:00:00+08:00",
                    "org_id": "org_automage_mvp",
                    "department_id": "dept_mvp_core",
                    "user_id": staff_identity["user_id"],
                    "node_id": staff_identity["node_id"],
                    "record_date": smoke_date,
                    "work_progress": f"Real API smoke test payload from AutoMage Agent side. run_id={run_token}",
                    "issues_faced": [],
                    "solution_attempt": "Use minimal smoke payload and inspect API response.",
                    "need_support": False,
                    "next_day_plan": "Continue Milestone 2 to Milestone 3 integration after API is ready.",
                    "risk_level": "medium",
                    "signature": {"confirm_status": "confirmed", "confirmed_by": staff_identity["user_id"]},
                    "meta": {"context": runtime_context},
                },
            },
        },
        {
            "name": "post_manager_report",
            "method": "POST",
            "path": "/api/v1/report/manager",
            "headers": _identity_headers(
                manager_identity,
                f"smoke-manager-report-{run_token}",
                idempotency_key=f"smoke-manager-report-{run_token}",
            ),
            "body": {
                "identity": manager_identity,
                "report": {
                    "schema_id": "schema_v1_manager",
                    "schema_version": "1.0.0",
                    "timestamp": f"{smoke_date}T18:00:00+08:00",
                    "org_id": "org_automage_mvp",
                    "dept_id": "dept_mvp_core",
                    "manager_user_id": manager_identity["user_id"],
                    "manager_node_id": manager_identity["node_id"],
                    "summary_date": smoke_date,
                    "overall_health": "yellow",
                    "aggregated_summary": f"Real API smoke test manager summary. run_id={run_token}",
                    "top_3_risks": ["Backend API readiness is still the main-chain dependency."],
                    "pending_approvals": 1,
                    "source_record_ids": [],
                    "signature": {"confirm_status": "confirmed", "confirmed_by": manager_identity["user_id"]},
                    "meta": {"context": runtime_context},
                },
            },
        },
        {
            "name": "commit_decision",
            "method": "POST",
            "path": "/api/v1/decision/commit",
            "headers": _identity_headers(
                executive_identity,
                f"smoke-decision-commit-{run_token}",
                idempotency_key=f"smoke-decision-commit-{run_token}",
            ),
            "body": {
                "identity": executive_identity,
                "decision": {
                    "org_id": "org_automage_mvp",
                    "department_id": "dept_mvp_core",
                    "title": "Real API smoke decision",
                    "description": "Smoke decision commit for Milestone 2 backend readiness.",
                    "decision_summary": "Smoke decision commit for Milestone 2 backend readiness.",
                    "selected_option_id": "A",
                    "selected_option_label": "Run minimal validation",
                    "priority": "medium",
                    "task_candidates": [
                        {
                            "task_id": task_id,
                            "org_id": "org_automage_mvp",
                            "department_id": "dept_mvp_core",
                            "task_title": "Complete real API smoke validation",
                            "task_description": "Run smoke_real_api.py after backend API starts.",
                            "creator_user_id": executive_identity["user_id"],
                            "manager_user_id": manager_identity["user_id"],
                            "manager_node_id": manager_identity["node_id"],
                            "assignee_user_id": staff_identity["user_id"],
                            "assignee_node_id": staff_identity["node_id"],
                            "priority": "medium",
                            "status": "pending",
                            "meta": {"context": runtime_context},
                        }
                    ],
                    "meta": {"context": runtime_context},
                },
            },
        },
        {
            "name": "post_tasks",
            "method": "POST",
            "path": "/api/v1/tasks",
            "headers": _identity_headers(
                manager_identity,
                f"smoke-post-tasks-{run_token}",
                idempotency_key=f"smoke-post-tasks-{run_token}",
            ),
            "body": {
                "tasks": [
                    {
                        "schema_id": "schema_v1_task",
                        "schema_version": "1.0.0",
                        "task_id": direct_task_id,
                        "org_id": "org_automage_mvp",
                        "department_id": "dept_mvp_core",
                        "task_title": "Verify direct task API from smoke",
                        "task_description": "Direct task creation aligned with M2 real API acceptance.",
                        "source_type": "real_api_smoke",
                        "source_id": run_token,
                        "creator_user_id": manager_identity["user_id"],
                        "created_by_node_id": manager_identity["node_id"],
                        "manager_user_id": manager_identity["user_id"],
                        "manager_node_id": manager_identity["node_id"],
                        "assignee_user_id": staff_identity["user_id"],
                        "assignee_node_id": staff_identity["node_id"],
                        "priority": "medium",
                        "status": "pending",
                        "meta": {"context": runtime_context},
                    }
                ]
            },
        },
        {
            "name": "fetch_tasks",
            "method": "GET",
            "path": "/api/v1/tasks",
            "headers": _identity_headers(staff_identity, f"smoke-fetch-tasks-{run_token}"),
            "query": {"org_id": "org_automage_mvp", "assignee_user_id": staff_identity["user_id"]},
        },
        {
            "name": "patch_task",
            "method": "PATCH",
            "path": f"/api/v1/tasks/{direct_task_id}",
            "headers": _identity_headers(
                staff_identity,
                f"smoke-patch-task-{run_token}",
                idempotency_key=f"smoke-patch-task-{run_token}",
            ),
            "body": {
                "status": "in_progress",
                "title": "Verify direct task API from smoke",
                "description": "Staff started the direct smoke task.",
                "task_payload": {"run_id": run_token, "source_channel": "script"},
            },
        },
    ]


def _run_check(base_url: str, check: dict[str, Any], *, settings: RuntimeSettings, timeout: float) -> dict[str, Any]:
    url = _build_url(base_url, check["path"], check.get("query"))
    body = _encode_body(check.get("body"))
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    headers.update(settings.auth_headers())
    headers.update(check.get("headers", {}))
    request = Request(url=url, data=body, headers=headers, method=check["method"])
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = _read_payload(response.read())
            return {
                "name": check["name"],
                "ok": 200 <= response.status < 300,
                "blocked": False,
                "status_code": response.status,
                "path": check["path"],
                "response": payload,
            }
    except HTTPError as exc:
        return {
            "name": check["name"],
            "ok": False,
            "blocked": False,
            "status_code": exc.code,
            "path": check["path"],
            "response": _read_payload(exc.read()),
        }
    except URLError as exc:
        return {
            "name": check["name"],
            "ok": False,
            "blocked": True,
            "status_code": None,
            "path": check["path"],
            "error": str(exc.reason),
        }
    except TimeoutError as exc:
        return {
            "name": check["name"],
            "ok": False,
            "blocked": True,
            "status_code": None,
            "path": check["path"],
            "error": str(exc),
        }


def _build_url(base_url: str, path: str, query: dict[str, Any] | None) -> str:
    url = f"{base_url}{path}"
    if query:
        clean_query = {key: value for key, value in query.items() if value is not None}
        url = f"{url}?{urlencode(clean_query)}"
    return url


def _encode_body(body: dict[str, Any] | None) -> bytes | None:
    if body is None:
        return None
    return json.dumps(body, ensure_ascii=False).encode("utf-8")


def _read_payload(raw: bytes) -> Any:
    if not raw:
        return {}
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        return raw.decode("utf-8", errors="replace")


def _result_summary(result: dict[str, Any]) -> dict[str, Any]:
    response = result.get("response")
    detail = None
    msg = None
    error_code = None
    conflict_target = None
    request_id = None
    if isinstance(response, dict):
        detail = response.get("detail")
        msg = response.get("msg")
        error = response.get("error")
        if isinstance(error, dict):
            error_code = error.get("error_code")
            conflict_target = error.get("conflict_target")
            request_id = error.get("request_id")
        request_id = request_id or response.get("request_id")
    return {
        "name": result.get("name"),
        "ok": result.get("ok"),
        "blocked": result.get("blocked"),
        "status_code": result.get("status_code"),
        "path": result.get("path"),
        "detail": detail,
        "msg": msg,
        "error_code": error_code,
        "conflict_target": conflict_target,
        "request_id": request_id,
        "error": result.get("error"),
    }


def _public_check(check: dict[str, Any]) -> dict[str, Any]:
    headers = check.get("headers", {})
    return {
        "name": check["name"],
        "method": check["method"],
        "path": check["path"],
        "query": check.get("query", {}),
        "has_body": bool(check.get("body")),
        "identity_headers": sorted(key for key in headers if key.startswith("X-")),
        "idempotency_key_configured": "Idempotency-Key" in headers,
    }


def _identity_headers(identity: dict[str, Any], request_id: str, *, idempotency_key: str | None = None) -> dict[str, str]:
    headers = {
        "X-Request-Id": request_id,
        "X-User-Id": str(identity["user_id"]),
        "X-Role": str(identity["role"]),
        "X-Node-Id": str(identity["node_id"]),
        "X-Level": str(identity["level"]),
    }
    if identity.get("department_id"):
        headers["X-Department-Id"] = str(identity["department_id"])
    if identity.get("manager_node_id"):
        headers["X-Manager-Node-Id"] = str(identity["manager_node_id"])
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    return headers


def _safe_token(value: str) -> str:
    token = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in value)
    return token.strip("-_") or datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")


def _task_suffix(run_token: str) -> str:
    return "".join(char for char in run_token if char.isalnum()) or datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")


def _record_date_from_run_id(run_id: str) -> str:
    digits = "".join(char for char in run_id if char.isdigit())
    offset_seed = int(digits[-6:] or str(int(time.time()) % 100000))
    return (date(2026, 5, 7) + timedelta(days=offset_seed % 3650)).isoformat()


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_json_dumps(data), encoding="utf-8")


def _json_dumps(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=True, indent=2)


if __name__ == "__main__":
    main()
