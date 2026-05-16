"""Schema helpers and placeholders pending final contract confirmation."""

from automage_agents.schemas.placeholders import (
    DREAM_DECISION_SCHEMA_ID,
    MANAGER_REPORT_SCHEMA_ID,
    STAFF_REPORT_SCHEMA_ID,
)
from automage_agents.schemas.staff_daily_report_parser import (
    build_legacy_projection,
    parse_staff_daily_report_bytes,
    parse_staff_daily_report_file,
    parse_staff_daily_report_markdown,
)
from automage_agents.schemas.executive_v1 import (
    coerce_decision_commit_payload,
    coerce_executive_decision_card_payload,
    coerce_task_v1_payload,
)

__all__ = [
    "DREAM_DECISION_SCHEMA_ID",
    "MANAGER_REPORT_SCHEMA_ID",
    "STAFF_REPORT_SCHEMA_ID",
    "build_legacy_projection",
    "coerce_decision_commit_payload",
    "coerce_executive_decision_card_payload",
    "coerce_task_v1_payload",
    "parse_staff_daily_report_bytes",
    "parse_staff_daily_report_file",
    "parse_staff_daily_report_markdown",
]
