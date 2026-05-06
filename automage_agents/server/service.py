from __future__ import annotations

import base64
from typing import Any

from sqlalchemy.orm import Session

from automage_agents.config import load_runtime_settings
from automage_agents.core.enums import AgentLevel, AgentRole
from automage_agents.core.models import AgentIdentity
from automage_agents.db.models import (
    AgentSessionModel,
    DecisionLogModel,
    ManagerReportModel,
    StaffReportModel,
    TaskQueueModel,
)
from automage_agents.schemas.staff_daily_report_parser import (
    parse_staff_daily_report_bytes,
    parse_staff_daily_report_markdown,
)
from automage_agents.schemas.staff_daily_report_persistence import (
    StaffDailyReportPersistenceOptions,
    load_staff_daily_report,
    persist_staff_daily_report,
)
from automage_agents.server.audit import write_audit_log
from automage_agents.server.schemas import IdentityPayload


_settings = load_runtime_settings("configs/automage.local.toml")


def build_identity(payload: IdentityPayload) -> AgentIdentity:
    return AgentIdentity(
        node_id=payload.node_id,
        user_id=payload.user_id,
        role=AgentRole(payload.role),
        level=AgentLevel(payload.level),
        department_id=payload.department_id,
        manager_node_id=payload.manager_node_id,
        metadata=dict(payload.metadata),
    )


