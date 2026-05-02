from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from automage_agents.api.models import ApiResponse
from automage_agents.core.models import AgentIdentity


@dataclass(slots=True)
class MockBackendState:
    staff_reports: list[dict[str, Any]] = field(default_factory=list)
    manager_reports: list[dict[str, Any]] = field(default_factory=list)
    decision_logs: list[dict[str, Any]] = field(default_factory=list)
    task_queue: list[dict[str, Any]] = field(default_factory=list)
    initialized_agents: list[dict[str, Any]] = field(default_factory=list)


class MockAutoMageApiClient:
    def __init__(self, state: MockBackendState | None = None):
        self.state = state or MockBackendState()

    def agent_init(self, identity: AgentIdentity) -> ApiResponse:
        self.state.initialized_agents.append(identity.to_dict())
        return ApiResponse(
            status_code=200,
            code=200,
            data={"auth_status": "active", "identity": identity.to_dict()},
            msg="mock agent initialized",
        )

    def post_staff_report(self, identity: AgentIdentity, report_payload: dict[str, Any]) -> ApiResponse:
        record = {"identity": identity.to_dict(), "report": report_payload}
        self.state.staff_reports.append(record)
        return ApiResponse(status_code=200, code=200, data={"record": record}, msg="mock staff report saved")

    def fetch_tasks(self, identity: AgentIdentity, status: str | None = None) -> ApiResponse:
        tasks = [task for task in self.state.task_queue if task.get("assignee_user_id") in {identity.user_id, None}]
        if status:
            tasks = [task for task in tasks if task.get("status") == status]
        return ApiResponse(status_code=200, code=200, data={"tasks": tasks}, msg="mock tasks fetched")

    def post_manager_report(self, identity: AgentIdentity, report_payload: dict[str, Any]) -> ApiResponse:
        record = {"identity": identity.to_dict(), "report": report_payload}
        self.state.manager_reports.append(record)
        return ApiResponse(status_code=200, code=200, data={"record": record}, msg="mock manager report saved")

    def commit_decision(self, identity: AgentIdentity, decision_payload: dict[str, Any]) -> ApiResponse:
        decision_record = {"identity": identity.to_dict(), "decision": decision_payload}
        self.state.decision_logs.append(decision_record)
        for index, task in enumerate(decision_payload.get("task_candidates", []), start=1):
            self.state.task_queue.append({"task_id": f"mock-task-{index}", "status": "pending", **task})
        return ApiResponse(
            status_code=200,
            code=200,
            data={"decision": decision_record, "task_queue": self.state.task_queue},
            msg="mock decision committed",
        )
