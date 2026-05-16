from __future__ import annotations

import base64
from collections.abc import Iterable
from datetime import date, datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from automage_agents.config import load_runtime_settings
from automage_agents.core.enums import AgentLevel, AgentRole
from automage_agents.core.models import AgentIdentity
from automage_agents.db.models import (
    AgentSessionModel,
    AuditLogModel,
    DecisionLogModel,
    DecisionRecordModel,
    DepartmentModel,
    FormalDecisionLogModel,
    IncidentModel,
    IncidentUpdateModel,
    ManagerReportModel,
    OrganizationModel,
    StaffReportModel,
    SummaryModel,
    SummarySourceLinkModel,
    TaskAssignmentModel,
    TaskModel,
    TaskQueueModel,
    TaskUpdateModel,
    UserModel,
    WorkRecordModel,
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

UTC = timezone.utc

SUMMARY_SOURCE_TYPE_WORK_RECORD = 1
SUMMARY_SOURCE_TYPE_INCIDENT = 2

DECISION_ACTION_CREATED = 1
DECISION_ACTION_CONFIRMED = 2

DECISION_STATUS_DRAFT = 0
DECISION_STATUS_PENDING = 1
DECISION_STATUS_CONFIRMED = 2

TASK_STATUS_PENDING = 1
TASK_STATUS_IN_PROGRESS = 2
TASK_STATUS_DONE = 3
TASK_STATUS_CLOSED = 4

TASK_PRIORITY_HIGH = 1
TASK_PRIORITY_MEDIUM = 2
TASK_PRIORITY_LOW = 3

INCIDENT_STATUS_OPEN = 0
INCIDENT_STATUS_IN_PROGRESS = 1
INCIDENT_STATUS_RESOLVED = 2
INCIDENT_STATUS_CLOSED = 3

INCIDENT_SEVERITY_LOW = 1
INCIDENT_SEVERITY_MEDIUM = 2
INCIDENT_SEVERITY_HIGH = 3
INCIDENT_SEVERITY_CRITICAL = 4


class ConflictError(ValueError):
    pass


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
    db.flush()
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
    db.refresh(record)
    return {
        "id": record.id,
        "auth_status": "active",
        "identity": identity.to_dict(),
    }


def create_staff_report(
    db: Session,
    identity: AgentIdentity,
    report: dict[str, Any],
    request_id: str | None = None,
) -> dict[str, Any]:
    user = _resolve_user(db, identity.user_id)
    org = _resolve_org(db, report.get("org_id"), user=user)
    department = _resolve_department(db, report.get("department_id"), user=user, org=org, actor=identity)

    normalized_report = _normalize_staff_report_payload(identity, report, org=org, department=department, user=user)
    record_date = _coerce_date(normalized_report["legacy_projection"].get("record_date"))
    existing_work_record = _find_existing_staff_work_record(
        db,
        org_id=org.id,
        user_id=user.id,
        record_date=record_date,
    )
    if existing_work_record is not None:
        existing_payload = _load_staff_report_snapshot(db, existing_work_record)
        if _staff_report_payload_matches(existing_payload, normalized_report["legacy_projection"]):
            return _build_existing_staff_report_response(
                db,
                identity=identity,
                work_record=existing_work_record,
                fallback_report=normalized_report["legacy_projection"],
            )
        raise ConflictError("同一员工同一日期的日报已存在，且内容不一致")

    try:
        persisted = persist_staff_daily_report(
            db,
            normalized_report,
            options=StaffDailyReportPersistenceOptions(
                org_id=org.id,
                user_id=user.id,
                department_id=department.id if department is not None else None,
                created_by=user.id,
                include_staff_report_snapshot=True,
                staff_report_identity={
                    "node_id": identity.node_id,
                    "user_id": identity.user_id,
                    "role": identity.role.value,
                },
            ),
        )
    except IntegrityError:
        db.rollback()
        existing_work_record = _find_existing_staff_work_record(
            db,
            org_id=org.id,
            user_id=user.id,
            record_date=record_date,
        )
        if existing_work_record is None:
            raise
        existing_payload = _load_staff_report_snapshot(db, existing_work_record)
        if _staff_report_payload_matches(existing_payload, normalized_report["legacy_projection"]):
            return _build_existing_staff_report_response(
                db,
                identity=identity,
                work_record=existing_work_record,
                fallback_report=normalized_report["legacy_projection"],
            )
        raise ConflictError("同一员工同一日期的日报已存在，且内容不一致")
    work_record = db.get(WorkRecordModel, persisted.work_record_id)
    if work_record is not None and request_id is not None:
        work_record.meta = {
            **dict(work_record.meta or {}),
            "request_id": request_id,
        }
        db.add(work_record)

    created_incidents = _create_incidents_for_report(
        db,
        identity=identity,
        normalized_report=normalized_report,
        org=org,
        department=department,
        user=user,
        work_record_id=persisted.work_record_id,
    )

    _audit_write(
        db,
        action="create_staff_report",
        target_type="work_records",
        target_id=persisted.work_record_id,
        summary=f"Created staff report for {identity.user_id}",
        actor_user_id=user.id,
        payload={
            "identity": identity.to_dict(),
            "work_record_id": persisted.work_record_id,
            "work_record_public_id": persisted.work_record_public_id,
            "staff_report_id": persisted.staff_report_id,
            "incident_ids": [item["incident_id"] for item in created_incidents],
        },
        request_id=request_id,
    )
    db.commit()

    return {
        "work_record_id": persisted.work_record_id,
        "work_record_public_id": persisted.work_record_public_id,
        "staff_report_id": persisted.staff_report_id,
        "incident_ids": [item["incident_id"] for item in created_incidents],
        "created_incidents": created_incidents,
        "identity": identity.to_dict(),
        "report": normalized_report["legacy_projection"],
    }


def create_manager_report(
    db: Session,
    identity: AgentIdentity,
    report: dict[str, Any],
    request_id: str | None = None,
) -> dict[str, Any]:
    manager = _resolve_user(db, identity.user_id)
    org = _resolve_org(db, report.get("org_id"), user=manager)
    department = _resolve_department(
        db,
        report.get("dept_id") or report.get("department_id"),
        user=manager,
        org=org,
        actor=identity,
    )
    summary_date = _coerce_date(report.get("summary_date")) or date.today()
    summary_meta = {
        "schema_id": report.get("schema_id", "schema_v1_manager"),
        "schema_version": report.get("schema_version", "1.0.0"),
        "overall_health": report.get("overall_health"),
        "pending_approvals": report.get("pending_approvals", 0),
        "staff_report_count": report.get("staff_report_count", 0),
        "missing_report_count": report.get("missing_report_count", 0),
        "need_executive_decision": bool(report.get("pending_approvals") or report.get("need_executive_decision")),
        "top_3_risks": list(report.get("top_3_risks") or []),
        "source_record_ids": list(report.get("source_record_ids") or []),
        "signature": dict(report.get("signature") or {}),
    }

    summary = SummaryModel(
        public_id=_public_id("SUM"),
        org_id=org.id,
        department_id=department.id if department is not None else None,
        user_id=None,
        summary_type=1,
        scope_type=2,
        summary_date=summary_date,
        week_start=_coerce_date(report.get("week_start")),
        status=1,
        title=str(report.get("title") or f"Manager Summary {summary_date.isoformat()}"),
        content=report.get("aggregated_summary") or report.get("summary") or "",
        source_count=0,
        generated_by_type=2,
        created_by=manager.id,
        updated_by=manager.id,
        meta=summary_meta,
    )
    db.add(summary)
    db.flush()

    source_links = _resolve_summary_source_links(
        db,
        org=org,
        department=department,
        summary=summary,
        report=report,
        summary_date=summary_date,
    )
    summary.source_count = len(source_links)
    db.add(summary)

    snapshot = ManagerReportModel(
        node_id=identity.node_id,
        user_id=identity.user_id,
        role=identity.role.value,
        report_json={
            "schema_id": report.get("schema_id", "schema_v1_manager"),
            "schema_version": report.get("schema_version", "1.0.0"),
            "org_id": report.get("org_id"),
            "dept_id": report.get("dept_id") or report.get("department_id"),
            "manager_user_id": identity.user_id,
            "manager_node_id": identity.node_id,
            "summary_date": summary_date.isoformat(),
            "aggregated_summary": summary.content,
            "overall_health": report.get("overall_health"),
            "top_3_risks": list(report.get("top_3_risks") or []),
            "pending_approvals": report.get("pending_approvals", 0),
            "source_record_ids": list(report.get("source_record_ids") or []),
            "summary_public_id": summary.public_id,
        },
    )
    db.add(snapshot)
    db.flush()

    _audit_write(
        db,
        action="create_manager_report",
        target_type="summaries",
        target_id=summary.id,
        summary=f"Created manager summary for {identity.user_id}",
        actor_user_id=manager.id,
        payload={
            "identity": identity.to_dict(),
            "summary_id": summary.id,
            "summary_public_id": summary.public_id,
            "source_count": summary.source_count,
            "manager_report_snapshot_id": snapshot.id,
        },
        request_id=request_id,
    )
    db.commit()

    return {
        "summary_id": summary.id,
        "summary_public_id": summary.public_id,
        "source_count": summary.source_count,
        "manager_report_snapshot_id": snapshot.id,
        "identity": identity.to_dict(),
        "report": snapshot.report_json,
    }


def list_staff_reports(
    db: Session,
    *,
    org_id: str | None = None,
    department_id: str | None = None,
    record_date: str | None = None,
    user_id: str | None = None,
) -> list[dict[str, Any]]:
    org = _try_resolve_org(db, org_id)
    department = _try_resolve_department(db, department_id, org=org)
    user = _try_resolve_user(db, user_id)
    target_date = _coerce_date(record_date)

    query = db.query(WorkRecordModel).filter(WorkRecordModel.deleted_at.is_(None))
    if org is not None:
        query = query.filter(WorkRecordModel.org_id == org.id)
    if department is not None:
        query = query.filter(WorkRecordModel.department_id == department.id)
    if user is not None:
        query = query.filter(WorkRecordModel.user_id == user.id)
    if target_date is not None:
        query = query.filter(WorkRecordModel.record_date == target_date)

    rows = query.order_by(WorkRecordModel.record_date.desc(), WorkRecordModel.id.desc()).all()
    users = _load_usernames_by_ids(db, [row.user_id for row in rows])
    reports: list[dict[str, Any]] = []
    for row in rows:
        hydrated = load_staff_daily_report(db, row.id)
        if hydrated is None:
            continue
        legacy = dict(hydrated.report.get("legacy_projection") or {})
        legacy.setdefault("schema_id", "schema_v1_staff")
        legacy["org_id"] = org_id or _org_label(org, row.org_id)
        legacy["department_id"] = department_id or _department_label(department, row.department_id)
        legacy["record_date"] = row.record_date.isoformat()
        legacy["user_id"] = users.get(row.user_id, str(row.user_id))
        snapshot_user_id = users.get(row.user_id, str(row.user_id))
        reports.append(
            {
                "id": row.id,
                "node_id": _snapshot_node_id(hydrated.meta, snapshot_user_id),
                "user_id": snapshot_user_id,
                "role": "staff",
                "report": legacy,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "work_record_id": row.id,
                "work_record_public_id": row.public_id,
            }
        )
    return reports


def list_manager_reports(
    db: Session,
    *,
    org_id: str | None = None,
    summary_date: str | None = None,
    dept_id: str | None = None,
    manager_user_id: str | None = None,
) -> list[dict[str, Any]]:
    rows = db.query(ManagerReportModel).order_by(ManagerReportModel.id.desc()).all()

    reports: list[dict[str, Any]] = []
    for row in rows:
        report = dict(row.report_json or {})
        if org_id is not None and str(report.get("org_id") or "") != str(org_id):
            continue
        row_dept_id = report.get("dept_id", report.get("department_id"))
        if dept_id is not None and str(row_dept_id or "") != str(dept_id):
            continue
        if summary_date is not None and str(report.get("summary_date") or "") != str(summary_date):
            continue
        row_manager_user_id = str(report.get("manager_user_id") or row.user_id or "")
        if manager_user_id is not None and row_manager_user_id != str(manager_user_id):
            continue
        reports.append(
            {
                "id": row.id,
                "node_id": row.node_id,
                "user_id": row.user_id,
                "role": row.role,
                "report": report,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "summary_id": report.get("summary_id"),
                "summary_public_id": report.get("summary_public_id"),
            }
        )
    return reports


def commit_decision(
    db: Session,
    identity: AgentIdentity,
    decision: dict[str, Any],
    request_id: str | None = None,
) -> dict[str, Any]:
    owner = _resolve_user(db, identity.user_id)
    org = _resolve_org(db, decision.get("org_id"), user=owner)
    department = _resolve_department(db, decision.get("department_id"), user=owner, org=org, actor=identity)
    source_summary = _try_resolve_summary(db, decision.get("summary_id") or decision.get("source_summary_id"), org=org)
    source_record = _try_resolve_work_record(db, decision.get("source_record_id"), org=org)

    selected_option_key = str(
        decision.get("selected_option_id")
        or decision.get("selected_option_key")
        or decision.get("selected_option")
        or ""
    ).strip() or None
    selected_option_label = decision.get("selected_option_label")
    confirmed = selected_option_key is not None

    option_schema = _build_decision_option_schema(decision)
    record = DecisionRecordModel(
        public_id=_public_id("DEC"),
        org_id=org.id,
        department_id=department.id if department is not None else None,
        source_record_id=source_record.id if source_record is not None else None,
        source_summary_id=source_summary.id if source_summary is not None else None,
        related_task_id=None,
        related_incident_id=None,
        requester_user_id=owner.id,
        decision_owner_user_id=owner.id,
        title=str(decision.get("title") or "Executive Decision"),
        description=decision.get("decision_summary") or decision.get("description"),
        decision_type=1,
        status=DECISION_STATUS_CONFIRMED if confirmed else DECISION_STATUS_PENDING,
        priority=_map_priority(decision.get("priority")),
        option_schema_json=option_schema,
        selected_option_key=selected_option_key,
        selected_option_label=selected_option_label,
        decision_comment=decision.get("comment"),
        due_at=_coerce_datetime(decision.get("due_at")),
        decided_at=_now() if confirmed else None,
        closed_at=None,
        created_by=owner.id,
        updated_by=owner.id,
        meta={
            "identity": identity.to_dict(),
            "decision_payload": dict(decision),
        },
    )
    db.add(record)
    db.flush()

    created_log = FormalDecisionLogModel(
        org_id=org.id,
        decision_record_id=record.id,
        actor_user_id=owner.id,
        action_type=DECISION_ACTION_CREATED,
        status_before=None,
        status_after=record.status,
        selected_option_key=None,
        selected_option_label=None,
        comment="Decision record created",
        payload={"request_id": request_id, "stage": "created"},
    )
    db.add(created_log)

    if confirmed:
        confirm_log = FormalDecisionLogModel(
            org_id=org.id,
            decision_record_id=record.id,
            actor_user_id=owner.id,
            action_type=DECISION_ACTION_CONFIRMED,
            status_before=DECISION_STATUS_PENDING,
            status_after=record.status,
            selected_option_key=selected_option_key,
            selected_option_label=selected_option_label,
            comment=decision.get("comment") or decision.get("decision_summary"),
            payload={"request_id": request_id, "stage": "confirmed"},
        )
        db.add(confirm_log)

    snapshot = DecisionLogModel(
        node_id=identity.node_id,
        user_id=identity.user_id,
        role=identity.role.value,
        decision_json=dict(decision),
    )
    db.add(snapshot)
    db.flush()

    created_tasks: list[dict[str, Any]] = []
    if confirmed:
        for task in decision.get("task_candidates", []):
            task_payload = dict(task)
            task_payload.setdefault("org_id", org.public_id)
            task_payload.setdefault("department_id", department.public_id if department is not None else None)
            task_payload.setdefault("source_id", source_record.public_id if source_record is not None else None)
            prepared_task = _prepare_task_record_payload(
                db,
                task=task_payload,
                request_id=request_id,
                creator_user=owner,
                org=org,
                department=department,
                decision_record=record,
            )
            created = _create_task_records(
                db,
                prepared_task=prepared_task,
            )
            created_tasks.append(created)

    _audit_write(
        db,
        action="commit_decision",
        target_type="decision_records",
        target_id=record.id,
        summary=f"Committed decision for {identity.user_id}",
        actor_user_id=owner.id,
        payload={
            "identity": identity.to_dict(),
            "decision_record_id": record.id,
            "decision_public_id": record.public_id,
            "task_ids": [task["task_id"] for task in created_tasks],
        },
        request_id=request_id,
    )
    db.commit()

    return {
        "decision": {
            "decision_record_id": record.id,
            "decision_record_public_id": record.public_id,
            "identity": identity.to_dict(),
            "decision": dict(decision),
        },
        "task_ids": [task["task_id"] for task in created_tasks],
        "tasks": created_tasks,
        "snapshot_id": snapshot.id,
    }


def create_tasks(
    db: Session,
    *,
    tasks: list[dict[str, Any]],
    request_id: str | None = None,
) -> list[dict[str, Any]]:
    created: list[dict[str, Any]] = []
    for task in tasks:
        creator = _resolve_user(db, str(task.get("creator_user_id"))) if task.get("creator_user_id") else _first_user(db)
        org = _resolve_org(db, task.get("org_id"), user=creator)
        department = _resolve_department(db, task.get("department_id"), user=creator, org=org, actor=None)
        decision_record = _try_resolve_decision_record(
            db,
            task.get("source_decision_id") or task.get("decision_record_id"),
            org=org,
        )
        prepared_task = _prepare_task_record_payload(
            db,
            task=dict(task),
            request_id=request_id,
            creator_user=creator,
            org=org,
            department=department,
            decision_record=decision_record,
        )
        existing_task = db.query(TaskModel).filter(TaskModel.public_id == prepared_task["public_id"]).one_or_none()
        if existing_task is not None:
            existing_assignment = (
                db.query(TaskAssignmentModel)
                .filter(TaskAssignmentModel.task_id == existing_task.id)
                .order_by(TaskAssignmentModel.id.asc())
                .first()
            )
            if not _task_create_matches_existing(
                existing_task,
                existing_assignment,
                prepared_task=prepared_task,
            ):
                raise ConflictError(f"任务 {prepared_task['public_id']} 已存在，且请求内容不一致")
            users = _load_usernames_by_ids(
                db,
                [
                    existing_task.creator_user_id,
                    existing_assignment.user_id if existing_assignment is not None else None,
                ],
            )
            created.append(_serialize_task(existing_task, existing_assignment, users))
            continue
        created.append(
            _create_task_records(
                db,
                prepared_task=prepared_task,
            )
        )
    db.commit()
    return created


def list_tasks(
    db: Session,
    user_id: str | None = None,
    status: str | None = None,
    assignee_user_id: str | None = None,
) -> list[dict[str, Any]]:
    assignee = _try_resolve_user(db, assignee_user_id or user_id)
    query = db.query(TaskModel).filter(TaskModel.deleted_at.is_(None))
    if status is not None:
        query = query.filter(TaskModel.status == _map_task_status(status))
    rows = query.order_by(TaskModel.id.asc()).all()

    assignments = db.query(TaskAssignmentModel).filter(
        TaskAssignmentModel.task_id.in_([row.id for row in rows] or [-1])
    ).all()
    assignment_map = {row.task_id: row for row in assignments}
    users = _load_usernames_by_ids(
        db,
        [row.user_id for row in assignments] + [row.creator_user_id for row in rows if row.creator_user_id is not None],
    )

    tasks: list[dict[str, Any]] = []
    for row in rows:
        assignment = assignment_map.get(row.id)
        if assignee is not None and (assignment is None or assignment.user_id != assignee.id):
            continue
        tasks.append(_serialize_task(row, assignment, users))
    return tasks


def update_task(
    db: Session,
    *,
    task_id: str,
    status: str | None = None,
    title: str | None = None,
    description: str | None = None,
    task_payload: dict[str, Any] | None = None,
    request_id: str | None = None,
    actor_user_id: str | None = None,
) -> dict[str, Any] | None:
    row = get_task_by_task_id(db, task_id)
    if row is None:
        return None

    assignment = (
        db.query(TaskAssignmentModel)
        .filter(TaskAssignmentModel.task_id == row.id)
        .order_by(TaskAssignmentModel.id.asc())
        .first()
    )
    actor = _try_resolve_user(db, actor_user_id)
    previous_status = row.status

    if request_id is not None:
        existing_update = _find_task_update_by_request_id(db, task_row_id=row.id, request_id=request_id)
        if existing_update is not None:
            if not _task_update_payload_matches(
                existing_update,
                status=status,
                title=title,
                description=description,
                task_payload=task_payload,
            ):
                raise ConflictError(f"任务 {task_id} 的相同 request_id 更新内容不一致")
            users = _load_usernames_by_ids(
                db,
                [
                    assignment.user_id if assignment is not None else None,
                    row.creator_user_id,
                ],
            )
            return _serialize_task(row, assignment, users)

    if _task_update_is_noop(
        row,
        status=status,
        title=title,
        description=description,
        task_payload=task_payload,
    ):
        users = _load_usernames_by_ids(
            db,
            [
                assignment.user_id if assignment is not None else None,
                row.creator_user_id,
            ],
        )
        return _serialize_task(row, assignment, users)

    if status is not None:
        row.status = _map_task_status(status)
        if row.status == TASK_STATUS_IN_PROGRESS and row.started_at is None:
            row.started_at = _now()
        if row.status in {TASK_STATUS_DONE, TASK_STATUS_CLOSED} and previous_status not in {
            TASK_STATUS_DONE,
            TASK_STATUS_CLOSED,
        }:
            row.closed_at = _now()
    if title is not None:
        row.title = title
    if description is not None:
        row.description = description
    if task_payload is not None:
        merged_payload = dict(row.meta or {})
        merged_payload.update(task_payload)
        row.meta = merged_payload
    if actor is not None:
        row.updated_by = actor.id

    db.add(row)
    db.flush()

    update_record = TaskUpdateModel(
        org_id=row.org_id,
        task_id=row.id,
        request_id=request_id,
        actor_user_id=actor.id if actor is not None else None,
        update_type=1,
        content=description or title,
        status_before=previous_status,
        status_after=row.status,
        meta={
            "request_id": request_id,
            "status": status,
            "title": title,
            "description": description,
            "task_payload": dict(task_payload or {}),
        },
    )
    db.add(update_record)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        row = get_task_by_task_id(db, task_id)
        if row is None:
            raise
        assignment = (
            db.query(TaskAssignmentModel)
            .filter(TaskAssignmentModel.task_id == row.id)
            .order_by(TaskAssignmentModel.id.asc())
            .first()
        )
        if request_id is not None:
            existing_update = _find_task_update_by_request_id(db, task_row_id=row.id, request_id=request_id)
            if existing_update is not None:
                if not _task_update_payload_matches(
                    existing_update,
                    status=status,
                    title=title,
                    description=description,
                    task_payload=task_payload,
                ):
                    raise ConflictError(f"任务 {task_id} 的相同 request_id 更新内容不一致")
                users = _load_usernames_by_ids(
                    db,
                    [
                        assignment.user_id if assignment is not None else None,
                        row.creator_user_id,
                    ],
                )
                return _serialize_task(row, assignment, users)
        raise

    if status is not None:
        queue_row = db.query(TaskQueueModel).filter(TaskQueueModel.task_id == row.public_id).one_or_none()
        if queue_row is not None:
            queue_row.status = status
            db.add(queue_row)

    _audit_write(
        db,
        action="update_task",
        target_type="tasks",
        target_id=row.id,
        summary=f"Updated task {row.public_id}",
        actor_user_id=actor.id if actor is not None else None,
        payload={
            "task_id": task_id,
            "status": status,
            "title": title,
            "description": description,
            "task_payload": task_payload,
        },
        request_id=request_id,
    )
    db.commit()

    users = _load_usernames_by_ids(
        db,
        [
            assignment.user_id if assignment is not None else None,
            row.creator_user_id,
        ],
    )
    return _serialize_task(row, assignment, users)


def get_task_by_task_id(db: Session, task_id: str) -> TaskModel | None:
    row = db.query(TaskModel).filter(TaskModel.public_id == task_id, TaskModel.deleted_at.is_(None)).one_or_none()
    if row is not None:
        return row

    # Fallback for older or mixed payloads that still treat business task_id as the
    # external identifier while the formal task row may carry it only in meta.
    rows = (
        db.query(TaskModel)
        .filter(TaskModel.deleted_at.is_(None))
        .order_by(TaskModel.id.desc())
        .limit(500)
        .all()
    )
    for candidate in rows:
        meta = dict(candidate.meta or {})
        if str(meta.get("task_id") or "") == task_id:
            return candidate
    return None


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
    legacy = dict(hydrated.report.get("legacy_projection") or {})
    payload: dict[str, Any] = {
        "work_record_id": hydrated.work_record_id,
        "work_record_public_id": hydrated.work_record_public_id,
        "format": output_format,
        "meta": hydrated.meta,
        "user_id": legacy.get("user_id"),
        "department_id": legacy.get("department_id"),
    }
    if output_format == "markdown":
        payload["markdown"] = hydrated.markdown
    else:
        payload["report"] = hydrated.report
    return payload


def list_audit_logs(
    db: Session,
    *,
    target_type: str | None = None,
    actor_user_id: str | None = None,
    started_at: str | None = None,
    ended_at: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    actor = _try_resolve_user(db, actor_user_id)
    started = _coerce_datetime(started_at)
    ended = _coerce_datetime(ended_at)

    query = db.query(AuditLogModel).order_by(AuditLogModel.event_at.desc(), AuditLogModel.id.desc())
    if target_type is not None:
        query = query.filter(AuditLogModel.target_type == target_type)
    if actor is not None:
        query = query.filter(AuditLogModel.actor_user_id == actor.id)
    if started is not None:
        query = query.filter(AuditLogModel.event_at >= started)
    if ended is not None:
        query = query.filter(AuditLogModel.event_at <= ended)

    rows = query.limit(limit).all()
    user_ids = [row.actor_user_id for row in rows if row.actor_user_id is not None]
    usernames = _load_usernames_by_ids(db, user_ids)
    return [
        {
            "id": row.id,
            "org_id": row.org_id,
            "actor_user_id": usernames.get(row.actor_user_id, str(row.actor_user_id))
            if row.actor_user_id is not None
            else None,
            "target_type": row.target_type,
            "target_id": row.target_id,
            "action": row.action,
            "summary": row.summary,
            "payload": dict(row.payload or {}),
            "event_at": row.event_at.isoformat() if row.event_at else None,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
        for row in rows
    ]


def run_dream_from_summary(
    db: Session,
    *,
    summary_id: str,
    actor_identity: AgentIdentity,
    request_id: str | None = None,
) -> dict[str, Any]:
    actor = _resolve_user(db, actor_identity.user_id)
    summary = _resolve_summary(db, summary_id, org=None)
    meta = dict(summary.meta or {})
    decision_options = [
        {
            "option_id": "A",
            "title": "Conservative execution plan",
            "summary": "Prioritize risk control before broad execution.",
            "task_candidates": _build_dream_task_candidates(summary, actor_identity, conservative=True),
        },
        {
            "option_id": "B",
            "title": "Aggressive execution plan",
            "summary": "Push execution with tighter follow-up and faster feedback loops.",
            "task_candidates": _build_dream_task_candidates(summary, actor_identity, conservative=False),
        },
    ]
    _audit_write(
        db,
        action="dream_run",
        target_type="summaries",
        target_id=summary.id,
        summary=f"Generated dream draft for summary {summary.public_id}",
        actor_user_id=actor.id,
        payload={"summary_public_id": summary.public_id, "request_id": request_id},
        request_id=request_id,
    )
    db.commit()
    return {
        "summary_id": summary.id,
        "summary_public_id": summary.public_id,
        "contract_status": "pending_dream_confirmation",
        "manager_summary": {
            "title": summary.title,
            "content": summary.content,
            "summary_date": summary.summary_date.isoformat() if summary.summary_date else None,
            "overall_health": meta.get("overall_health"),
            "top_3_risks": list(meta.get("top_3_risks") or []),
        },
        "decision_options": decision_options,
    }


def _create_incidents_for_report(
    db: Session,
    *,
    identity: AgentIdentity,
    normalized_report: dict[str, Any],
    org: OrganizationModel,
    department: DepartmentModel | None,
    user: UserModel,
    work_record_id: int,
) -> list[dict[str, Any]]:
    if not _should_create_incident(normalized_report):
        return []

    blockers = list(normalized_report.get("today_blockers") or [])
    primary_blocker = blockers[0] if blockers else {}
    title = primary_blocker.get("issue_name") or "High risk staff report"
    description = primary_blocker.get("issue_description") or normalized_report["legacy_projection"].get(
        "issues_faced", "High risk reported by staff"
    )
    incident = IncidentModel(
        public_id=_public_id("INC"),
        org_id=org.id,
        department_id=department.id if department is not None else None,
        source_record_id=work_record_id,
        related_task_id=None,
        reporter_user_id=user.id,
        title=str(title),
        description=str(description),
        severity=_map_incident_severity(
            normalized_report.get("risk_assessment", {}).get("overall_risk_level")
            or normalized_report["legacy_projection"].get("risk_level")
        ),
        status=INCIDENT_STATUS_OPEN,
        created_by=user.id,
        updated_by=user.id,
        meta={
            "created_from": "staff_report",
            "needs_escalation": normalized_report.get("risk_assessment", {}).get("needs_escalation", False),
            "identity": identity.to_dict(),
        },
    )
    db.add(incident)
    db.flush()

    update_row = IncidentUpdateModel(
        org_id=org.id,
        incident_id=incident.id,
        actor_user_id=user.id,
        update_type=1,
        content="Incident created from staff report",
        status_before=None,
        status_after=INCIDENT_STATUS_OPEN,
        meta={"source_work_record_id": work_record_id},
    )
    db.add(update_row)
    return [
        {
            "incident_id": incident.id,
            "incident_public_id": incident.public_id,
            "title": incident.title,
            "severity": _incident_severity_to_text(incident.severity),
            "status": _incident_status_to_text(incident.status),
        }
    ]


def _resolve_summary_source_links(
    db: Session,
    *,
    org: OrganizationModel,
    department: DepartmentModel | None,
    summary: SummaryModel,
    report: dict[str, Any],
    summary_date: date,
) -> list[SummarySourceLinkModel]:
    links: list[SummarySourceLinkModel] = []
    source_records = list(report.get("source_record_ids") or [])
    resolved_work_records = [
        item
        for item in (_try_resolve_work_record(db, source_id, org=org) for source_id in source_records)
        if item is not None
    ]

    if not resolved_work_records:
        query = db.query(WorkRecordModel).filter(
            WorkRecordModel.org_id == org.id,
            WorkRecordModel.deleted_at.is_(None),
            WorkRecordModel.record_date == summary_date,
        )
        if department is not None:
            query = query.filter(WorkRecordModel.department_id == department.id)
        resolved_work_records = query.order_by(WorkRecordModel.id.asc()).all()

    source_public_ids: list[str] = []
    for work_record in resolved_work_records:
        link = SummarySourceLinkModel(
            org_id=org.id,
            summary_id=summary.id,
            source_type=SUMMARY_SOURCE_TYPE_WORK_RECORD,
            source_id=work_record.id,
        )
        db.add(link)
        links.append(link)
        source_public_ids.append(work_record.public_id)

    summary.meta = {
        **dict(summary.meta or {}),
        "source_record_ids": source_public_ids,
    }
    return links


def _create_task_records(
    db: Session,
    *,
    prepared_task: dict[str, Any],
) -> dict[str, Any]:
    assignee = prepared_task["assignee"]
    public_id = prepared_task["public_id"]
    status = prepared_task["status"]
    priority = prepared_task["priority"]
    title = prepared_task["title"]
    description = prepared_task["description"]
    source_record = prepared_task["source_record"]
    due_at = prepared_task["due_at"]
    task_meta = dict(prepared_task["task_meta"])
    request_id = prepared_task["request_id"]
    creator_user = prepared_task["creator_user"]
    org = prepared_task["org"]
    department = prepared_task["department"]
    decision_record = prepared_task["decision_record"]
    existing_task = db.query(TaskModel).filter(TaskModel.public_id == public_id).one_or_none()
    if existing_task is not None:
        existing_assignment = (
            db.query(TaskAssignmentModel)
            .filter(TaskAssignmentModel.task_id == existing_task.id)
            .order_by(TaskAssignmentModel.id.asc())
            .first()
        )
        if not _task_create_matches_existing(existing_task, existing_assignment, prepared_task=prepared_task):
            raise ConflictError(f"任务 {public_id} 已存在，且请求内容不一致")
        users = _load_usernames_by_ids(
            db,
            [
                existing_task.creator_user_id,
                existing_assignment.user_id if existing_assignment is not None else None,
            ],
        )
        return _serialize_task(existing_task, existing_assignment, users)

    task_row = TaskModel(
        public_id=public_id,
        org_id=org.id,
        department_id=department.id if department is not None else None,
        decision_record_id=decision_record.id if decision_record is not None else None,
        source_record_id=source_record.id if source_record is not None else None,
        creator_user_id=creator_user.id,
        title=title,
        description=description,
        status=status,
        priority=priority,
        due_at=due_at,
        started_at=_now() if status == TASK_STATUS_IN_PROGRESS else None,
        closed_at=_now() if status in {TASK_STATUS_DONE, TASK_STATUS_CLOSED} else None,
        created_by=creator_user.id,
        updated_by=creator_user.id,
        meta=task_meta,
    )
    db.add(task_row)
    db.flush()

    assignment_row: TaskAssignmentModel | None = None
    if assignee is not None:
        assignment_row = TaskAssignmentModel(
            org_id=org.id,
            task_id=task_row.id,
            user_id=assignee.id,
            assignment_type=1,
            created_by=creator_user.id,
        )
        db.add(assignment_row)
        db.flush()

    update_row = TaskUpdateModel(
        org_id=org.id,
        task_id=task_row.id,
        request_id=request_id,
        actor_user_id=creator_user.id,
        update_type=1,
        content=description,
        status_before=None,
        status_after=status,
        meta={
            "event": "task_created",
            "request_id": request_id,
            "status": _task_status_to_text(status),
            "title": title,
            "description": description,
            "task_payload": task_meta,
        },
    )
    db.add(update_row)

    queue_row = TaskQueueModel(
        task_id=public_id,
        assignee_user_id=assignee.username if assignee is not None else None,
        title=title,
        description=description,
        status=_task_status_to_text(status),
        task_payload=task_meta,
    )
    db.add(queue_row)

    _audit_write(
        db,
        action="create_task",
        target_type="tasks",
        target_id=task_row.id,
        summary=f"Created task {task_row.public_id}",
        actor_user_id=creator_user.id,
        payload={"task": task_meta, "request_id": request_id},
        request_id=request_id,
    )
    users = _load_usernames_by_ids(
        db,
        [creator_user.id, assignee.id if assignee is not None else None],
    )
    return _serialize_task(task_row, assignment_row, users)


def _prepare_task_record_payload(
    db: Session,
    *,
    task: dict[str, Any],
    request_id: str | None,
    creator_user: UserModel,
    org: OrganizationModel,
    department: DepartmentModel | None,
    decision_record: DecisionRecordModel | None,
) -> dict[str, Any]:
    assignee = _resolve_user(db, str(task.get("assignee_user_id"))) if task.get("assignee_user_id") else None
    public_id = str(task.get("task_id") or _public_id("TSK"))
    status = _map_task_status(task.get("status"))
    priority = _map_priority(task.get("priority"))
    title = str(task.get("task_title") or task.get("title") or "Generated Task")
    description = task.get("task_description") or task.get("description")
    source_record = _try_resolve_work_record(db, task.get("source_id"), org=org)
    due_at = _coerce_datetime(task.get("due_at"))

    task_meta = dict(task)
    if assignee is not None:
        task_meta["assignee_user_id"] = assignee.username
    if department is not None:
        task_meta.setdefault("department_id", department.public_id)
        task_meta.setdefault("department_numeric_id", department.id)
    task_meta.setdefault("org_id", org.public_id)
    task_meta.setdefault("org_numeric_id", org.id)

    return {
        "assignee": assignee,
        "public_id": public_id,
        "status": status,
        "priority": priority,
        "title": title,
        "description": description,
        "source_record": source_record,
        "due_at": due_at,
        "task_meta": task_meta,
        "request_id": request_id,
        "creator_user": creator_user,
        "org": org,
        "department": department,
        "decision_record": decision_record,
    }


def _task_create_matches_existing(
    existing_task: TaskModel,
    existing_assignment: TaskAssignmentModel | None,
    *,
    prepared_task: dict[str, Any],
) -> bool:
    expected_assignee_id = prepared_task["assignee"].id if prepared_task["assignee"] is not None else None
    existing_assignee_id = existing_assignment.user_id if existing_assignment is not None else None
    return all(
        [
            existing_task.org_id == prepared_task["org"].id,
            existing_task.department_id == (prepared_task["department"].id if prepared_task["department"] is not None else None),
            existing_task.decision_record_id
            == (prepared_task["decision_record"].id if prepared_task["decision_record"] is not None else None),
            existing_task.source_record_id
            == (prepared_task["source_record"].id if prepared_task["source_record"] is not None else None),
            existing_task.creator_user_id == prepared_task["creator_user"].id,
            existing_task.title == prepared_task["title"],
            existing_task.description == prepared_task["description"],
            existing_task.status == prepared_task["status"],
            existing_task.priority == prepared_task["priority"],
            existing_task.due_at == prepared_task["due_at"],
            dict(existing_task.meta or {}) == prepared_task["task_meta"],
            existing_assignee_id == expected_assignee_id,
        ]
    )


def _find_task_update_by_request_id(
    db: Session,
    *,
    task_row_id: int,
    request_id: str,
) -> TaskUpdateModel | None:
    rows = (
        db.query(TaskUpdateModel)
        .filter(
            TaskUpdateModel.task_id == task_row_id,
            or_(
                TaskUpdateModel.request_id == request_id,
                TaskUpdateModel.request_id.is_(None),
            ),
        )
        .order_by(TaskUpdateModel.id.desc())
        .all()
    )
    for row in rows:
        persisted_request_id = row.request_id or str(dict(row.meta or {}).get("request_id") or "")
        if persisted_request_id == request_id:
            return row
    return None


def _task_update_payload_matches(
    existing_update: TaskUpdateModel,
    *,
    status: str | None,
    title: str | None,
    description: str | None,
    task_payload: dict[str, Any] | None,
) -> bool:
    meta = dict(existing_update.meta or {})
    return (
        meta.get("status") == status
        and meta.get("title") == title
        and meta.get("description") == description
        and dict(meta.get("task_payload") or {}) == dict(task_payload or {})
    )


def _task_update_is_noop(
    row: TaskModel,
    *,
    status: str | None,
    title: str | None,
    description: str | None,
    task_payload: dict[str, Any] | None,
) -> bool:
    if status is not None and row.status != _map_task_status(status):
        return False
    if title is not None and row.title != title:
        return False
    if description is not None and row.description != description:
        return False
    if task_payload:
        merged_payload = dict(row.meta or {})
        merged_payload.update(task_payload)
        if merged_payload != dict(row.meta or {}):
            return False
    return True


def _serialize_task(
    row: TaskModel,
    assignment: TaskAssignmentModel | None,
    users: dict[int, str],
) -> dict[str, Any]:
    return {
        "id": row.id,
        "task_id": row.public_id,
        "assignee_user_id": users.get(assignment.user_id) if assignment is not None else None,
        "title": row.title,
        "description": row.description,
        "status": _task_status_to_text(row.status),
        "priority": _priority_to_text(row.priority),
        "task_payload": dict(row.meta or {}),
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


def _find_existing_staff_work_record(
    db: Session,
    *,
    org_id: int,
    user_id: int,
    record_date: date | None,
) -> WorkRecordModel | None:
    if record_date is None:
        return None
    return (
        db.query(WorkRecordModel)
        .filter(
            WorkRecordModel.org_id == org_id,
            WorkRecordModel.user_id == user_id,
            WorkRecordModel.record_date == record_date,
            WorkRecordModel.deleted_at.is_(None),
        )
        .order_by(WorkRecordModel.id.desc())
        .first()
    )


def _load_staff_report_snapshot(db: Session, work_record: WorkRecordModel) -> dict[str, Any] | None:
    snapshot_id = dict(work_record.meta or {}).get("staff_report_snapshot_id")
    if snapshot_id is not None:
        snapshot = db.get(StaffReportModel, snapshot_id)
        if snapshot is not None:
            return dict(snapshot.report_json or {})
    try:
        hydrated = load_staff_daily_report(db, work_record.id)
    except (KeyError, TypeError, ValueError):
        return None
    if hydrated is None:
        return None
    legacy = dict(hydrated.report.get("legacy_projection") or {})
    legacy.setdefault("record_date", work_record.record_date.isoformat() if work_record.record_date else None)
    return legacy


def _staff_report_payload_matches(existing_payload: dict[str, Any] | None, incoming_payload: dict[str, Any]) -> bool:
    if existing_payload is None:
        return False
    return _normalize_staff_report_comparison_payload(existing_payload) == _normalize_staff_report_comparison_payload(
        incoming_payload
    )


def _normalize_staff_report_comparison_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": payload.get("schema_id"),
        "schema_version": payload.get("schema_version"),
        "org_id": payload.get("org_id"),
        "department_id": payload.get("department_id"),
        "user_id": payload.get("user_id"),
        "node_id": payload.get("node_id"),
        "record_date": payload.get("record_date"),
        "work_progress": str(payload.get("work_progress") or ""),
        "issues_faced": _normalize_text_list_field(payload.get("issues_faced")),
        "solution_attempt": str(payload.get("solution_attempt") or ""),
        "need_support": bool(payload.get("need_support")),
        "next_day_plan": str(payload.get("next_day_plan") or ""),
        "risk_level": str(payload.get("risk_level") or ""),
        "resource_usage": dict(payload.get("resource_usage") or {}),
    }


def _normalize_text_list_field(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, list):
        items = [str(item).strip() for item in value if str(item).strip()]
        return tuple(items)
    text = str(value).strip()
    if not text:
        return ()
    return tuple(item.strip() for item in text.splitlines() if item.strip())
    snapshot = db.get(StaffReportModel, snapshot_id)
    if snapshot is None:
        return None
    return dict(snapshot.report_json or {})


def _build_existing_staff_report_response(
    db: Session,
    *,
    identity: AgentIdentity,
    work_record: WorkRecordModel,
    fallback_report: dict[str, Any],
) -> dict[str, Any]:
    hydrated = load_staff_daily_report(db, work_record.id)
    report_payload = dict(hydrated.report.get("legacy_projection") or fallback_report) if hydrated is not None else dict(
        fallback_report
    )
    incident_rows = (
        db.query(IncidentModel)
        .filter(IncidentModel.source_record_id == work_record.id, IncidentModel.deleted_at.is_(None))
        .order_by(IncidentModel.id.asc())
        .all()
    )
    created_incidents = [
        {
            "incident_id": row.id,
            "incident_public_id": row.public_id,
            "title": row.title,
            "severity": _incident_severity_to_text(row.severity),
            "status": _incident_status_to_text(row.status),
        }
        for row in incident_rows
    ]
    return {
        "work_record_id": work_record.id,
        "work_record_public_id": work_record.public_id,
        "staff_report_id": dict(work_record.meta or {}).get("staff_report_snapshot_id"),
        "incident_ids": [item["incident_id"] for item in created_incidents],
        "created_incidents": created_incidents,
        "identity": identity.to_dict(),
        "report": report_payload,
    }


def _normalize_staff_report_payload(
    identity: AgentIdentity,
    report: dict[str, Any],
    *,
    org: OrganizationModel,
    department: DepartmentModel | None,
    user: UserModel,
) -> dict[str, Any]:
    if "basic_info" in report and "legacy_projection" in report:
        normalized = dict(report)
        normalized["basic_info"] = {
            **dict(normalized["basic_info"]),
            "org_id": org.public_id,
            "department_or_project_group": department.public_id if department is not None else "",
            "user_id": user.username,
            "agent_node_id": identity.node_id,
        }
        normalized["legacy_projection"] = {
            **dict(normalized["legacy_projection"]),
            "org_id": org.public_id,
            "department_id": department.public_id if department is not None else "",
            "user_id": user.username,
            "node_id": identity.node_id,
            "record_date": normalized["basic_info"].get("report_date"),
            "risk_level": normalized.get("risk_assessment", {}).get("overall_risk_level"),
        }
        return normalized

    timestamp = str(report.get("timestamp") or "")
    record_date = str(report.get("record_date") or "") or _date_from_timestamp(timestamp)
    risk_level = str(report.get("risk_level") or "low").lower()
    blockers = _split_lines(report.get("issues_faced"))
    support_needed = bool(report.get("need_support"))

    today_task_progress = []
    if report.get("work_progress"):
        today_task_progress.append(
            {
                "line_no": 1,
                "related_task_id": None,
                "task_name": "Daily progress",
                "today_result": str(report.get("work_progress")),
                "previous_status": "in_progress",
                "current_status": "done" if not support_needed else "in_progress",
                "completion_percent": 100 if not support_needed else 70,
                "needs_follow_up": support_needed,
                "notes": None,
            }
        )

    today_blockers = []
    for index, blocker in enumerate(blockers, start=1):
        today_blockers.append(
            {
                "line_no": index,
                "issue_name": f"Blocker {index}",
                "issue_description": blocker,
                "impact_scope": "staff_workflow",
                "severity": risk_level,
                "attempted_solution": report.get("solution_attempt"),
                "is_blocking": True,
                "support_owner": identity.manager_node_id,
            }
        )

    support_requests = []
    if support_needed:
        support_requests.append(
            {
                "line_no": 1,
                "need_support": True,
                "support_item": "Manager support required",
                "support_reason": str(report.get("issues_faced") or ""),
                "expected_support_target": identity.manager_node_id,
                "expected_completion_at": None,
                "impact_if_unresolved": str(report.get("issues_faced") or ""),
            }
        )

    return {
        "schema_id": "schema_v1_staff_daily",
        "schema_version": "v1.0.0",
        "template_name": "AutoMage_2_Staff日报模板",
        "basic_info": {
            "report_date": record_date,
            "submitted_by": identity.metadata.get("display_name") or user.display_name,
            "project_name": "AutoMage-2 MVP",
            "role_name": "staff",
            "responsibility_module": department.name if department is not None else "",
            "work_types": [],
            "report_status": "confirmed",
            "submitted_at": timestamp or f"{record_date}T18:00:00+08:00",
            "self_confirmed": True,
            "schema_id_ref": report.get("schema_id", "schema_v1_staff"),
            "schema_version_ref": report.get("schema_version", "1.0.0"),
            "org_id": org.public_id,
            "department_or_project_group": department.public_id if department is not None else "",
            "user_id": user.username,
            "agent_node_id": identity.node_id,
            "submission_channel": "agent",
            "related_template_name": "Staff Daily Report Template",
        },
        "today_task_progress": today_task_progress,
        "today_completed_items": [],
        "today_artifacts": [],
        "today_blockers": today_blockers,
        "support_requests": support_requests,
        "decision_requests": [],
        "tomorrow_plans": _build_tomorrow_plans(report.get("next_day_plan")),
        "cross_module_requests": [],
        "risk_assessment": {
            "overall_risk_level": risk_level,
            "primary_risk_sources": blockers,
            "impacted_deliverables": [],
            "impacted_workflow_nodes": ["staff_report"],
            "suggested_mitigation": report.get("solution_attempt"),
            "needs_escalation": risk_level in {"high", "critical"} or support_needed,
            "escalation_targets": [identity.manager_node_id] if identity.manager_node_id else [],
        },
        "workflow_notes": [],
        "daily_summary": {
            "most_important_progress": str(report.get("work_progress") or ""),
            "biggest_issue": blockers[0] if blockers else "",
            "top_priority_tomorrow": str(report.get("next_day_plan") or ""),
            "team_attention_items": str(report.get("issues_faced") or ""),
        },
        "sign_off": {
            "submitter_confirmation_text": "I confirm the report reflects today’s work.",
            "confirmation_status": (report.get("signature") or {}).get("confirm_status", "confirmed"),
            "confirmed_by": (report.get("signature") or {}).get("confirmed_by", identity.user_id),
            "confirmed_at": timestamp or None,
        },
        "legacy_projection": {
            "schema_id": report.get("schema_id", "schema_v1_staff"),
            "schema_version": report.get("schema_version", "1.0.0"),
            "timestamp": timestamp or f"{record_date}T18:00:00+08:00",
            "org_id": org.public_id,
            "department_id": department.public_id if department is not None else "",
            "user_id": user.username,
            "node_id": identity.node_id,
            "record_date": record_date,
            "work_progress": str(report.get("work_progress") or ""),
            "issues_faced": "\n".join(blockers),
            "solution_attempt": str(report.get("solution_attempt") or ""),
            "need_support": support_needed,
            "next_day_plan": str(report.get("next_day_plan") or ""),
            "risk_level": risk_level,
            "resource_usage": dict(report.get("resource_usage") or {}),
        },
    }


def _build_decision_option_schema(decision: dict[str, Any]) -> dict[str, Any] | list[Any]:
    options = decision.get("decision_options") or decision.get("options")
    if options:
        return {"options": list(options)}
    selected_option_key = (
        decision.get("selected_option_id")
        or decision.get("selected_option_key")
        or decision.get("selected_option")
    )
    if selected_option_key:
        return {"options": [{"key": selected_option_key, "label": decision.get("selected_option_label")}]}
    return {"options": []}


def _build_dream_task_candidates(
    summary: SummaryModel,
    actor_identity: AgentIdentity,
    *,
    conservative: bool,
) -> list[dict[str, Any]]:
    base_title = "Review summary risks" if conservative else "Accelerate summary actions"
    base_desc = (
        "Validate top risks before scaling execution."
        if conservative
        else "Push follow-up actions while monitoring execution risk."
    )
    return [
        {
            "task_id": _public_id("TSK"),
            "title": base_title,
            "description": base_desc,
            "assignee_user_id": actor_identity.user_id,
            "status": "pending",
            "priority": "high" if conservative else "medium",
            "source_summary_id": summary.public_id,
        }
    ]


def _load_usernames_by_ids(db: Session, user_ids: Iterable[int | None]) -> dict[int, str]:
    filtered = sorted({user_id for user_id in user_ids if user_id is not None})
    if not filtered:
        return {}
    rows = db.query(UserModel).filter(UserModel.id.in_(filtered)).all()
    return {row.id: row.username for row in rows}


def _resolve_org(
    db: Session,
    org_ref: Any,
    *,
    user: UserModel | None,
) -> OrganizationModel:
    org = _try_resolve_org(db, org_ref)
    if org is not None:
        return org
    if user is not None:
        org = db.query(OrganizationModel).filter(OrganizationModel.id == user.org_id).one_or_none()
        if org is not None:
            return org
    org = db.query(OrganizationModel).order_by(OrganizationModel.id.asc()).first()
    if org is None:
        raise ValueError("Organization not found")
    return org


def _try_resolve_org(db: Session, org_ref: Any) -> OrganizationModel | None:
    if org_ref is None:
        return None
    value = str(org_ref).strip()
    if not value:
        return None
    query = db.query(OrganizationModel)
    if value.isdigit():
        return query.filter(OrganizationModel.id == int(value)).one_or_none()
    return query.filter(or_(OrganizationModel.public_id == value, OrganizationModel.code == value)).one_or_none()


def _resolve_department(
    db: Session,
    department_ref: Any,
    *,
    user: UserModel | None,
    org: OrganizationModel,
    actor: AgentIdentity | None,
) -> DepartmentModel | None:
    department = _try_resolve_department(db, department_ref, org=org)
    if department is not None:
        return department
    if actor is not None and actor.department_id:
        department = _try_resolve_department(db, actor.department_id, org=org)
        if department is not None:
            return department
    if user is not None:
        department = (
            db.query(DepartmentModel)
            .filter(DepartmentModel.org_id == org.id, DepartmentModel.manager_user_id == user.manager_user_id)
            .order_by(DepartmentModel.id.asc())
            .first()
        )
        if department is not None:
            return department
    return (
        db.query(DepartmentModel)
        .filter(DepartmentModel.org_id == org.id, DepartmentModel.deleted_at.is_(None))
        .order_by(DepartmentModel.id.asc())
        .first()
    )


def _try_resolve_department(
    db: Session,
    department_ref: Any,
    *,
    org: OrganizationModel | None,
) -> DepartmentModel | None:
    if department_ref is None:
        return None
    value = str(department_ref).strip()
    if not value:
        return None
    query = db.query(DepartmentModel)
    if org is not None:
        query = query.filter(DepartmentModel.org_id == org.id)
    if value.isdigit():
        return query.filter(DepartmentModel.id == int(value)).one_or_none()
    return query.filter(
        or_(DepartmentModel.public_id == value, DepartmentModel.code == value, DepartmentModel.name == value)
    ).one_or_none()


def _resolve_user(db: Session, user_ref: str) -> UserModel:
    user = _try_resolve_user(db, user_ref)
    if user is None:
        raise ValueError(f"User not found: {user_ref}")
    return user


def _try_resolve_user(db: Session, user_ref: str | None) -> UserModel | None:
    if user_ref is None:
        return None
    value = str(user_ref).strip()
    if not value:
        return None
    query = db.query(UserModel).filter(UserModel.deleted_at.is_(None))
    if value.isdigit():
        return query.filter(UserModel.id == int(value)).one_or_none()
    return query.filter(
        or_(
            UserModel.public_id == value,
            UserModel.username == value,
            UserModel.display_name == value,
        )
    ).one_or_none()


def _first_user(db: Session) -> UserModel:
    user = db.query(UserModel).filter(UserModel.deleted_at.is_(None)).order_by(UserModel.id.asc()).first()
    if user is None:
        raise ValueError("No active users found")
    return user


def _resolve_summary(db: Session, summary_ref: Any, *, org: OrganizationModel | None) -> SummaryModel:
    summary = _try_resolve_summary(db, summary_ref, org=org)
    if summary is None:
        raise ValueError(f"Summary not found: {summary_ref}")
    return summary


def _try_resolve_summary(db: Session, summary_ref: Any, *, org: OrganizationModel | None) -> SummaryModel | None:
    if summary_ref is None:
        return None
    value = str(summary_ref).strip()
    if not value:
        return None
    query = db.query(SummaryModel).filter(SummaryModel.deleted_at.is_(None))
    if org is not None:
        query = query.filter(SummaryModel.org_id == org.id)
    if value.isdigit():
        return query.filter(SummaryModel.id == int(value)).one_or_none()
    return query.filter(SummaryModel.public_id == value).one_or_none()


def _try_resolve_work_record(db: Session, record_ref: Any, *, org: OrganizationModel | None) -> WorkRecordModel | None:
    if record_ref is None:
        return None
    value = str(record_ref).strip()
    if not value:
        return None
    query = db.query(WorkRecordModel).filter(WorkRecordModel.deleted_at.is_(None))
    if org is not None:
        query = query.filter(WorkRecordModel.org_id == org.id)
    if value.isdigit():
        return query.filter(WorkRecordModel.id == int(value)).one_or_none()
    return query.filter(WorkRecordModel.public_id == value).one_or_none()


def _try_resolve_decision_record(
    db: Session,
    record_ref: Any,
    *,
    org: OrganizationModel | None,
) -> DecisionRecordModel | None:
    if record_ref is None:
        return None
    value = str(record_ref).strip()
    if not value:
        return None
    query = db.query(DecisionRecordModel).filter(DecisionRecordModel.deleted_at.is_(None))
    if org is not None:
        query = query.filter(DecisionRecordModel.org_id == org.id)
    if value.isdigit():
        return query.filter(DecisionRecordModel.id == int(value)).one_or_none()
    return query.filter(DecisionRecordModel.public_id == value).one_or_none()


def _should_create_incident(report: dict[str, Any]) -> bool:
    risk_level = str(report.get("risk_assessment", {}).get("overall_risk_level") or "").lower()
    needs_escalation = bool(report.get("risk_assessment", {}).get("needs_escalation"))
    has_blocker = any(item.get("is_blocking") for item in report.get("today_blockers", []))
    return risk_level in {"high", "critical"} or needs_escalation or has_blocker


def _map_task_status(value: Any) -> int:
    if isinstance(value, int):
        return value
    mapping = {
        None: TASK_STATUS_PENDING,
        "pending": TASK_STATUS_PENDING,
        "not_started": TASK_STATUS_PENDING,
        "in_progress": TASK_STATUS_IN_PROGRESS,
        "doing": TASK_STATUS_IN_PROGRESS,
        "done": TASK_STATUS_DONE,
        "completed": TASK_STATUS_DONE,
        "closed": TASK_STATUS_CLOSED,
    }
    return mapping.get(str(value).lower(), TASK_STATUS_PENDING)


def _task_status_to_text(value: int | None) -> str:
    mapping = {
        TASK_STATUS_PENDING: "pending",
        TASK_STATUS_IN_PROGRESS: "in_progress",
        TASK_STATUS_DONE: "done",
        TASK_STATUS_CLOSED: "closed",
    }
    return mapping.get(value or TASK_STATUS_PENDING, "pending")


def _map_priority(value: Any) -> int:
    if isinstance(value, int):
        return value
    mapping = {
        "critical": TASK_PRIORITY_HIGH,
        "high": TASK_PRIORITY_HIGH,
        "medium": TASK_PRIORITY_MEDIUM,
        "normal": TASK_PRIORITY_MEDIUM,
        "low": TASK_PRIORITY_LOW,
    }
    return mapping.get(str(value).lower(), TASK_PRIORITY_MEDIUM)


def _priority_to_text(value: int | None) -> str:
    mapping = {
        TASK_PRIORITY_HIGH: "high",
        TASK_PRIORITY_MEDIUM: "medium",
        TASK_PRIORITY_LOW: "low",
    }
    return mapping.get(value or TASK_PRIORITY_MEDIUM, "medium")


def _map_incident_severity(value: Any) -> int:
    if isinstance(value, int):
        return value
    mapping = {
        "low": INCIDENT_SEVERITY_LOW,
        "medium": INCIDENT_SEVERITY_MEDIUM,
        "high": INCIDENT_SEVERITY_HIGH,
        "critical": INCIDENT_SEVERITY_CRITICAL,
    }
    return mapping.get(str(value).lower(), INCIDENT_SEVERITY_MEDIUM)


def _incident_severity_to_text(value: int | None) -> str:
    mapping = {
        INCIDENT_SEVERITY_LOW: "low",
        INCIDENT_SEVERITY_MEDIUM: "medium",
        INCIDENT_SEVERITY_HIGH: "high",
        INCIDENT_SEVERITY_CRITICAL: "critical",
    }
    return mapping.get(value or INCIDENT_SEVERITY_MEDIUM, "medium")


def _incident_status_to_text(value: int | None) -> str:
    mapping = {
        INCIDENT_STATUS_OPEN: "open",
        INCIDENT_STATUS_IN_PROGRESS: "in_progress",
        INCIDENT_STATUS_RESOLVED: "resolved",
        INCIDENT_STATUS_CLOSED: "closed",
    }
    return mapping.get(value or INCIDENT_STATUS_OPEN, "open")


def _public_id(prefix: str) -> str:
    return f"{prefix}{uuid4().hex[:22].upper()}"


def _coerce_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    text = str(value).strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _coerce_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _date_from_timestamp(value: str) -> str:
    parsed = _coerce_datetime(value)
    if parsed is not None:
        return parsed.date().isoformat()
    return date.today().isoformat()


def _build_tomorrow_plans(value: Any) -> list[dict[str, Any]]:
    plans = _split_lines(value)
    if not plans:
        return []
    return [
        {
            "line_no": index,
            "plan": plan,
            "expected_artifact": None,
            "priority": "medium",
            "expected_completion_at": None,
            "dependencies": None,
            "needs_collaboration": False,
        }
        for index, plan in enumerate(plans, start=1)
    ]


def _split_lines(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [line.strip() for line in str(value).splitlines() if line.strip()]


def _snapshot_node_id(meta: dict[str, Any], username: str) -> str:
    snapshot_id = meta.get("staff_report_snapshot_id")
    if snapshot_id is not None:
        return f"staff-snapshot-{snapshot_id}"
    return f"staff-node-{username}"


def _org_label(org: OrganizationModel | None, org_id: int | None) -> str:
    if org is not None:
        return org.public_id
    return str(org_id) if org_id is not None else ""


def _department_label(department: DepartmentModel | None, department_id: int | None) -> str:
    if department is not None:
        return department.public_id
    return str(department_id) if department_id is not None else ""


def _now() -> datetime:
    return datetime.now(UTC)


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
