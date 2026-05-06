from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.config import load_runtime_settings
from automage_agents.db import create_session_factory
from automage_agents.schemas.staff_daily_report_parser import parse_staff_daily_report_file
from automage_agents.schemas.staff_daily_report_persistence import (
    StaffDailyReportPersistenceOptions,
    persist_staff_daily_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parse a staff daily report markdown file and persist it to PostgreSQL.")
    parser.add_argument("input", help="Path to the markdown report file.")
    parser.add_argument("--config", default="configs/automage.local.toml", help="Runtime config path.")
    parser.add_argument("--org-id", required=True, type=int, help="Numeric org_id for work_records.")
    parser.add_argument("--user-id", required=True, type=int, help="Numeric user_id for work_records.")
    parser.add_argument("--department-id", type=int, help="Numeric department_id for work_records.")
    parser.add_argument("--created-by", type=int, help="Numeric actor user id.")
    parser.add_argument(
        "--skip-staff-report-snapshot",
        action="store_true",
        help="Do not write the legacy_projection snapshot into staff_reports.",
    )
    parser.add_argument(
        "--omit-source-markdown",
        action="store_true",
        help="Do not embed the original markdown in the normalized JSON payload.",
    )
    parser.add_argument("--snapshot-node-id", help="Optional node_id for staff_reports snapshot.")
    parser.add_argument("--snapshot-user-id", help="Optional string user_id for staff_reports snapshot.")
    parser.add_argument("--snapshot-role", default="staff", help="Optional role for staff_reports snapshot.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    settings = load_runtime_settings(args.config)
    report = parse_staff_daily_report_file(
        args.input,
        include_source_markdown=not args.omit_source_markdown,
    )

    snapshot_identity = None
    if args.snapshot_node_id or args.snapshot_user_id:
        snapshot_identity = {
            "node_id": args.snapshot_node_id or f"staff-node-{args.snapshot_user_id or args.user_id}",
            "user_id": args.snapshot_user_id or str(args.user_id),
            "role": args.snapshot_role,
        }

    session_factory = create_session_factory(settings.postgres)
    with session_factory() as db:
        result = persist_staff_daily_report(
            db,
            report,
            options=StaffDailyReportPersistenceOptions(
                org_id=args.org_id,
                user_id=args.user_id,
                department_id=args.department_id,
                created_by=args.created_by or args.user_id,
                include_staff_report_snapshot=not args.skip_staff_report_snapshot,
                staff_report_identity=snapshot_identity,
            ),
        )

    print(f"template_id={result.template_id}")
    print(f"work_record_id={result.work_record_id}")
    print(f"work_record_public_id={result.work_record_public_id}")
    print(f"item_count={result.item_count}")
    print(f"staff_report_id={result.staff_report_id}")


if __name__ == "__main__":
    main()
