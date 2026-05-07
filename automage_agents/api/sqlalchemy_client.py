from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session, sessionmaker

from automage_agents.api.models import ApiResponse
from automage_agents.core.models import AgentIdentity
from automage_agents.db.models import (
    AgentSessionModel,
    DecisionLogModel,
    ManagerReportModel,
    StaffReportModel,
    TaskQueueModel,
)


class SqlAlchemyAutoMageApiClient:
    def __init__(self, session_factory: sessionmaker[Session]):
        self.session_factory = session_factory

    def agent_init(self, identity: AgentIdentity, runtime_context: dict[str, Any] | None = None) -> ApiResponse:
        _ = runtime_context
        with self.session_factory.begin() as session:
            record = AgentSessionModel(
                node_id=identity.node_id,
                user_id=identity.user_id,
                role=identity.role.value,
                level=identity.level.value,
                department_id=identity.department_id,
                manager_node_id=identity.manager_node_id,
                metadata_json=dict(identity.metadata),
            )
            session.add(record)
        return ApiResponse(
            status_code=200,
            code=200,
            data={"auth_status": "active", "identity": identity.to_dict()},
            msg="database agent initialized",
        )

    def post_staff_report(
        self,
        identity: AgentIdentity,
        report_payload: dict[str, Any],
        runtime_context: dict[str, Any] | None = None,
    ) -> ApiResponse:
        _ = runtime_context
        with self.session_factory.begin() as session:
            record = StaffReportModel(
                node_id=identity.node_id,
                user_id=identity.user_id,
                role=identity.role.value,
                report_json=dict(report_payload),
            )
            session.add(record)
            session.flush()
            data = {
                "record": {
                    "id": record.id,
                    "identity": identity.to_dict(),
                    "report": report_payload,
                }
            }
        return ApiResponse(status_code=200, code=200, data=data, msg="staff report saved")

    def fetch_tasks(self, identity: AgentIdentity, status: str | None = None) -> ApiResponse:
        with self.session_factory() as session:
            query = session.query(TaskQueueModel).filter(
                (TaskQueueModel.assignee_user_id == identity.user_id) | (TaskQueueModel.assignee_user_id.is_(None))
            )
            if status:
                query = query.filter(TaskQueueModel.status == status)
            tasks = [
                {
                    "task_id": row.task_id,
                    "assignee_user_id": row.assignee_user_id,
                    "title": row.title,
                    "description": row.description,
                    "status": row.status,
                    **dict(row.task_payload or {}),
                }
                for row in query.order_by(TaskQueueModel.id.asc()).all()
            ]
        return ApiResponse(status_code=200, code=200, data={"tasks": tasks}, msg="tasks fetched")

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
        _ = identity
        with self.session_factory.begin() as session:
            row = session.query(TaskQueueModel).filter(TaskQueueModel.task_id == task_id).one_or_none()
            if row is None:
                return ApiResponse(status_code=404, code=404, data={"task_id": task_id}, msg="task not found")
            if status is not None:
                row.status = status
            if title is not None:
                row.title = title
            if description is not None:
                row.description = description
            if task_payload is not None:
                payload = dict(row.task_payload or {})
                payload.update(task_payload)
                row.task_payload = payload
            session.add(row)
            data = {
                "task": {
                    "task_id": row.task_id,
                    "assignee_user_id": row.assignee_user_id,
                    "title": row.title,
                    "description": row.description,
                    "status": row.status,
                    **dict(row.task_payload or {}),
                }
            }
        return ApiResponse(status_code=200, code=200, data=data, msg="task updated")

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
        _ = (identity, department_id, record_date_from, record_date_to, status, limit, cursor)
        return ApiResponse(status_code=200, code=200, data={"items": [], "reports": []}, msg="work records fetched")

    def post_manager_report(
        self,
        identity: AgentIdentity,
        report_payload: dict[str, Any],
        runtime_context: dict[str, Any] | None = None,
    ) -> ApiResponse:
        _ = runtime_context
        with self.session_factory.begin() as session:
            record = ManagerReportModel(
                node_id=identity.node_id,
                user_id=identity.user_id,
                role=identity.role.value,
                report_json=dict(report_payload),
            )
            session.add(record)
            session.flush()
            data = {
                "record": {
                    "id": record.id,
                    "identity": identity.to_dict(),
                    "report": report_payload,
                }
            }
        return ApiResponse(status_code=200, code=200, data=data, msg="manager report saved")

    def create_task(
        self,
        identity: AgentIdentity,
        task_payload: dict[str, Any],
        runtime_context: dict[str, Any] | None = None,
    ) -> ApiResponse:
        return self.commit_decision(identity, {"task_candidates": [task_payload]}, runtime_context)

    def commit_decision(
        self,
        identity: AgentIdentity,
        decision_payload: dict[str, Any],
        runtime_context: dict[str, Any] | None = None,
    ) -> ApiResponse:
        _ = runtime_context
        created_tasks: list[dict[str, Any]] = []
        with self.session_factory.begin() as session:
            decision = DecisionLogModel(
                node_id=identity.node_id,
                user_id=identity.user_id,
                role=identity.role.value,
                decision_json=dict(decision_payload),
            )
            session.add(decision)
            session.flush()

            for index, task in enumerate(decision_payload.get("task_candidates", []), start=1):
                task_id = str(task.get("task_id") or f"task-{decision.id}-{index}")
                row = TaskQueueModel(
                    task_id=task_id,
                    assignee_user_id=task.get("assignee_user_id"),
                    title=task.get("title"),
                    description=task.get("description"),
                    status=str(task.get("status") or "pending"),
                    task_payload=dict(task),
                )
                session.add(row)
                created_tasks.append(
                    {
                        "task_id": task_id,
                        "assignee_user_id": task.get("assignee_user_id"),
                        "title": task.get("title"),
                        "description": task.get("description"),
                        "status": str(task.get("status") or "pending"),
                        **dict(task),
                    }
                )

            data = {
                "decision": {
                    "id": decision.id,
                    "identity": identity.to_dict(),
                    "decision": decision_payload,
                },
                "task_queue": created_tasks,
            }
        return ApiResponse(status_code=200, code=200, data=data, msg="decision committed")

    def read_staff_daily_report(
        self,
        work_record_id: str,
        output_format: str = "json",
        identity: AgentIdentity | None = None,
    ) -> ApiResponse:
        _ = (output_format, identity)
        return ApiResponse(status_code=404, code=404, data={"work_record_id": work_record_id}, msg="not implemented")

    def import_staff_daily_report_from_markdown(
        self,
        identity: AgentIdentity,
        import_payload: dict[str, Any],
        runtime_context: dict[str, Any] | None = None,
    ) -> ApiResponse:
        _ = (identity, import_payload, runtime_context)
        return ApiResponse(status_code=501, code=501, data={}, msg="not implemented")

    def run_dream(self, identity: AgentIdentity, summary_id: str) -> ApiResponse:
        return ApiResponse(
            status_code=200,
            code=200,
            data={"summary_id": summary_id, "identity": identity.to_dict(), "decision_options": []},
            msg="database dream placeholder",
        )
