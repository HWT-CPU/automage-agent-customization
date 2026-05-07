from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import Any

from automage_agents.api.models import ApiResponse
from automage_agents.core.models import AgentIdentity


@dataclass(slots=True)
class MockBackendState:
    agent_sessions: list[dict[str, Any]] = field(default_factory=list)
    staff_reports: list[dict[str, Any]] = field(default_factory=list)
    form_templates: list[dict[str, Any]] = field(default_factory=list)
    work_records: list[dict[str, Any]] = field(default_factory=list)
    work_record_items: list[dict[str, Any]] = field(default_factory=list)
    manager_reports: list[dict[str, Any]] = field(default_factory=list)
    agent_decision_logs: list[dict[str, Any]] = field(default_factory=list)
    decision_logs: list[dict[str, Any]] = field(default_factory=list)
    task_queue: list[dict[str, Any]] = field(default_factory=list)
    initialized_agents: list[dict[str, Any]] = field(default_factory=list)
    audit_logs: list[dict[str, Any]] = field(default_factory=list)


class MockAutoMageApiClient:
    def __init__(self, state: MockBackendState | None = None):
        self.state = state or MockBackendState()

    def agent_init(self, identity: AgentIdentity, runtime_context: dict[str, Any] | None = None) -> ApiResponse:
        session_id = f"mock-agent-session-{len(self.state.initialized_agents) + 1}"
        session = {
            "agent_session_id": session_id,
            "storage_table": "agent_sessions",
            "identity": identity.to_dict(),
            "context": runtime_context or {},
        }
        self.state.agent_sessions.append(session)
        self.state.initialized_agents.append(session)
        audit_log_id = self._append_audit_log("agent_init", "agent_sessions", session_id, session)
        return ApiResponse(
            status_code=200,
            code=200,
            data={
                "agent_session_id": session_id,
                "audit_log_id": audit_log_id,
                "org_id": (runtime_context or {}).get("org_id", "org-001"),
                "user_id": identity.user_id,
                "node_id": identity.node_id,
                "node_type": identity.role.value,
                "roles": [identity.role.value],
                "department_ids": [identity.department_id] if identity.department_id else [],
                "permission_scope": {"mock": True},
                "supported_schemas": {"report": ["schema_v1_staff", "schema_v1_manager"]},
                "auth_status": "active",
                "identity": identity.to_dict(),
                "context": runtime_context or {},
            },
            msg="mock agent initialized",
        )

    def post_staff_report(
        self,
        identity: AgentIdentity,
        report_payload: dict[str, Any],
        runtime_context: dict[str, Any] | None = None,
    ) -> ApiResponse:
        work_record_id = self._next_work_record_id()
        staff_report_id = f"mock-staff-report-{len(self.state.staff_reports) + 1}"
        record = {
            "staff_report_id": staff_report_id,
            "work_record_id": work_record_id,
            "storage_mode": "snapshot",
            "storage_table": "staff_reports",
            "identity": identity.to_dict(),
            "context": runtime_context or {},
            "report": report_payload,
            "status": "submitted",
        }
        self.state.staff_reports.append(record)
        audit_log_id = self._append_audit_log("post_staff_report", "staff_reports", staff_report_id, record)
        return ApiResponse(
            status_code=200,
            code=200,
            data={
                "staff_report_id": staff_report_id,
                "work_record_id": work_record_id,
                "created_incident_ids": [],
                "updated_task_ids": [],
                "audit_log_id": audit_log_id,
                "record": record,
            },
            msg="mock staff report saved",
        )

    def import_staff_daily_report_from_markdown(
        self,
        identity: AgentIdentity,
        import_payload: dict[str, Any],
        runtime_context: dict[str, Any] | None = None,
    ) -> ApiResponse:
        work_record_id = self._next_work_record_id()
        form_template_id = str(import_payload.get("form_template_id") or f"mock-form-template-{len(self.state.form_templates) + 1}")
        markdown = self._extract_markdown(import_payload)
        template = {
            "form_template_id": form_template_id,
            "schema_id": import_payload.get("schema_id", "schema_v1_staff"),
            "schema_version": import_payload.get("schema_version", "1.0.0"),
            "schema_json": import_payload.get("schema_json", {}),
        }
        self.state.form_templates.append(template)
        item_payloads = import_payload.get("items") or [{"field_key": "markdown", "field_value": markdown}]
        item_records = [
            {
                "work_record_item_id": f"mock-work-record-item-{len(self.state.work_record_items) + index}",
                "work_record_id": work_record_id,
                "field_key": str(item.get("field_key", f"item_{index}")) if isinstance(item, dict) else f"item_{index}",
                "field_value": item.get("field_value", item) if isinstance(item, dict) else item,
            }
            for index, item in enumerate(item_payloads, start=1)
        ]
        record = {
            "work_record_id": work_record_id,
            "form_template_id": form_template_id,
            "work_record_item_ids": [item["work_record_item_id"] for item in item_records],
            "storage_mode": "formal",
            "storage_table": "work_records",
            "identity": identity.to_dict(),
            "context": runtime_context or {},
            "status": "submitted",
            "source": "markdown_import",
            "markdown": markdown,
            "report": {
                "work_record_id": work_record_id,
                "submitted_by": import_payload.get("submitted_by", identity.user_id),
                "report_date": import_payload.get("report_date"),
                "task_count": import_payload.get("task_count", 0),
                "need_support": import_payload.get("need_support", False),
                "risk_level": import_payload.get("risk_level", "low"),
                "items": import_payload.get("items", []),
                "meta": import_payload.get("meta", {}),
            },
        }
        self.state.work_records.append(record)
        self.state.work_record_items.extend(item_records)
        audit_log_id = self._append_audit_log("import_staff_daily_report_from_markdown", "work_records", work_record_id, record)
        return ApiResponse(
            status_code=200,
            code=200,
            data={
                "form_template_id": form_template_id,
                "work_record_id": work_record_id,
                "work_record_item_ids": record["work_record_item_ids"],
                "work_record": record["report"],
                "audit_log_id": audit_log_id,
                "record": record,
            },
            msg="mock staff daily report imported",
        )

    def read_staff_daily_report(
        self,
        work_record_id: str,
        output_format: str = "json",
        identity: AgentIdentity | None = None,
    ) -> ApiResponse:
        _ = identity
        record = self._find_work_record(work_record_id)
        if record is None:
            return ApiResponse(status_code=404, code=404, data={}, msg="mock work record not found")
        items = [item for item in self.state.work_record_items if str(item.get("work_record_id")) == str(work_record_id)]
        if output_format == "markdown":
            data = {"work_record_id": work_record_id, "markdown": record.get("markdown", "")}
        else:
            data = {
                "work_record_id": work_record_id,
                "work_record": record.get("report", {}),
                "work_record_items": items,
                "report": record.get("report", {}),
            }
        return ApiResponse(status_code=200, code=200, data=data, msg="mock staff daily report loaded")

    def fetch_work_records(
        self,
        identity: AgentIdentity,
        *,
        department_id: str | None = None,
        record_date_from: str | None = None,
        record_date_to: str | None = None,
        status: str | None = "submitted",
        limit: int = 20,
        cursor: str | None = None,
    ) -> ApiResponse:
        target_department_id = department_id or identity.department_id
        all_records = [*self.state.staff_reports, *self.state.work_records]
        records = [
            record
            for record in all_records
            if record["identity"].get("department_id") == target_department_id and (status is None or record.get("status") == status)
        ]
        return ApiResponse(
            status_code=200,
            code=200,
            data={
                "items": records[:limit],
                "pagination": {"page": 1, "page_size": limit, "total": len(records), "has_more": False},
                "next_cursor": None,
                "has_more": False,
            },
            msg="mock work records fetched",
        )

    def fetch_tasks(self, identity: AgentIdentity, status: str | None = None) -> ApiResponse:
        tasks = [task for task in self.state.task_queue if task.get("assignee_user_id") in {identity.user_id, None}]
        if status:
            tasks = [task for task in tasks if task.get("status") == status]
        return ApiResponse(
            status_code=200,
            code=200,
            data={
                "items": tasks,
                "tasks": tasks,
                "pagination": {"page": 1, "page_size": len(tasks), "total": len(tasks), "has_more": False},
            },
            msg="mock tasks fetched",
        )

    def update_task(
        self,
        identity: AgentIdentity,
        task_id: str,
        *,
        status: str | None = None,
        title: str | None = None,
        description: str | None = None,
        task_payload: dict[str, Any] | None = None,
    ) -> ApiResponse:
        for task in self.state.task_queue:
            if str(task.get("task_id") or task.get("task_queue_id")) != str(task_id):
                continue
            if status is not None:
                task["status"] = status
            if title is not None:
                task["title"] = title
            if description is not None:
                task["description"] = description
            if task_payload is not None:
                task.update(task_payload)
            audit_log_id = self._append_audit_log("update_task", "task_queue", str(task_id), task)
            return ApiResponse(status_code=200, code=200, data={"task": task, "audit_log_id": audit_log_id}, msg="mock task updated")
        return ApiResponse(status_code=404, code=404, data={"task_id": task_id}, msg="mock task not found")

    def create_task(
        self,
        identity: AgentIdentity,
        task_payload: dict[str, Any],
        runtime_context: dict[str, Any] | None = None,
    ) -> ApiResponse:
        task_id = f"mock-task-{len(self.state.task_queue) + 1}"
        task = {"task_queue_id": task_id, "task_id": task_id, "storage_table": "task_queue", "status": "pending", **task_payload}
        self.state.task_queue.append(task)
        audit_log_id = self._append_audit_log("create_task", "task_queue", task_id, task)
        return ApiResponse(status_code=200, code=200, data={"task": task, "audit_log_id": audit_log_id, "context": runtime_context or {}}, msg="mock task created")

    def post_manager_report(
        self,
        identity: AgentIdentity,
        report_payload: dict[str, Any],
        runtime_context: dict[str, Any] | None = None,
    ) -> ApiResponse:
        summary_id = f"mock-summary-{len(self.state.manager_reports) + 1}"
        manager_report_id = f"mock-manager-report-{len(self.state.manager_reports) + 1}"
        record = {
            "manager_report_id": manager_report_id,
            "summary_id": summary_id,
            "storage_mode": "snapshot",
            "storage_table": "manager_reports",
            "identity": identity.to_dict(),
            "context": runtime_context or {},
            "report": report_payload,
        }
        self.state.manager_reports.append(record)
        audit_log_id = self._append_audit_log("post_manager_report", "manager_reports", manager_report_id, record)
        return ApiResponse(
            status_code=200,
            code=200,
            data={
                "manager_report_id": manager_report_id,
                "summary_id": summary_id,
                "source_link_count": len(report_payload.get("source_record_ids", [])),
                "decision_candidate_count": len(report_payload.get("need_executive_decision", [])),
                "audit_log_id": audit_log_id,
                "created_decision_candidate_ids": [],
                "created_task_ids": [],
                "record": record,
            },
            msg="mock manager report saved",
        )

    def commit_decision(
        self,
        identity: AgentIdentity,
        decision_payload: dict[str, Any],
        runtime_context: dict[str, Any] | None = None,
    ) -> ApiResponse:
        decision_id = f"mock-decision-{len(self.state.decision_logs) + 1}"
        agent_decision_log_id = f"mock-agent-decision-log-{len(self.state.agent_decision_logs) + 1}"
        decision_record = {
            "agent_decision_log_id": agent_decision_log_id,
            "decision_id": decision_id,
            "storage_table": "agent_decision_logs",
            "identity": identity.to_dict(),
            "context": runtime_context or {},
            "decision": decision_payload,
        }
        self.state.agent_decision_logs.append(decision_record)
        self.state.decision_logs.append(decision_record)
        generated_task_ids: list[str] = []
        for task in decision_payload.get("task_candidates", []):
            task_id = str(task.get("task_id") or f"mock-task-{len(self.state.task_queue) + 1}")
            generated_task_ids.append(task_id)
            task_record = {"task_queue_id": task_id, "storage_table": "task_queue", "status": "pending", **task}
            task_record["task_id"] = task_id
            self.state.task_queue.append(task_record)
        audit_log_id = self._append_audit_log("commit_decision", "agent_decision_logs", agent_decision_log_id, decision_record)
        return ApiResponse(
            status_code=200,
            code=200,
            data={
                "agent_decision_log_id": agent_decision_log_id,
                "decision_id": decision_id,
                "confirm_status": "confirmed",
                "generated_task_ids": generated_task_ids,
                "audit_log_id": audit_log_id,
                "decision": decision_record,
                "task_queue": self.state.task_queue,
            },
            msg="mock decision committed",
        )

    def run_dream(self, identity: AgentIdentity, summary_id: str) -> ApiResponse:
        return ApiResponse(
            status_code=200,
            code=200,
            data={
                "summary_id": summary_id,
                "identity": identity.to_dict(),
                "decision_options": [
                    {
                        "option_id": "A",
                        "title": "Conservative execution plan",
                        "summary": "Prioritize confirmed tasks and reduce execution risk.",
                        "task_candidates": [
                            {
                                "task_id": f"mock-dream-{summary_id}-A-1",
                                "title": "Review summary risks",
                                "description": "Validate top risks before scaling execution.",
                                "status": "pending",
                                "priority": "high",
                                "source_summary_id": summary_id,
                            }
                        ],
                    },
                    {
                        "option_id": "B",
                        "title": "Aggressive execution plan",
                        "summary": "Prioritize high-impact opportunities and resource reallocation.",
                        "task_candidates": [
                            {
                                "task_id": f"mock-dream-{summary_id}-B-1",
                                "title": "Accelerate summary actions",
                                "description": "Push follow-up actions while monitoring execution risk.",
                                "status": "pending",
                                "priority": "medium",
                                "source_summary_id": summary_id,
                            }
                        ],
                    },
                ],
                "contract_status": "mock_dream_generated",
            },
            msg="mock dream decision draft generated",
        )

    def _extract_markdown(self, import_payload: dict[str, Any]) -> str:
        markdown = import_payload.get("markdown") or import_payload.get("markdown_text")
        if markdown:
            return str(markdown)
        markdown_base64 = import_payload.get("markdown_base64")
        if markdown_base64:
            return base64.b64decode(str(markdown_base64)).decode("utf-8")
        return ""

    def _find_work_record(self, work_record_id: str) -> dict[str, Any] | None:
        for record in [*self.state.work_records, *self.state.staff_reports]:
            if str(record.get("work_record_id")) == str(work_record_id):
                return record
        return None

    def _next_work_record_id(self) -> str:
        return f"mock-work-record-{len(self.state.staff_reports) + len(self.state.work_records) + 1}"

    def _append_audit_log(self, action: str, table_name: str, record_id: str, payload: dict[str, Any]) -> str:
        audit_log_id = f"mock-audit-{len(self.state.audit_logs) + 1}"
        self.state.audit_logs.append(
            {
                "audit_log_id": audit_log_id,
                "action": action,
                "table_name": table_name,
                "record_id": record_id,
                "payload": payload,
            }
        )
        return audit_log_id
