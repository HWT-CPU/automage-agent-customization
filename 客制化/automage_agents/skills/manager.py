from __future__ import annotations

from typing import Any

from automage_agents.ai.analysis_service import get_analysis_service
from automage_agents.core.models import SkillResult
from automage_agents.knowledge.auto_context import ensure_feishu_knowledge_for_payload
from automage_agents.knowledge.payload_enrichment import enrich_business_payload_with_knowledge
from automage_agents.schemas.manager_v1 import coerce_manager_report_v1_payload
from automage_agents.schemas.placeholders import MANAGER_REPORT_SCHEMA_ID, ManagerReportDraft
from automage_agents.skills.context import SkillContext
from automage_agents.skills.result import api_response_to_skill_result
from automage_agents.skills.schema_tools import schema_self_correct, validate_manager_report_payload


def analyze_team_reports(context: SkillContext, date: str | None = None) -> SkillResult:
    """分析团队日报，使用 AI 提取关键信息和风险"""
    # 1. 获取日报数据
    response = context.api_client.fetch_work_records(
        context.identity,
        department_id=context.identity.department_id,
        record_date_from=date,
        record_date_to=date,
    )
    
    result = api_response_to_skill_result(response, "team reports fetched")
    if not result.ok:
        return result
    
    # 2. 使用 AI 分析日报
    reports = result.data.get("records", []) if isinstance(result.data, dict) else []
    if not reports:
        return result
    
    try:
        # 获取知识库上下文
        knowledge_context = _extract_knowledge_context(context)
        
        # 调用 AI 分析服务
        analysis_service = get_analysis_service()
        analysis = analysis_service.analyze_team_reports(
            reports=reports,
            department=context.identity.department_id or "unknown",
            date=date or "today",
            knowledge_context=knowledge_context,
        )
        
        # 将分析结果添加到返回数据中
        result.data["ai_analysis"] = analysis
        result.message = f"team reports analyzed with AI: {len(reports)} reports, health={analysis.get('overall_health', 'unknown')}"
    except Exception as e:
        # AI 分析失败不影响原始数据返回
        result.data["ai_analysis_error"] = str(e)
    
    return result


def generate_manager_report(context: SkillContext, report: ManagerReportDraft | dict[str, Any]) -> SkillResult:
    """生成 Manager 汇总报告，使用 AI 增强内容"""
    payload = _to_payload(report)
    
    # 使用 AI 增强汇总内容
    try:
        knowledge_context = _extract_knowledge_context(context)
        analysis_service = get_analysis_service()
        
        # 如果 payload 中有 ai_analysis，使用它；否则尝试生成
        if "ai_analysis" not in payload and "aggregated_summary" in payload:
            # 生成更好的汇总文本
            enhanced_summary = analysis_service.generate_manager_summary(
                analysis=payload,
                department=context.identity.department_id or "unknown",
                date=payload.get("summary_date", "today"),
                knowledge_context=knowledge_context,
            )
            payload["aggregated_summary"] = enhanced_summary
    except Exception as e:
        # AI 增强失败不影响提交
        payload.setdefault("meta", {})
        if isinstance(payload["meta"], dict):
            payload["meta"]["ai_enhancement_error"] = str(e)
    
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



def _extract_knowledge_context(context: SkillContext) -> str:
    """从 runtime context 中提取知识库上下文"""
    try:
        feishu_ref = context.runtime.input_refs.get("feishu_knowledge", {})
        if isinstance(feishu_ref, dict):
            return str(feishu_ref.get("context_text", ""))
    except Exception:
        pass
    return ""
