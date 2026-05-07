from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from automage_agents.db.models import (
    AgentSessionModel,
    DecisionRecordModel,
    DecisionLogModel,
    FormalDecisionLogModel,
    IncidentModel,
    IncidentUpdateModel,
    ManagerReportModel,
    StaffReportModel,
    SummaryModel,
    SummarySourceLinkModel,
    TaskAssignmentModel,
    TaskModel,
    TaskQueueModel,
    TaskUpdateModel,
    WorkRecordItemModel,
    WorkRecordModel,
)


MODEL_REGISTRY = {
    "agent_sessions": AgentSessionModel,
    "staff_reports": StaffReportModel,
    "manager_reports": ManagerReportModel,
    "agent_decision_logs": DecisionLogModel,
    "work_records": WorkRecordModel,
    "work_record_items": WorkRecordItemModel,
    "summaries": SummaryModel,
    "summary_source_links": SummarySourceLinkModel,
    "decision_records": DecisionRecordModel,
    "decision_logs": FormalDecisionLogModel,
    "incidents": IncidentModel,
    "incident_updates": IncidentUpdateModel,
    "tasks": TaskModel,
    "task_assignments": TaskAssignmentModel,
    "task_updates": TaskUpdateModel,
    "task_queue": TaskQueueModel,
}

IMMUTABLE_FIELDS = {"id", "created_at"}


def serialize_record(record: Any) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for prop in record.__mapper__.column_attrs:
        column = prop.columns[0]
        value = getattr(record, prop.key)
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        data[column.name] = value
    return data


def list_records(db: Session, resource: str, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    model = MODEL_REGISTRY[resource]
    rows = db.query(model).offset(offset).limit(limit).all()
    return [serialize_record(row) for row in rows]


def get_record(db: Session, resource: str, record_id: int) -> dict[str, Any] | None:
    model = MODEL_REGISTRY[resource]
    row = db.get(model, record_id)
    if row is None:
        return None
    return serialize_record(row)


def delete_record(db: Session, resource: str, record_id: int) -> bool:
    model = MODEL_REGISTRY[resource]
    row = db.get(model, record_id)
    if row is None:
        return False
    db.delete(row)
    db.commit()
    return True


def create_record(db: Session, resource: str, payload: dict[str, Any]) -> dict[str, Any]:
    model = MODEL_REGISTRY[resource]
    normalized = _normalize_payload(model, payload, partial=False)
    row = model(**normalized)
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize_record(row)


def update_record(db: Session, resource: str, record_id: int, payload: dict[str, Any], *, partial: bool) -> dict[str, Any] | None:
    model = MODEL_REGISTRY[resource]
    row = db.get(model, record_id)
    if row is None:
        return None

    normalized = _normalize_payload(model, payload, partial=partial)
    for attr_name, value in normalized.items():
        setattr(row, attr_name, value)

    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize_record(row)


def _normalize_payload(model: type, payload: dict[str, Any], *, partial: bool) -> dict[str, Any]:
    column_map = {prop.columns[0].name: prop.key for prop in model.__mapper__.column_attrs}
    writable_columns = {
        column_name: attr_name for column_name, attr_name in column_map.items() if column_name not in IMMUTABLE_FIELDS
    }

    unknown = sorted(set(payload) - set(writable_columns))
    if unknown:
        raise ValueError(f"Unknown or immutable fields: {', '.join(unknown)}")

    if not partial:
        required = {
            prop.columns[0].name
            for prop in model.__mapper__.column_attrs
            if not prop.columns[0].nullable
            and prop.columns[0].name not in IMMUTABLE_FIELDS
            and prop.columns[0].server_default is None
            and prop.columns[0].default is None
        }
        missing = sorted(required - set(payload))
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

    return {writable_columns[column_name]: value for column_name, value in payload.items()}
