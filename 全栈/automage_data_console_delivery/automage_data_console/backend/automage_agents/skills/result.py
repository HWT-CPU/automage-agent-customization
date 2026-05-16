from __future__ import annotations

from automage_agents.api.models import ApiResponse
from automage_agents.core.models import SkillResult


def api_response_to_skill_result(response: ApiResponse, success_message: str = "success") -> SkillResult:
    if response.ok:
        data = response.data if isinstance(response.data, dict) else {"items": response.data or []}
        return SkillResult(ok=True, data=data, message=response.msg or success_message)

    if response.status_code == 401:
        return SkillResult(ok=False, data={"response": response.raw}, message=response.msg, error_code="auth_failed")
    if response.status_code == 403:
        return SkillResult(ok=False, data={"response": response.raw}, message=response.msg, error_code="permission_denied")
    if response.status_code == 409:
        return SkillResult(ok=False, data={"response": response.raw}, message=response.msg, error_code="conflict")
    if response.status_code == 429:
        return SkillResult(ok=False, data={"response": response.raw}, message=response.msg, error_code="rate_limited")
    if response.status_code == 422:
        return SkillResult(ok=False, data={"response": response.raw}, message=response.msg, error_code="schema_validation_failed")
    if response.status_code >= 500:
        return SkillResult(ok=False, data={"response": response.raw}, message=response.msg, error_code="server_error")
    return SkillResult(ok=False, data={"response": response.raw}, message=response.msg, error_code="api_error")
