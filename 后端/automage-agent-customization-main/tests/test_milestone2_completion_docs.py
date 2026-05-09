from __future__ import annotations

from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Milestone2CompletionDocsTests(unittest.TestCase):
    def test_hwt_completion_matrix_closes_0506_0509_schedule(self) -> None:
        content = (PROJECT_ROOT / "references" / "hwt_m2_0506_0509_completion_matrix.md").read_text(encoding="utf-8")

        self.assertIn("Hu Wentao-side engineering work for the 5.6-5.9 Milestone 2 schedule is closed", content)
        self.assertIn("Staff -> Manager -> Executive -> Task", content)
        self.assertIn("Real API smoke", content)
        self.assertIn("Landing Page P0", content)
        self.assertIn("New employee onboarding", content)
        self.assertIn("M3/deployment/frontend/profile API", content)

    def test_onboarding_min_flow_uses_existing_task_api_without_new_m2_scope(self) -> None:
        content = (PROJECT_ROOT / "references" / "onboarding_information_completion_min_flow.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("POST /api/v1/agent/init", content)
        self.assertIn("POST /api/v1/tasks", content)
        self.assertIn("GET /api/v1/tasks", content)
        self.assertIn("PATCH /api/v1/tasks/{task_id}", content)
        self.assertIn("Idempotency-Key", content)
        self.assertIn("Full self-service onboarding UI and formal profile APIs are Milestone 3 work", content)

    def test_issue_log_and_landing_page_are_updated_to_59_closure_status(self) -> None:
        issue_log = (PROJECT_ROOT / "references" / "milestone2_issue_log.md").read_text(encoding="utf-8")
        landing_page = (PROJECT_ROOT / "references" / "landing_page_p0_p1_p2.md").read_text(encoding="utf-8")

        self.assertIn("HWT repository-level Milestone 2 work | Closed", issue_log)
        self.assertIn("No HWT repository-level blocker remains for Milestone 2", issue_log)
        self.assertIn("Done as M2 minimal flow", issue_log)
        self.assertIn("Ready for P0 contract", landing_page)
        self.assertIn("Recommended 5.9 wording", landing_page)


if __name__ == "__main__":
    unittest.main()
