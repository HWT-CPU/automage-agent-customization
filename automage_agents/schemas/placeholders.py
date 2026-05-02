from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


STAFF_REPORT_SCHEMA_ID = "schema_v1_staff"
MANAGER_REPORT_SCHEMA_ID = "schema_v1_manager"
DREAM_DECISION_SCHEMA_ID = "schema_v1_dream_decision"


@dataclass(slots=True)
class StaffReportDraft:
    timestamp: str
    work_progress: str
    issues_faced: str
    solution_attempt: str
    need_support: bool
    next_day_plan: str
    resource_usage: dict[str, Any] = field(default_factory=dict)

    # TODO(杨卓): Replace this draft with final schema_v1_staff validation rules.
    def to_payload(self) -> dict[str, Any]:
        return {
            "schema_id": STAFF_REPORT_SCHEMA_ID,
            "timestamp": self.timestamp,
            "work_progress": self.work_progress,
            "issues_faced": self.issues_faced,
            "solution_attempt": self.solution_attempt,
            "need_support": self.need_support,
            "next_day_plan": self.next_day_plan,
            "resource_usage": self.resource_usage,
        }


@dataclass(slots=True)
class ManagerReportDraft:
    dept_id: str
    overall_health: Literal["green", "yellow", "red"]
    aggregated_summary: str
    top_3_risks: list[str]
    workforce_efficiency: float
    pending_approvals: int

    # TODO(杨卓): Replace this draft with final schema_v1_manager validation rules.
    def to_payload(self) -> dict[str, Any]:
        return {
            "schema_id": MANAGER_REPORT_SCHEMA_ID,
            "dept_id": self.dept_id,
            "overall_health": self.overall_health,
            "aggregated_summary": self.aggregated_summary,
            "top_3_risks": self.top_3_risks,
            "workforce_efficiency": self.workforce_efficiency,
            "pending_approvals": self.pending_approvals,
        }


@dataclass(slots=True)
class DreamDecisionDraft:
    stage_goal: str
    manager_summary: dict[str, Any]
    external_variables: dict[str, Any] = field(default_factory=dict)

    # TODO(徐少洋): Replace this draft with final Dream input/output contract.
    def to_payload(self) -> dict[str, Any]:
        return {
            "schema_id": DREAM_DECISION_SCHEMA_ID,
            "stage_goal": self.stage_goal,
            "manager_summary": self.manager_summary,
            "external_variables": self.external_variables,
        }
