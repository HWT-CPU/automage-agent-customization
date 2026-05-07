from __future__ import annotations

from typing import Any

from automage_agents.core.enums import InternalEventType
from automage_agents.core.models import InternalEvent, SkillResult
from automage_agents.schemas.placeholders import ManagerReportDraft, StaffReportDraft
from automage_agents.skills.context import SkillContext
from automage_agents.skills.executive import commit_decision, dream_decision_engine
from automage_agents.skills.manager import generate_manager_report
from automage_agents.skills.staff import fetch_my_tasks, post_daily_report


class InternalEventRouter:
    def __init__(self, staff_context: SkillContext, manager_context: SkillContext, executive_context: SkillContext):
        self.staff_context = staff_context
        self.manager_context = manager_context
        self.executive_context = executive_context

    def route(self, event: InternalEvent) -> SkillResult:
        if event.event_type == InternalEventType.DAILY_REPORT_SUBMITTED:
            return post_daily_report(self.staff_context, self._build_staff_report(event.payload))
        if event.event_type == InternalEventType.TASK_QUERY_REQUESTED:
            return fetch_my_tasks(self.staff_context, status=event.payload.get("status"))
        if event.event_type == InternalEventType.MANAGER_FEEDBACK_SUBMITTED:
            return generate_manager_report(self.manager_context, self._build_manager_report(event.payload))
        if event.event_type == InternalEventType.EXECUTIVE_DECISION_SELECTED:
            return commit_decision(self.executive_context, event.payload)
        if event.event_type == InternalEventType.AUTH_FAILED:
            return SkillResult(ok=False, data=event.payload, message="Auth failed event received.", error_code="auth_failed")
        return SkillResult(ok=False, data=event.payload, message="Unsupported event type.", error_code="unsupported_event")

    def run_dream_decision(self, payload: dict[str, Any]) -> SkillResult:
        return dream_decision_engine(self.executive_context, payload)

    def _build_staff_report(self, payload: dict[str, Any]) -> StaffReportDraft | dict[str, Any]:
        if payload.get("schema_id") == "schema_v1_staff":
            return dict(payload)
        return StaffReportDraft(
            timestamp=str(payload["timestamp"]),
            work_progress=str(payload["work_progress"]),
            issues_faced=str(payload["issues_faced"]),
            solution_attempt=str(payload["solution_attempt"]),
            need_support=bool(payload["need_support"]),
            next_day_plan=str(payload["next_day_plan"]),
            resource_usage=dict(payload.get("resource_usage", {})),
        )

    def _build_manager_report(self, payload: dict[str, Any]) -> ManagerReportDraft:
        return ManagerReportDraft(
            dept_id=str(payload["dept_id"]),
            overall_health=payload["overall_health"],
            aggregated_summary=str(payload["aggregated_summary"]),
            top_3_risks=list(payload["top_3_risks"]),
            workforce_efficiency=float(payload["workforce_efficiency"]),
            pending_approvals=int(payload["pending_approvals"]),
        )
