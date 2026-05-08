from __future__ import annotations

import unittest

from scripts.smoke_real_api import _build_checks, _public_check


class SmokeRealApiPlanTests(unittest.TestCase):
    def test_real_api_smoke_plan_covers_m2_write_chain_with_idempotency(self) -> None:
        checks = _build_checks("hwt-m2-0508")
        by_name = {check["name"]: check for check in checks}

        self.assertIn("post_staff_report", by_name)
        self.assertIn("post_manager_report", by_name)
        self.assertIn("commit_decision", by_name)
        self.assertIn("post_tasks", by_name)
        self.assertIn("patch_task", by_name)

        for name in ["post_staff_report", "post_manager_report", "commit_decision", "post_tasks", "patch_task"]:
            self.assertIn("Idempotency-Key", by_name[name]["headers"])

        self.assertEqual(by_name["post_tasks"]["path"], "/api/v1/tasks")
        self.assertEqual(by_name["patch_task"]["method"], "PATCH")
        self.assertNotIn("--", by_name["patch_task"]["path"])

    def test_public_dry_run_plan_exposes_idempotency_configuration_without_secret_values(self) -> None:
        checks = _build_checks("hwt-m2-0508")
        public_checks = [_public_check(check) for check in checks]
        post_tasks = next(check for check in public_checks if check["name"] == "post_tasks")

        self.assertEqual(post_tasks["path"], "/api/v1/tasks")
        self.assertEqual(post_tasks["idempotency_key_configured"], True)
        self.assertNotIn("Idempotency-Key", post_tasks["identity_headers"])


if __name__ == "__main__":
    unittest.main()
