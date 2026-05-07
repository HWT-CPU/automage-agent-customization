from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from automage_agents.db.models import AuditLogModel
from automage_agents.server.request_context import request_id_var


def write_audit_log(
    db: Session,
    *,
    org_id: int,
    actor_user_id: int | None,
    target_type: str,
    target_id: int,
    action: str,
    summary: str | None,
    payload: dict[str, Any],
) -> None:
    request_id = request_id_var.get()
    final_payload = dict(payload)
    if request_id is not None:
        final_payload.setdefault("request_id", request_id)

    row = AuditLogModel(
        org_id=org_id,
        actor_user_id=actor_user_id,
        target_type=target_type,
        target_id=target_id,
        action=action,
        summary=summary,
        payload=final_payload,
    )
    db.add(row)


def try_write_audit_log(
    db: Session | None,
    *,
    org_id: int,
    actor_user_id: int | None,
    target_type: str,
    target_id: int,
    action: str,
    summary: str | None,
    payload: dict[str, Any],
) -> None:
    if db is None:
        return
    try:
        write_audit_log(
            db,
            org_id=org_id,
            actor_user_id=actor_user_id,
            target_type=target_type,
            target_id=target_id,
            action=action,
            summary=summary,
            payload=payload,
        )
        db.commit()
    except Exception:
        db.rollback()
