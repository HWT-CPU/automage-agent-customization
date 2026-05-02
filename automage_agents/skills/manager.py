from __future__ import annotations

from typing import Any

from automage_agents.core.models import SkillResult
from automage_agents.schemas.placeholders import MANAGER_REPORT_SCHEMA_ID, ManagerReportDraft
from automage_agents.skills.context import SkillContext
from automage_agents.skills.result import api_response_to_skill_result
from automage_agents.skills.schema_tools import schema_self_correct, validate_manager_report_payload


def analyze_team_reports(context: SkillContext, date: str | None = None) -> SkillResult:
    # TODO(熊锦文): 等后端确认部门日报读取 API 后，改为真实读取本部门 Staff 日报。
    return SkillResult(
        ok=False,
        data={"department_id": context.identity.department_id, "date": date},
        message="Department report read API is not confirmed yet.",
        error_code="api_contract_pending",
    )


def generate_manager_report(context: SkillContext, report: ManagerReportDraft | dict[str, Any]) -> SkillResult:
    payload = _to_payload(report)
    validation = validate_manager_report_payload(payload)
    if not validation.ok:
        return validation

    response = context.api_client.post_manager_report(context.identity, payload)
    result = api_response_to_skill_result(response, "manager report submitted")
    if result.error_code == "schema_validation_failed":
        return schema_self_correct(payload, result.data.get("response", {}), MANAGER_REPORT_SCHEMA_ID)
    return result


def generate_manager_schema(context: SkillContext, report: ManagerReportDraft | dict[str, Any]) -> SkillResult:
    return generate_manager_report(context, report)


def delegate_task(context: SkillContext, task_payload: dict[str, Any]) -> SkillResult:
    # TODO(熊锦文): 确认权限内任务分发 API；如复用 decision/commit，需要确认请求体和审批边界。
    return SkillResult(
        ok=False,
        data={"identity": context.identity.to_dict(), "task": task_payload},
        message="Task delegation API is not confirmed yet.",
        error_code="api_contract_pending",
    )


def _to_payload(report: ManagerReportDraft | dict[str, Any]) -> dict[str, Any]:
    if isinstance(report, ManagerReportDraft):
        return report.to_payload()
    return dict(report)
