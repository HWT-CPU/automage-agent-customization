from __future__ import annotations

from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DELIVERY_ROOT = PROJECT_ROOT / "delivery"


class DeliveryDatabaseSkillDocsTests(unittest.TestCase):
    def _read(self, relative_path: str) -> str:
        return (DELIVERY_ROOT / relative_path).read_text(encoding="utf-8")

    def test_skill_doc_matches_formal_main_path(self) -> None:
        content = self._read("database-api-skill/SKILL.md")
        self.assertIn("work_records / work_record_items", content)
        self.assertIn("summaries / summary_source_links", content)
        self.assertIn("decision_records / decision_logs", content)
        self.assertIn("tasks / task_assignments / task_updates", content)
        self.assertIn("/api/v1/audit-logs", content)

    def test_http_flow_mentions_current_protection_chain(self) -> None:
        content = self._read("database-api-skill/references/http-flow.md")
        self.assertIn("/internal/dream/run", content)
        self.assertIn("RBAC", content)
        self.assertIn("限流", content)
        self.assertIn("幂等", content)

    def test_sqlalchemy_flow_marks_legacy_boundary(self) -> None:
        content = self._read("database-api-skill/references/sqlalchemy-flow.md")
        self.assertIn("旧快照表链路", content)
        self.assertIn("不应替代当前正式 HTTP API 主链路", content)

    def test_table_map_mentions_formal_task_and_summary_tables(self) -> None:
        content = self._read("database-api-skill/references/table-map.md")
        self.assertIn("summary_source_links", content)
        self.assertIn("task_assignments", content)
        self.assertIn("task_updates", content)
        self.assertIn("incident_updates", content)

    def test_delivery_overview_mentions_snapshot_is_compatible_only(self) -> None:
        content = self._read("database-skill-delivery-zh.md")
        self.assertIn("快照表仅保留兼容镜像", content)
        self.assertIn("HTTP API 路径为主口径", content)


if __name__ == "__main__":
    unittest.main()
