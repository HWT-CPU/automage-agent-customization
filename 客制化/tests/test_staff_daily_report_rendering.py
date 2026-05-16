from __future__ import annotations

import unittest

from automage_agents.schemas.staff_daily_report_parser import parse_staff_daily_report_markdown
from automage_agents.schemas.staff_daily_report_rendering import render_staff_daily_report_markdown
from tests.test_staff_daily_report_parser import SAMPLE_MARKDOWN


class StaffDailyReportRenderingTests(unittest.TestCase):
    def test_render_markdown_contains_sections(self) -> None:
        report = parse_staff_daily_report_markdown(SAMPLE_MARKDOWN)
        markdown = render_staff_daily_report_markdown(report)

        self.assertIn("# AutoMage_2_Staff日报模板", markdown)
        self.assertIn("## 0. 基础信息", markdown)
        self.assertIn("## 11. 今日总结", markdown)
        self.assertIn("Build parser", markdown)
        self.assertIn("Parser schema aligned", markdown)


if __name__ == "__main__":
    unittest.main()
