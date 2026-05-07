from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from automage_agents.config import load_runtime_settings
from automage_agents.core.enums import AgentRole
from automage_agents.core.models import AgentIdentity


_settings = load_runtime_settings("configs/automage.local.toml")


@dataclass(frozen=True, slots=True)
class AccessRequest:
    resource: str
    action: str
    owner_user_id: str | None = None
    owner_node_id: str | None = None
    department_id: str | None = None
    manager_user_id: str | None = None
    manager_node_id: str | None = None
    payload: dict[str, Any] | None = None


def is_allowed(identity: AgentIdentity, request: AccessRequest) -> bool:
    if not _settings.rbac_enabled:
        return _fallback_role_check(identity, request)

    if identity.role == AgentRole.EXECUTIVE:
        return True

    if identity.role == AgentRole.MANAGER:
        return _manager_allowed(identity, request)

    if identity.role == AgentRole.STAFF:
        return _staff_allowed(identity, request)

    return False


def _fallback_role_check(identity: AgentIdentity, request: AccessRequest) -> bool:
    if identity.role == AgentRole.EXECUTIVE:
        return True
    if identity.role == AgentRole.MANAGER:
        return request.resource in {"staff_reports", "manager_reports", "tasks", "audit_logs"}
    if identity.role == AgentRole.STAFF:
        return request.resource in {"staff_reports", "tasks", "audit_logs"}
    return False


def _manager_allowed(identity: AgentIdentity, request: AccessRequest) -> bool:
    if request.resource == "manager_reports":
        return _same_department(identity, request) and _same_manager(identity, request)
    if request.resource == "staff_reports":
        return _same_department(identity, request)
    if request.resource == "tasks":
        return _same_department(identity, request) and _same_manager_or_unassigned(identity, request)
    if request.resource == "audit_logs":
        return request.action == "read" and (
            _same_department(identity, request)
            or request.owner_user_id in {None, identity.user_id}
            or request.resource == "audit_logs"
        )
    if request.resource == "dream":
        return False
    if request.resource == "decisions":
        return False
    return False


def _staff_allowed(identity: AgentIdentity, request: AccessRequest) -> bool:
    if request.resource == "staff_reports":
        return request.action in {"create", "read"} and _same_owner(identity, request)
    if request.resource == "tasks":
        if request.action == "read":
            return _same_owner(identity, request)
        if request.action == "update":
            return _same_owner(identity, request)
        return False
    if request.resource == "audit_logs":
        if request.action != "read":
            return False
        return request.owner_user_id in {None, identity.user_id}
    return False


def _same_owner(identity: AgentIdentity, request: AccessRequest) -> bool:
    if request.owner_user_id and request.owner_user_id != identity.user_id:
        return False
    if request.owner_node_id and request.owner_node_id != identity.node_id:
        return False
    if request.department_id and identity.department_id and request.department_id != identity.department_id:
        return False
    return True


def _same_department(identity: AgentIdentity, request: AccessRequest) -> bool:
    if not identity.department_id or not request.department_id:
        return True
    return request.department_id == identity.department_id


def _same_manager(identity: AgentIdentity, request: AccessRequest) -> bool:
    if request.manager_user_id and request.manager_user_id != identity.user_id:
        return False
    if request.manager_node_id and request.manager_node_id != identity.node_id:
        return False
    return True


def _same_manager_or_unassigned(identity: AgentIdentity, request: AccessRequest) -> bool:
    if request.manager_user_id is None and request.manager_node_id is None:
        return True
    return _same_manager(identity, request)
