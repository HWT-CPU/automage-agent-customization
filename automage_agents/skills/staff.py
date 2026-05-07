from __future__ import annotations

from typing import Any

from automage_agents.core.models import SkillResult
from automage_agents.knowledge.auto_context import ensure_feishu_knowledge_for_payload
from automage_agents.knowledge.payload_enrichment import enrich_business_payload_with_knowledge
from automage_agents.schemas.placeholders import STAFF_REPORT_SCHEMA_ID, StaffReportDraft
from automage_agents.schemas.staff_v1 import coerce_staff_report_v1_payload
from automage_agents.skills.context import SkillContext
from automage_agents.skills.result import api_response_to_skill_result
from automage_agents.skills.schema_tools import schema_self_correct, validate_staff_report_payload


def post_daily_report(context: SkillContext, report: StaffReportDraft | dict[str, Any]) -> SkillResult:
    payload = _to_payload(report)
    ensure_feishu_knowledge_for_payload(context.runtime, payload, "post_daily_report", context.identity.role.value)
    runtime_payload = context.runtime_payload()
    payload = enrich_business_payload_with_knowledge(payload, runtime_payload, "staff_report")
    payload = coerce_staff_report_v1_payload(payload, context.identity, runtime_payload)
    validation = validate_staff_report_payload(payload)
    if not validation.ok:
        return validation

    response = context.api_client.post_staff_report(context.identity, payload, runtime_payload)
    result = api_response_to_skill_result(response, "staff report submitted")
    if result.error_code == "schema_validation_failed":
        return schema_self_correct(payload, result.data.get("response", {}), STAFF_REPORT_SCHEMA_ID)
    return result


def fetch_my_tasks(context: SkillContext, status: str | None = None) -> SkillResult:
    response = context.api_client.fetch_tasks(context.identity, status=status)
    return api_response_to_skill_result(response, "tasks fetched")


def update_my_task(
    context: SkillContext,
    task_id: str,
    *,
    status: str | None = None,
    title: str | None = None,
    description: str | None = None,
    task_payload: dict[str, Any] | None = None,
) -> SkillResult:
    response = context.api_client.update_task(
        context.identity,
        task_id,
        status=status,
        title=title,
        description=description,
        task_payload=task_payload,
    )
    return api_response_to_skill_result(response, "task updated")


def import_staff_daily_report_from_markdown(context: SkillContext, report: str | dict[str, Any]) -> SkillResult:
    payload = _to_markdown_import_payload(report, context)
    response = context.api_client.import_staff_daily_report_from_markdown(context.identity, payload, context.runtime_payload())
    return api_response_to_skill_result(response, "staff daily report imported")


def read_staff_daily_report(context: SkillContext, work_record_id: str, output_format: str = "json") -> SkillResult:
    response = context.api_client.read_staff_daily_report(work_record_id, output_format, context.identity)
    return api_response_to_skill_result(response, "staff daily report loaded")


def _to_payload(report: StaffReportDraft | dict[str, Any]) -> dict[str, Any]:
    if isinstance(report, StaffReportDraft):
        return report.to_payload()
    return dict(report)


def _to_markdown_import_payload(report: str | dict[str, Any], context: SkillContext) -> dict[str, Any]:
    if isinstance(report, str):
        return {
            "markdown": report,
            "submitted_by": context.identity.user_id,
            "schema_id": "schema_v1_staff",
            "schema_version": "1.0.0",
        }
    payload = dict(report)
    payload.setdefault("submitted_by", context.identity.user_id)
    payload.setdefault("schema_id", "schema_v1_staff")
    payload.setdefault("schema_version", "1.0.0")
    return payload
