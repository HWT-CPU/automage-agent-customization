from __future__ import annotations

import unittest

from automage_agents.core.enums import AgentLevel, AgentRole
from automage_agents.core.models import AgentIdentity
from automage_agents.server.rbac import AccessRequest, is_allowed


class RbacPolicyTests(unittest.TestCase):
    def test_staff_can_only_read_own_staff_report(self) -> None:
        identity = AgentIdentity(
            node_id="staff-node-1",
            user_id="user_backend_001",
            role=AgentRole.STAFF,
            level=AgentLevel.L1_STAFF,
            department_id="dept_mvp_core",
        )
        self.assertTrue(
            is_allowed(
                identity,
                AccessRequest(
                    resource="staff_reports",
                    action="read",
                    owner_user_id="user_backend_001",
                    department_id="dept_mvp_core",
                ),
            )
        )
        self.assertFalse(
            is_allowed(
                identity,
                AccessRequest(
                    resource="staff_reports",
                    action="read",
                    owner_user_id="user_other_001",
                    department_id="dept_mvp_core",
                ),
            )
        )

    def test_manager_cannot_create_task_for_other_department(self) -> None:
        identity = AgentIdentity(
            node_id="manager-node-1",
            user_id="user_manager_001",
            role=AgentRole.MANAGER,
            level=AgentLevel.L2_MANAGER,
            department_id="dept_mvp_core",
        )
        self.assertFalse(
            is_allowed(
                identity,
                AccessRequest(
                    resource="tasks",
                    action="create",
                    owner_user_id="user_ops_001",
                    department_id="dept_mvp_ops",
                    manager_user_id="user_manager_ops_001",
                    manager_node_id="manager-node-ops",
                ),
            )
        )

    def test_executive_has_global_access(self) -> None:
        identity = AgentIdentity(
            node_id="executive-node",
            user_id="user_executive_001",
            role=AgentRole.EXECUTIVE,
            level=AgentLevel.L3_EXECUTIVE,
            department_id=None,
        )
        self.assertTrue(
            is_allowed(
                identity,
                AccessRequest(
                    resource="decisions",
                    action="create",
                    department_id="dept_mvp_ops",
                ),
            )
        )
