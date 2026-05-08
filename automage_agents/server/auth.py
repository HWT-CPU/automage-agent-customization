from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from automage_agents.config import load_runtime_settings
from automage_agents.core.enums import AgentLevel, AgentRole
from automage_agents.core.models import AgentIdentity
from automage_agents.db.models import TaskModel
from automage_agents.server.audit import try_write_audit_log
from automage_agents.server.rbac import AccessRequest, is_allowed
from automage_agents.server.schemas import IdentityPayload


_settings = load_runtime_settings("configs/automage.local.toml")

_DEFAULT_LEVEL_BY_ROLE = {
    AgentRole.STAFF: AgentLevel.L1_STAFF,
    AgentRole.MANAGER: AgentLevel.L2_MANAGER,
    AgentRole.EXECUTIVE: AgentLevel.L3_EXECUTIVE,
}


@dataclass(slots=True)
class AuthenticatedActor:
    identity: AgentIdentity
    token: str | None = None


def get_current_actor(request: Request) -> AuthenticatedActor | None:
    if not _settings.auth_enabled:
        return _parse_actor_from_headers(request, required=False)

    expected_token = (_settings.auth_token or "").strip()
    if not expected_token:
        raise HTTPException(status_code=500, detail="Server auth is enabled but auth_token is not configured")

    authorization = request.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid bearer token")
    if token != expected_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")

    actor = _parse_actor_from_headers(request, required=True)
    return AuthenticatedActor(identity=actor.identity, token=token)


def require_roles(*allowed_roles: AgentRole) -> Callable[[AuthenticatedActor | None], AuthenticatedActor | None]:
    allowed = {role.value for role in allowed_roles}

    def dependency(actor: AuthenticatedActor | None = Depends(get_current_actor)) -> AuthenticatedActor | None:
        if actor is None:
            return None
        if actor.identity.role.value not in allowed:
            _raise_forbidden(actor, f"Role {actor.identity.role.value} is not allowed to access this resource")
        return actor

    return dependency


def assert_actor_has_role(actor: AuthenticatedActor | None, *allowed_roles: AgentRole, db: Session | None = None) -> None:
    if actor is None:
        return
    allowed = {role.value for role in allowed_roles}
    if actor.identity.role.value not in allowed:
        _raise_forbidden(actor, f"Role {actor.identity.role.value} is not allowed to access this resource", db=db)


def assert_identity_matches_actor(actor: AuthenticatedActor | None, payload: IdentityPayload, *, db: Session | None = None) -> None:
    if actor is None:
        return
    identity = actor.identity
    mismatches: list[str] = []
    if payload.user_id != identity.user_id:
        mismatches.append("user_id")
    if payload.node_id != identity.node_id:
        mismatches.append("node_id")
    if payload.role.value != identity.role.value:
        mismatches.append("role")
    if payload.department_id and identity.department_id and payload.department_id != identity.department_id:
        mismatches.append("department_id")
    if mismatches:
        _raise_forbidden(actor, f"Request identity does not match authenticated actor: {', '.join(mismatches)}", db=db)


