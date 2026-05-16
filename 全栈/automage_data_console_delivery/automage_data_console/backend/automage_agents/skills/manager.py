from __future__ import annotations

from typing import Any

from automage_agents.core.models import SkillResult
from automage_agents.knowledge.auto_context import ensure_feishu_knowledge_for_payload
from automage_agents.knowledge.payload_enrichment import enrich_business_payload_with_knowledge
from automage_agents.schemas.manager_v1 import coerce_manager_report_v1_payload
from automage_agents.schemas.placeholders import MANAGER_REPORT_SCHEMA_ID, ManagerReportDraft
from automage_agents.skills.context import SkillContext
from automage_agents.skills.result import api_response_to_skill_result
from automage_agents.skills.schema_tools import schema_self_correct, validate_manager_report_payload


def analyze_team_reports(context: SkillContext, date: str | None = None) -> SkillResult:
    response = context.api_client.fetch_work_records(
        context.identity,
        department_id=context.identity.department_id,
        record_date_from=date,
        record_date_to=date,
    )
    return api_response_to_skill_result(response, "team reports fetched")


def generate_manager_report(context: SkillContext, report: ManagerReportDraft | dict[str, Any]) -> SkillResult:
    payload = _to_payload(report)
    ensure_feishu_knowledge_for_payload(context.runtime, payload, "generate_manager_report", context.identity.role.value)
    runtime_payload = context.runtime_payload()
    payload = enrich_business_payload_with_knowledge(payload, runtime_payload, "manager_report")
    payload = coerce_manager_report_v1_payload(payload, context.identity, runtime_payload)
    validation = validate_manager_report_payload(payload)
    if not validation.ok:
        return validation

    response = context.api_client.post_manager_report(context.identity, payload, runtime_payload)
    result = api_response_to_skill_result(response, "manager report submitted")
    if result.error_code == "schema_validation_failed":
        return schema_self_correct(payload, result.data.get("response", {}), MANAGER_REPORT_SCHEMA_ID)
    return result


def generate_manager_schema(context: SkillContext, report: ManagerReportDraft | dict[str, Any]) -> SkillResult:
    return generate_manager_report(context, report)


def delegate_task(context: SkillContext, task_payload: dict[str, Any]) -> SkillResult:
    response = context.api_client.create_task(context.identity, task_payload, context.runtime_payload())
    return api_response_to_skill_result(response, "task delegated")


def _to_payload(report: ManagerReportDraft | dict[str, Any]) -> dict[str, Any]:
    if isinstance(report, ManagerReportDraft):
        return report.to_payload()
    return dict(report)
