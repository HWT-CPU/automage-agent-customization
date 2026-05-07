from enum import StrEnum


class AgentRole(StrEnum):
    BASE = "base"
    STAFF = "staff"
    MANAGER = "manager"
    EXECUTIVE = "executive"


class AgentLevel(StrEnum):
    BASE = "base"
    L1_STAFF = "l1_staff"
    L2_MANAGER = "l2_manager"
    L3_EXECUTIVE = "l3_executive"


class RuntimeChannel(StrEnum):
    MOCK = "mock"
    OPENCLAW = "openclaw"
    FEISHU = "feishu"
    CLI = "cli"


class AuthStatus(StrEnum):
    UNKNOWN = "unknown"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class InternalEventType(StrEnum):
    DAILY_REPORT_SUBMITTED = "daily_report_submitted"
    TASK_QUERY_REQUESTED = "task_query_requested"
    TASK_UPDATE_REQUESTED = "task_update_requested"
    REMINDER_ACKED = "reminder_acked"
    TASK_COMPLETED = "task_completed"
    MANAGER_FEEDBACK_SUBMITTED = "manager_feedback_submitted"
    DREAM_DECISION_REQUESTED = "dream_decision_requested"
    EXECUTIVE_DECISION_SELECTED = "executive_decision_selected"
    AUTH_FAILED = "auth_failed"
