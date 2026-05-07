from __future__ import annotations

import unittest

from automage_agents.schemas.staff_daily_report_parser import (
    parse_staff_daily_report_bytes,
    parse_staff_daily_report_markdown,
)


SAMPLE_MARKDOWN = """# Demo

## 0. Basic Info

| Field | Value |
| --- | --- |
| report_date | 2026-05-06 |
| submitted_by | Alice |
| project_name | AutoMage-2 MVP |
| role_name | Backend |
| responsibility_module | Database |
| work_types | database / backend |
| report_status | 已确认 |
| submitted_at | 2026-05-06T18:30:00+08:00 |
| self_confirmed | 是 |
| schema_id | schema_v1_staff |
| schema_version | v1.0.0 |
| org_id | org-001 |
| department_or_project_group | backend |
| user_id | user-001 |
| agent_node_id | staff-node-001 |
| submission_channel | Web |
| related_template_name | Staff Daily Report Template |

## 1. Today Task Progress

| No | Related Task ID | Task Name | Today Result | Previous Status | Current Status | Completion | Need Follow Up | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | task-001 | Build parser | Markdown parser completed | in progress | 已完成 | 100% | 否 | merged |

## 2. Today Completed Items

| No | Item Name | Item Type | Completion Detail | Current Status | Evidence | Artifact Title | Artifact URI | Related Module | Reusable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Parser doc | document | Wrote mapping doc | 已完成 | reviewed | staff_daily_report_mapping.md | docs/staff_daily_report_mapping.md | docs | 是 |

## 3. Today Artifacts

| No | Artifact Name | Artifact Type | Main Content | Usage Scope | Current Version | Synced |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Parser JSON | document | Parsed output sample | demo | v1 | 是 |

## 4. Today Blockers

| No | Issue Name | Issue Description | Impact Scope | Severity | Attempted Solution | Blocking | Support Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Encoding issue | Need fallback decoding | parser | 中 | Added encoding candidates | 是 | infra |

## 5. Support Requests

| No | Need Support | Support Item | Support Reason | Expected Support Target | Expected Completion At | Impact If Unresolved |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 是 | Confirm file encoding | Avoid parse failure | backend lead | 2026-05-07T12:00:00+08:00 | Parsing may fail |

## 6. Decision Requests

| No | Decision Item | Background | Options | Recommended | Decision Level | Escalation Target | Impact If Unconfirmed | Expected Confirmation At | Confirmed By |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Parser storage | Need choose final storage | A: JSON only; B: Structured storage | B | L2 | Manager | Blocks implementation | 2026-05-07T18:00:00+08:00 | CTO |

## 7. Tomorrow Plans

| No | Plan | Expected Artifact | Priority | Expected Completion At | Dependencies | Need Collaboration |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Build DB writer | insertion module | 高 | 2026-05-07T20:00:00+08:00 | schema review | 是 |

## 8. Cross Module Requests

| No | Counterpart | Request Content | Need From Other Side | Available From Me | Expected Completion At | Current Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | backend | align insert API | API fields | parser payload | 2026-05-07T16:00:00+08:00 | 进行中 |

## 9. Risk Assessment

| Field | Value |
| --- | --- |
| overall_risk_level | 中 |
| primary_risk_sources | encoding, schema drift |
| impacted_deliverables | parser, db writer |
| impacted_workflow_nodes | staff_report, database_write |
| suggested_mitigation | lock schema before coding |
| needs_escalation | 否 |
| escalation_targets | Manager |

## 10. Context / Prompt / Workflow Notes

| Type | Content | Target Roles | Recommend Persist | Validated | Notes |
| --- | --- | --- | --- | --- | --- |
| Context | Keep raw markdown snapshot | staff / manager | 是 | 是 | useful for replay |

## 11. Daily Summary

| Field | Value |
| --- | --- |
| most_important_progress | Parser schema aligned |
| biggest_issue | Encoding uncertainty |
| top_priority_tomorrow | Write DB persistence |
| team_attention_items | Keep schema stable |

## 12. Sign Off

| Field | Value |
| --- | --- |
| submitter_confirmation_text | I confirm the content is accurate |
| confirmation_status | 已确认 |
| confirmed_by | Alice |
| confirmed_at | 2026-05-06T18:35:00+08:00 |
"""


