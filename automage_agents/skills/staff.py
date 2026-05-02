from __future__ import annotations

from typing import Any

from automage_agents.core.models import SkillResult
from automage_agents.schemas.placeholders import STAFF_REPORT_SCHEMA_ID, StaffReportDraft
from automage_agents.skills.context import SkillContext
from automage_agents.skills.result import api_response_to_skill_result
from automage_agents.skills.schema_tools import schema_self_correct, validate_staff_report_payload


def post_daily_report(context: SkillContext, report: StaffReportDraft | dict[str, Any]) -> SkillResult:
    payload = _to_payload(report)
    validation = validate_staff_report_payload(payload)
    if not validation.ok:
        return validation

    response = context.api_client.post_staff_report(context.identity, payload)
    result = api_response_to_skill_result(response, "staff report submitted")
    if result.error_code == "schema_validation_failed":
        return schema_self_correct(payload, result.data.get("response", {}), STAFF_REPORT_SCHEMA_ID)
    return result


def fetch_my_tasks(context: SkillContext, status: str | None = None) -> SkillResult:
    response = context.api_client.fetch_tasks(context.identity, status=status)
    return api_response_to_skill_result(response, "tasks fetched")


def _to_payload(report: StaffReportDraft | dict[str, Any]) -> dict[str, Any]:
    if isinstance(report, StaffReportDraft):
        return report.to_payload()
    return dict(report)
