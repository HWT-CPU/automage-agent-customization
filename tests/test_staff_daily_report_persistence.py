from __future__ import annotations

import unittest

from automage_agents.schemas.staff_daily_report_parser import parse_staff_daily_report_markdown
from automage_agents.schemas.staff_daily_report_persistence import (
    StaffDailyReportPersistenceOptions,
    _build_search_projection_items,
    _build_work_record_items,
    _build_work_record_meta,
)
from tests.test_staff_daily_report_parser import SAMPLE_MARKDOWN


class StaffDailyReportPersistenceTests(unittest.TestCase):
    def test_build_work_record_items_contains_sections_and_projections(self) -> None:
        report = parse_staff_daily_report_markdown(SAMPLE_MARKDOWN)
        items = _build_work_record_items(report, org_id=1, work_record_id=100)

        field_keys = {item.field_key for item in items}
        self.assertIn("basic_info", field_keys)
        self.assertIn("today_task_progress", field_keys)
        self.assertIn("search.need_support", field_keys)
        self.assertIn("search.risk_level", field_keys)

    def test_build_work_record_meta_uses_aggregates(self) -> None:
        report = parse_staff_daily_report_markdown(SAMPLE_MARKDOWN)
        meta = _build_work_record_meta(
            report,
            StaffDailyReportPersistenceOptions(org_id=1, user_id=2, created_by=2),
        )

        self.assertTrue(meta["need_support"])
        self.assertEqual(meta["risk_level"], "medium")
        self.assertEqual(meta["blocker_count"], 1)
        self.assertEqual(meta["decision_count"], 1)
        self.assertEqual(meta["artifact_count"], 1)

    def test_build_search_projection_items(self) -> None:
        report = parse_staff_daily_report_markdown(SAMPLE_MARKDOWN)
        projections = dict((field_key, payload) for field_key, _, _, payload in _build_search_projection_items(report))

        self.assertTrue(projections["search.need_support"])
        self.assertEqual(projections["search.blocker_count"], 1)
        self.assertEqual(projections["search.decision_count"], 1)
        self.assertEqual(projections["search.risk_level"], "medium")


if __name__ == "__main__":
    unittest.main()
