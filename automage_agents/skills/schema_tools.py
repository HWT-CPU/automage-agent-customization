from __future__ import annotations

from typing import Any

from automage_agents.core.models import SkillResult
from automage_agents.schemas.placeholders import MANAGER_REPORT_SCHEMA_ID, STAFF_REPORT_SCHEMA_ID


STAFF_REQUIRED_FIELDS = {
    "timestamp",
    "work_progress",
    "issues_faced",
    "solution_attempt",
    "need_support",
    "next_day_plan",
    "resource_usage",
}

MANAGER_REQUIRED_FIELDS = {
    "dept_id",
    "overall_health",
    "aggregated_summary",
    "top_3_risks",
    "workforce_efficiency",
    "pending_approvals",
}


def validate_required_fields(payload: dict[str, Any], required_fields: set[str]) -> SkillResult:
    missing = sorted(field for field in required_fields if field not in payload)
    if missing:
        return SkillResult(
            ok=False,
            data={"missing_fields": missing, "payload": payload},
            message="Missing required schema fields.",
            error_code="local_schema_validation_failed",
        )
    return SkillResult(ok=True, data={"payload": payload}, message="schema validation passed")


def validate_staff_report_payload(payload: dict[str, Any]) -> SkillResult:
    # TODO(杨卓): Replace required-field check with final schema_v1_staff validation rules.
    return validate_required_fields(payload, STAFF_REQUIRED_FIELDS)


def validate_manager_report_payload(payload: dict[str, Any]) -> SkillResult:
    # TODO(杨卓): Replace required-field check with final schema_v1_manager validation rules.
    return validate_required_fields(payload, MANAGER_REQUIRED_FIELDS)


def schema_self_correct(
    payload: dict[str, Any],
    backend_error: dict[str, Any] | str,
    schema_id: str = STAFF_REPORT_SCHEMA_ID,
) -> SkillResult:
    # TODO(Hermes): Use Hermes LLM runtime to rewrite payload according to backend 422 details.
    # TODO(杨卓): Use final schema rules to constrain self-correction output.
    known_schema = schema_id in {STAFF_REPORT_SCHEMA_ID, MANAGER_REPORT_SCHEMA_ID}
    return SkillResult(
        ok=False,
        data={
            "schema_id": schema_id,
            "known_schema": known_schema,
            "original_payload": payload,
            "backend_error": backend_error,
            "requires_hermes_runtime": True,
        },
        message="Schema self-correction requires Hermes runtime and final schema contract.",
        error_code="schema_self_correction_pending",
    )