class StaffDailyReportParserTests(unittest.TestCase):
    def test_parse_markdown_to_normalized_report(self) -> None:
        report = parse_staff_daily_report_markdown(SAMPLE_MARKDOWN)

        self.assertEqual(report["schema_id"], "schema_v1_staff_daily")
        self.assertEqual(report["basic_info"]["user_id"], "user-001")
        self.assertEqual(report["basic_info"]["report_status"], "confirmed")
        self.assertEqual(report["basic_info"]["submission_channel"], "web")
        self.assertEqual(report["today_task_progress"][0]["current_status"], "done")
        self.assertTrue(report["today_completed_items"][0]["reusable_for_followup"])
        self.assertTrue(report["today_blockers"][0]["is_blocking"])
        self.assertEqual(report["decision_requests"][0]["recommended_option_key"], "B")
        self.assertEqual(report["risk_assessment"]["overall_risk_level"], "medium")
        self.assertEqual(report["workflow_notes"][0]["note_type"], "context")
        self.assertEqual(report["sign_off"]["confirmation_status"], "confirmed")

    def test_builds_legacy_projection(self) -> None:
        report = parse_staff_daily_report_markdown(SAMPLE_MARKDOWN)
        legacy = report["legacy_projection"]

        self.assertEqual(legacy["schema_id"], "schema_v1_staff")
        self.assertTrue(legacy["need_support"])
        self.assertIn("Markdown parser completed", legacy["work_progress"])
        self.assertIn("Need fallback decoding", legacy["issues_faced"])
        self.assertIn("Build DB writer", legacy["next_day_plan"])
        self.assertEqual(legacy["resource_usage"]["task_count"], 1)

    def test_parse_bytes_keeps_chinese_content(self) -> None:
        markdown = """# 示例

## 0. Basic Info

| Field | Value |
| --- | --- |
| report_date | 2026-05-05 |
| submitted_by | 熊锦文 |
| report_status | 已确认 |
| self_confirmed | 是 |

## 5. Support Requests

| No | Need Support | Support Item | Support Reason | Expected Support Target | Expected Completion At | Impact If Unresolved |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 是 | 联调支持 | 接口待确认 | 后端负责人 | 2026-05-06T12:00:00+08:00 | 影响交付 |

## 9. Risk Assessment

| Field | Value |
| --- | --- |
| overall_risk_level | 中 |
| needs_escalation | 否 |
"""
        report = parse_staff_daily_report_bytes(markdown.encode("utf-8"))

        self.assertEqual(report["basic_info"]["submitted_by"], "熊锦文")
        self.assertEqual(report["basic_info"]["report_date"], "2026-05-05")
        self.assertTrue(report["support_requests"][0]["need_support"])
        self.assertEqual(report["risk_assessment"]["overall_risk_level"], "medium")

    def test_parse_markdown_with_unnumbered_chinese_section_titles(self) -> None:
        markdown = """# 示例

## 基础信息

| 字段 | 值 |
| --- | --- |
| 日报日期 | 2026-05-07 |
| 提交人 | 胡文涛 |
| 日报状态 | 已确认 |
| 本人确认 | 是 |

## 今日任务进展

| No | Related Task ID | Task Name | Today Result | Previous Status | Current Status | Completion | Need Follow Up | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | TASK-1 | Agent 联调 | 已完成 IM 闭环验收 | 进行中 | 已完成 | 100% | 否 | 可进入下一步 |

## 明日计划

| No | Plan | Expected Artifact | Priority | Expected Completion At | Dependencies | Need Collaboration |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 补齐生产权限 | 权限测试 | 高 | 2026-05-08T18:00:00+08:00 | open_id | 是 |
"""
        report = parse_staff_daily_report_markdown(markdown)

        self.assertEqual(report["basic_info"]["submitted_by"], "胡文涛")
        self.assertEqual(report["basic_info"]["report_date"], "2026-05-07")
        self.assertEqual(report["today_task_progress"][0]["current_status"], "done")
        self.assertIn("补齐生产权限", report["legacy_projection"]["next_day_plan"])


if __name__ == "__main__":
    unittest.main()
