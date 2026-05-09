from __future__ import annotations

import unittest

from automage_agents.api.models import ApiResponse
from automage_agents.skills.result import api_response_to_skill_result


class SkillResultTests(unittest.TestCase):
    def test_conflict_response_maps_to_conflict_error_code(self) -> None:
        result = api_response_to_skill_result(
            ApiResponse.from_payload(
                409,
                {
                    "code": 409,
                    "msg": "员工日报提交冲突",
                    "error": {
                        "error_code": "staff_report_conflict",
                        "message": "同一员工同一日期的日报已存在，且内容不一致",
                    },
                },
            )
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.error_code, "conflict")
        self.assertEqual(result.message, "员工日报提交冲突")

    def test_rate_limited_response_maps_to_rate_limited_error_code(self) -> None:
        result = api_response_to_skill_result(ApiResponse.from_payload(429, {"detail": "rate_limit_exceeded"}))

        self.assertFalse(result.ok)
        self.assertEqual(result.error_code, "rate_limited")


if __name__ == "__main__":
    unittest.main()