def create_agent_session(db: Session, identity: AgentIdentity, request_id: str | None = None) -> dict[str, Any]:
    record = AgentSessionModel(
        node_id=identity.node_id,
        user_id=identity.user_id,
        role=identity.role.value,
        level=identity.level.value,
        department_id=identity.department_id,
        manager_node_id=identity.manager_node_id,
        metadata_json=dict(identity.metadata),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    _audit_write(
        db,
        action="agent_init",
        target_type="agent_sessions",
        target_id=record.id,
        summary=f"Initialized agent session for {identity.user_id}",
        actor_user_id=_safe_int(identity.user_id),
        payload={"identity": identity.to_dict()},
        request_id=request_id,
    )
    db.commit()
    return {
        "id": record.id,
        "auth_status": "active",
        "identity": identity.to_dict(),
    }


def create_staff_report(
    db: Session, identity: AgentIdentity, report: dict[str, Any], request_id: str | None = None
) -> dict[str, Any]:
    record = StaffReportModel(
        node_id=identity.node_id,
        user_id=identity.user_id,
        role=identity.role.value,
        report_json=dict(report),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    _audit_write(
        db,
        action="create_staff_report",
        target_type="staff_reports",
        target_id=record.id,
        summary=f"Created staff report for {identity.user_id}",
        actor_user_id=_safe_int(identity.user_id),
        payload={"identity": identity.to_dict(), "report": report},
        request_id=request_id,
    )
    db.commit()
    return {"id": record.id, "identity": identity.to_dict(), "report": report}


def create_manager_report(
    db: Session, identity: AgentIdentity, report: dict[str, Any], request_id: str | None = None
) -> dict[str, Any]:
    record = ManagerReportModel(
        node_id=identity.node_id,
        user_id=identity.user_id,
        role=identity.role.value,
        report_json=dict(report),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    _audit_write(
        db,
        action="create_manager_report",
        target_type="manager_reports",
        target_id=record.id,
        summary=f"Created manager report for {identity.user_id}",
        actor_user_id=_safe_int(identity.user_id),
        payload={"identity": identity.to_dict(), "report": report},
        request_id=request_id,
    )
    db.commit()
    return {"id": record.id, "identity": identity.to_dict(), "report": report}


def commit_decision(
    db: Session, identity: AgentIdentity, decision: dict[str, Any], request_id: str | None = None
) -> dict[str, Any]:
    decision_record = DecisionLogModel(
        node_id=identity.node_id,
        user_id=identity.user_id,
        role=identity.role.value,
        decision_json=dict(decision),
    )
    db.add(decision_record)
    db.flush()

    tasks: list[dict[str, Any]] = []
    for index, task in enumerate(decision.get("task_candidates", []), start=1):
        task_id = str(task.get("task_id") or f"task-{decision_record.id}-{index}")
        row = TaskQueueModel(
            task_id=task_id,
            assignee_user_id=task.get("assignee_user_id"),
            title=task.get("title"),
            description=task.get("description"),
            status=str(task.get("status") or "pending"),
            task_payload=dict(task),
        )
        db.add(row)
        tasks.append(
            {
                "task_id": task_id,
                "assignee_user_id": row.assignee_user_id,
                "title": row.title,
                "description": row.description,
                "status": row.status,
            }
        )

    db.commit()
    _audit_write(
        db,
        action="commit_decision",
        target_type="agent_decision_logs",
        target_id=decision_record.id,
        summary=f"Committed decision for {identity.user_id}",
        actor_user_id=_safe_int(identity.user_id),
        payload={"identity": identity.to_dict(), "decision": decision, "task_count": len(tasks)},
        request_id=request_id,
    )
    db.commit()
    return {
        "decision": {
            "id": decision_record.id,
            "identity": identity.to_dict(),
            "decision": decision,
        },
        "task_queue": tasks,
    }


def list_tasks(db: Session, user_id: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
    query = db.query(TaskQueueModel)
    if user_id:
        query = query.filter(
            (TaskQueueModel.assignee_user_id == user_id) | (TaskQueueModel.assignee_user_id.is_(None))
        )
    if status:
        query = query.filter(TaskQueueModel.status == status)
    rows = query.order_by(TaskQueueModel.id.asc()).all()
    return [
        {
            "id": row.id,
            "task_id": row.task_id,
            "assignee_user_id": row.assignee_user_id,
            "title": row.title,
            "description": row.description,
            "status": row.status,
            "task_payload": row.task_payload,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
        for row in rows
    ]


def import_staff_daily_report_from_markdown(
    db: Session,
    *,
    markdown: str | None,
    markdown_base64: str | None,
    org_id: int,
    user_id: int,
    department_id: int | None,
    created_by: int | None,
    include_staff_report_snapshot: bool,
    snapshot_identity: dict[str, str] | None,
    include_source_markdown: bool,
    request_id: str | None = None,
) -> dict[str, Any]:
    if markdown_base64:
        raw = base64.b64decode(markdown_base64)
        report = parse_staff_daily_report_bytes(raw, include_source_markdown=include_source_markdown)
    else:
        report = parse_staff_daily_report_markdown(markdown or "", include_source_markdown=include_source_markdown)
    result = persist_staff_daily_report(
        db,
        report,
        options=StaffDailyReportPersistenceOptions(
            org_id=org_id,
            user_id=user_id,
            department_id=department_id,
            created_by=created_by or user_id,
            include_staff_report_snapshot=include_staff_report_snapshot,
            staff_report_identity=snapshot_identity,
        ),
    )
    _audit_write(
        db,
        action="import_staff_daily_report",
        target_type="work_records",
        target_id=result.work_record_id,
        summary=f"Imported staff daily report into work_record {result.work_record_id}",
        actor_user_id=created_by or user_id,
        payload={
            "work_record_id": result.work_record_id,
            "work_record_public_id": result.work_record_public_id,
            "template_id": result.template_id,
            "item_count": result.item_count,
            "staff_report_id": result.staff_report_id,
        },
        request_id=request_id,
    )
    db.commit()
    return {
        "template_id": result.template_id,
        "work_record_id": result.work_record_id,
        "work_record_public_id": result.work_record_public_id,
        "item_count": result.item_count,
        "staff_report_id": result.staff_report_id,
    }


def read_staff_daily_report(
    db: Session,
    *,
    work_record_id: int,
    output_format: str,
) -> dict[str, Any] | None:
    hydrated = load_staff_daily_report(db, work_record_id)
    if hydrated is None:
        return None
    payload: dict[str, Any] = {
        "work_record_id": hydrated.work_record_id,
        "work_record_public_id": hydrated.work_record_public_id,
        "format": output_format,
        "meta": hydrated.meta,
    }
    if output_format == "markdown":
        payload["markdown"] = hydrated.markdown
    else:
        payload["report"] = hydrated.report
    return payload


def _audit_write(
    db: Session,
    *,
    action: str,
    target_type: str,
    target_id: int,
    summary: str | None,
    actor_user_id: int | None,
    payload: dict[str, Any],
    request_id: str | None = None,
) -> None:
    if not _settings.audit_enabled:
        return
    final_payload = dict(payload)
    if request_id is not None:
        final_payload["request_id"] = request_id
    write_audit_log(
        db,
        org_id=_settings.audit_org_id,
        actor_user_id=actor_user_id,
        target_type=target_type,
        target_id=target_id,
        action=action,
        summary=summary,
        payload=final_payload,
    )


def _safe_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None