def filter_staff_reports_for_actor(
    actor: AuthenticatedActor | None,
    reports: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if actor is None or actor.identity.role == AgentRole.EXECUTIVE:
        return reports
    if actor.identity.role == AgentRole.MANAGER:
        if not actor.identity.department_id:
            return []
        return [report for report in reports if _report_department_id(report) == actor.identity.department_id]
    return [report for report in reports if str(report.get("user_id")) == actor.identity.user_id]


def filter_manager_reports_for_actor(
    actor: AuthenticatedActor | None,
    reports: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if actor is None or actor.identity.role == AgentRole.EXECUTIVE:
        return reports
    if actor.identity.role == AgentRole.MANAGER:
        return [
            report
            for report in reports
            if _manager_report_is_visible_to_actor(actor, report)
        ]
    return []


def resolve_task_query_scope(
    actor: AuthenticatedActor | None,
    *,
    user_id: str | None,
    assignee_user_id: str | None,
) -> tuple[str | None, str | None]:
    if actor is None or actor.identity.role == AgentRole.EXECUTIVE:
        return user_id, assignee_user_id
    return actor.identity.user_id, actor.identity.user_id


def filter_tasks_for_actor(
    actor: AuthenticatedActor | None,
    tasks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if actor is None or actor.identity.role == AgentRole.EXECUTIVE:
        return tasks
    if actor.identity.role == AgentRole.MANAGER:
        return [task for task in tasks if _task_is_visible_to_manager(actor, task)]
    return [task for task in tasks if _task_is_visible_to_staff(actor, task)]


def assert_task_update_allowed(actor: AuthenticatedActor | None, task: TaskModel, *, db: Session | None = None) -> None:
    if actor is None or actor.identity.role == AgentRole.EXECUTIVE:
        return
    task_meta = dict(task.meta or {})
    task_department_id = (
        str(task_meta.get("department_id") or task_meta.get("dept_id") or "") or None
    )
    if task_department_id is None and task.department_id is not None:
        task_department_id = str(task.department_id)
    allowed = is_allowed(
        actor.identity,
        AccessRequest(
            resource="tasks",
            action="update",
            owner_user_id=str(task_meta.get("assignee_user_id")) if task_meta.get("assignee_user_id") is not None else None,
            owner_node_id=str(task_meta.get("assignee_node_id")) if task_meta.get("assignee_node_id") is not None else None,
            department_id=task_department_id,
            manager_user_id=str(task_meta.get("manager_user_id")) if task_meta.get("manager_user_id") is not None else None,
            manager_node_id=str(task_meta.get("manager_node_id")) if task_meta.get("manager_node_id") is not None else None,
            payload=task_meta,
        ),
    )
    if not allowed:
        _raise_forbidden(actor, "You are not allowed to update this task", db=db)


def assert_staff_report_visible(actor: AuthenticatedActor | None, report: dict[str, Any] | None, *, db: Session | None = None) -> None:
    if actor is None or actor.identity.role == AgentRole.EXECUTIVE or report is None:
        return
    allowed = is_allowed(
        actor.identity,
        AccessRequest(
            resource="staff_reports",
            action="read",
            owner_user_id=_report_user_id(report),
            department_id=_report_department_id(report),
            payload=report,
        ),
    )
    if not allowed:
        _raise_forbidden(actor, "You are not allowed to read this staff report", db=db)


def assert_manager_report_payload_allowed(
    actor: AuthenticatedActor | None, payload: dict[str, Any], *, db: Session | None = None
) -> None:
    if actor is None or actor.identity.role == AgentRole.EXECUTIVE:
        return
    requested_department_id = str(payload.get("dept_id") or payload.get("department_id") or "") or None
    if actor.identity.department_id and requested_department_id and requested_department_id != actor.identity.department_id:
        _raise_forbidden(actor, "Manager report is outside your RBAC scope", db=db)
    allowed = is_allowed(
        actor.identity,
        AccessRequest(
            resource="manager_reports",
            action="create",
            department_id=requested_department_id,
            manager_user_id=str(payload.get("manager_user_id") or "") or None,
            manager_node_id=str(payload.get("manager_node_id") or "") or None,
            payload=payload,
        ),
    )
    if not allowed:
        _raise_forbidden(actor, "Manager report is outside your RBAC scope", db=db)


def assert_task_create_payload_allowed(
    actor: AuthenticatedActor | None, tasks: list[dict[str, Any]], *, db: Session | None = None
) -> None:
    if actor is None or actor.identity.role == AgentRole.EXECUTIVE:
        return
    for task in tasks:
        allowed = is_allowed(
            actor.identity,
            AccessRequest(
                resource="tasks",
                action="create",
                owner_user_id=str(task.get("assignee_user_id") or "") or None,
                owner_node_id=str(task.get("assignee_node_id") or "") or None,
                department_id=str(task.get("department_id") or "") or None,
                manager_user_id=str(task.get("manager_user_id") or "") or None,
                manager_node_id=str(task.get("manager_node_id") or "") or None,
                payload=task,
            ),
        )
        if not allowed:
            _raise_forbidden(actor, "Task create request is outside your RBAC scope", db=db)


def assert_audit_log_access(
    actor: AuthenticatedActor | None,
    *,
    target_type: str | None,
    actor_user_id: str | None,
    db: Session | None = None,
) -> None:
    if actor is None or actor.identity.role == AgentRole.EXECUTIVE:
        return
    allowed = is_allowed(
        actor.identity,
        AccessRequest(
            resource="audit_logs",
            action="read",
            owner_user_id=actor_user_id,
            payload={"target_type": target_type},
        ),
    )
    if not allowed:
        _raise_forbidden(actor, "You are not allowed to query audit logs for another user", db=db)


def filter_audit_logs_for_actor(
    actor: AuthenticatedActor | None,
    items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if actor is None or actor.identity.role == AgentRole.EXECUTIVE:
        return items
    if actor.identity.role == AgentRole.MANAGER:
        return [
            item
            for item in items
            if _audit_item_visible_to_manager(actor, item)
        ]
    return [
        item
        for item in items
        if _audit_item_visible_to_staff(actor, item)
    ]


def _parse_actor_from_headers(request: Request, *, required: bool) -> AuthenticatedActor | None:
    user_id = request.headers.get("X-User-Id")
    role_raw = request.headers.get("X-Role")
    node_id = request.headers.get("X-Node-Id")
    level_raw = request.headers.get("X-Level")

    required_fields = {
        "X-User-Id": user_id,
        "X-Role": role_raw,
        "X-Node-Id": node_id,
    }
    missing = [name for name, value in required_fields.items() if not value]
    if missing:
        if required:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Missing auth identity headers: {', '.join(missing)}",
            )
        return None

    try:
        role = AgentRole(str(role_raw))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Unsupported role: {role_raw}") from exc

    if role not in _DEFAULT_LEVEL_BY_ROLE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Unsupported role: {role.value}")

    try:
        level = AgentLevel(str(level_raw)) if level_raw else _DEFAULT_LEVEL_BY_ROLE[role]
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Unsupported level: {level_raw}") from exc

    identity = AgentIdentity(
        node_id=str(node_id),
        user_id=str(user_id),
        role=role,
        level=level,
        department_id=request.headers.get("X-Department-Id"),
        manager_node_id=request.headers.get("X-Manager-Node-Id"),
        metadata={"display_name": request.headers.get("X-Display-Name")} if request.headers.get("X-Display-Name") else {},
    )
    return AuthenticatedActor(identity=identity)


def _report_department_id(report: dict[str, Any]) -> str | None:
    payload = report.get("report") or {}
    department_id = payload.get("department_id", payload.get("dept_id"))
    if department_id is None:
        return None
    return str(department_id)


def _report_user_id(report: dict[str, Any]) -> str | None:
    payload = report.get("report") or {}
    user_id = payload.get("user_id", report.get("user_id"))
    if user_id is None:
        return None
    return str(user_id)


def _manager_report_is_visible_to_actor(actor: AuthenticatedActor, report: dict[str, Any]) -> bool:
    payload = report.get("report") or {}
    manager_user_id = payload.get("manager_user_id", report.get("user_id"))
    manager_node_id = payload.get("manager_node_id", report.get("node_id"))
    department_id = payload.get("dept_id", payload.get("department_id"))
    user_match = str(manager_user_id) == actor.identity.user_id
    node_match = not actor.identity.node_id or not manager_node_id or str(manager_node_id) == actor.identity.node_id
    dept_match = not actor.identity.department_id or not department_id or str(department_id) == actor.identity.department_id
    if user_match and node_match and dept_match:
        return True
    return bool(dept_match and department_id is not None)


def _task_is_visible_to_staff(actor: AuthenticatedActor, task: dict[str, Any]) -> bool:
    payload = task.get("task_payload") or {}
    assignee_user_id = task.get("assignee_user_id") or payload.get("assignee_user_id")
    assignee_node_id = payload.get("assignee_node_id")
    task_department_id = payload.get("department_id", payload.get("dept_id"))
    if str(assignee_user_id) != actor.identity.user_id:
        return False
    if assignee_node_id and str(assignee_node_id) != actor.identity.node_id:
        return False
    if actor.identity.department_id and task_department_id and str(task_department_id) != actor.identity.department_id:
        return False
    return True


def _task_is_visible_to_manager(actor: AuthenticatedActor, task: dict[str, Any]) -> bool:
    payload = task.get("task_payload") or {}
    assignee_user_id = task.get("assignee_user_id") or payload.get("assignee_user_id")
    assignee_node_id = payload.get("assignee_node_id")
    manager_user_id = payload.get("manager_user_id")
    manager_node_id = payload.get("manager_node_id")
    task_department_id = payload.get("department_id", payload.get("dept_id"))
    if actor.identity.department_id and task_department_id and str(task_department_id) != actor.identity.department_id:
        return False
    if manager_user_id and str(manager_user_id) != actor.identity.user_id:
        return False
    if manager_node_id and str(manager_node_id) != actor.identity.node_id:
        return False
    if assignee_user_id == actor.identity.user_id:
        return True
    if not assignee_user_id:
        return True
    if actor.identity.department_id and task_department_id and str(task_department_id) == actor.identity.department_id:
        return True
    if assignee_node_id and actor.identity.node_id and str(assignee_node_id) == actor.identity.node_id:
        return True
    return False


def _audit_item_visible_to_manager(actor: AuthenticatedActor, item: dict[str, Any]) -> bool:
    payload = dict(item.get("payload") or {})
    target_type = str(item.get("target_type") or "")
    if target_type in {"summaries", "manager_reports"}:
        department_id = str(payload.get("department_id") or payload.get("dept_id") or "")
        if actor.identity.department_id and department_id and department_id != actor.identity.department_id:
            return False
    actor_user_id = item.get("actor_user_id")
    return actor_user_id in {None, actor.identity.user_id} or target_type in {"tasks", "work_records", "summaries"}


def _audit_item_visible_to_staff(actor: AuthenticatedActor, item: dict[str, Any]) -> bool:
    target_type = str(item.get("target_type") or "")
    if target_type not in {"tasks", "work_records"}:
        return False
    payload = dict(item.get("payload") or {})
    payload_user_id = str(payload.get("user_id") or payload.get("assignee_user_id") or "")
    actor_user_id = item.get("actor_user_id")
    if payload_user_id and payload_user_id != actor.identity.user_id:
        return False
    if actor_user_id not in {None, actor.identity.user_id}:
        return False
    return True


def _raise_forbidden(actor: AuthenticatedActor | None, detail: str, *, db: Session | None = None) -> None:
    _write_permission_denied_audit(actor, detail, db=db)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def _write_permission_denied_audit(actor: AuthenticatedActor | None, detail: str, *, db: Session | None = None) -> None:
    if actor is None or not _settings.audit_enabled:
        return
    actor_user_id_raw = actor.identity.user_id
    try:
        actor_user_id = int(actor_user_id_raw)
    except ValueError:
        actor_user_id = None
    try_write_audit_log(
        db,
        org_id=_settings.audit_org_id,
        actor_user_id=actor_user_id,
        target_type="auth",
        target_id=0,
        action="permission_denied",
        summary=detail,
        payload={"identity": actor.identity.to_dict(), "detail": detail},
    )
