from __future__ import annotations

import json
import time
from dataclasses import asdict, is_dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from automage_agents.api.errors import ApiTransportError
from automage_agents.api.models import ApiResponse
from automage_agents.config.settings import RuntimeSettings
from automage_agents.core.models import AgentIdentity


class AutoMageApiClient:
    def __init__(self, settings: RuntimeSettings):
        self.settings = settings
        self.base_url = settings.api_base_url.rstrip("/")

    def request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> ApiResponse:
        url = self._build_url(path, query)
        body = self._encode_body(json_body)
        request_headers = self._build_headers(headers, body is not None)
        last_error: Exception | None = None

        for attempt, delay in enumerate([0, *self.settings.retry_backoff_seconds]):
            if delay:
                time.sleep(delay)
            try:
                return self._send_once(method, url, body, request_headers)
            except ApiTransportError as exc:
                last_error = exc
                if attempt >= len(self.settings.retry_backoff_seconds):
                    break

        raise ApiTransportError(f"API request failed after retries: {method} {url}") from last_error

    def agent_init(self, identity: AgentIdentity, runtime_context: dict[str, Any] | None = None) -> ApiResponse:
        payload = {"identity": identity.to_dict(), "context": runtime_context or {}}
        return self.request("POST", "/api/v1/agent/init", json_body=payload, headers=self._identity_headers(identity))

    def post_staff_report(
        self,
        identity: AgentIdentity,
        report_payload: dict[str, Any],
        runtime_context: dict[str, Any] | None = None,
    ) -> ApiResponse:
        payload = {"identity": identity.to_dict(), "report": report_payload}
        return self.request("POST", "/api/v1/report/staff", json_body=payload, headers=self._identity_headers(identity))

    def import_staff_daily_report_from_markdown(
        self,
        identity: AgentIdentity,
        import_payload: dict[str, Any],
        runtime_context: dict[str, Any] | None = None,
    ) -> ApiResponse:
        return self.request(
            "POST",
            "/api/v1/report/staff/import-markdown",
            json_body=import_payload,
            headers=self._identity_headers(identity),
        )

    def read_staff_daily_report(
        self,
        work_record_id: str,
        output_format: str = "json",
        identity: AgentIdentity | None = None,
    ) -> ApiResponse:
        headers = self._identity_headers(identity) if identity is not None else None
        return self.request("GET", f"/api/v1/report/staff/{work_record_id}", query={"format": output_format}, headers=headers)

    def fetch_work_records(
        self,
        identity: AgentIdentity,
        *,
        department_id: str | None = None,
        record_date_from: str | None = None,
        record_date_to: str | None = None,
        status: str | None = "submitted",
        limit: int = 20,
        cursor: str | None = None,
    ) -> ApiResponse:
        query = {
            "org_id": identity.metadata.get("org_id") or "org-001",
            "department_id": department_id or identity.department_id,
            "record_date": record_date_from or record_date_to,
            "user_id": identity.user_id if identity.role.value == "staff" else None,
        }
        return self.request("GET", "/api/v1/report/staff", query=query, headers=self._identity_headers(identity))

    def fetch_tasks(self, identity: AgentIdentity, status: str | None = None) -> ApiResponse:
        query = {"org_id": identity.metadata.get("org_id") or "org-001", "assignee_user_id": identity.user_id}
        if status:
            query["status"] = status
        return self.request("GET", "/api/v1/tasks", query=query, headers=self._identity_headers(identity))

    def update_task(
        self,
        identity: AgentIdentity,
        task_id: str,
        *,
        status: str | None = None,
        title: str | None = None,
        description: str | None = None,
        task_payload: dict[str, Any] | None = None,
    ) -> ApiResponse:
        payload = {
            "status": status,
            "title": title,
            "description": description,
            "task_payload": task_payload,
        }
        payload = {key: value for key, value in payload.items() if value is not None}
        return self.request("PATCH", f"/api/v1/tasks/{task_id}", json_body=payload, headers=self._identity_headers(identity))

    def create_task(
        self,
        identity: AgentIdentity,
        task_payload: dict[str, Any],
        runtime_context: dict[str, Any] | None = None,
    ) -> ApiResponse:
        payload = {"tasks": [task_payload]}
        return self.request("POST", "/api/v1/tasks", json_body=payload, headers=self._identity_headers(identity))

    def post_manager_report(
        self,
        identity: AgentIdentity,
        report_payload: dict[str, Any],
        runtime_context: dict[str, Any] | None = None,
    ) -> ApiResponse:
        payload = {"identity": identity.to_dict(), "report": report_payload}
        return self.request("POST", "/api/v1/report/manager", json_body=payload, headers=self._identity_headers(identity))

    def commit_decision(
        self,
        identity: AgentIdentity,
        decision_payload: dict[str, Any],
        runtime_context: dict[str, Any] | None = None,
    ) -> ApiResponse:
        payload = {"identity": identity.to_dict(), "decision": decision_payload}
        return self.request("POST", "/api/v1/decision/commit", json_body=payload, headers=self._identity_headers(identity))

    def run_dream(self, identity: AgentIdentity, summary_id: str) -> ApiResponse:
        return self.request(
            "POST",
            "/internal/dream/run",
            json_body={"summary_id": summary_id},
            headers=self._identity_headers(identity),
        )

    def _send_once(self, method: str, url: str, body: bytes | None, headers: dict[str, str]) -> ApiResponse:
        request = Request(url=url, data=body, headers=headers, method=method.upper())
        try:
            with urlopen(request, timeout=self.settings.api_timeout_seconds) as response:
                payload = self._read_json(response.read())
                return ApiResponse.from_payload(response.status, payload, dict(response.headers.items()))
        except HTTPError as exc:
            payload = self._read_json(exc.read())
            response = ApiResponse.from_payload(exc.code, payload, dict(exc.headers.items()))
            if exc.code >= 500:
                raise ApiTransportError(response.msg or f"Server error: {exc.code}") from exc
            return response
        except URLError as exc:
            raise ApiTransportError(str(exc.reason)) from exc
        except TimeoutError as exc:
            raise ApiTransportError("API request timed out") from exc

    def _build_url(self, path: str, query: dict[str, Any] | None) -> str:
        normalized_path = path if path.startswith("/") else f"/{path}"
        url = f"{self.base_url}{normalized_path}"
        if query:
            clean_query = {key: value for key, value in query.items() if value is not None}
            url = f"{url}?{urlencode(clean_query)}"
        return url

    def _build_headers(self, headers: dict[str, str] | None, has_body: bool) -> dict[str, str]:
        request_headers = {"Accept": "application/json"}
        if has_body:
            request_headers["Content-Type"] = "application/json"
        request_headers.update(self.settings.auth_headers())
        if headers:
            request_headers.update(headers)
        return request_headers

    def _encode_body(self, body: dict[str, Any] | None) -> bytes | None:
        if body is None:
            return None
        return json.dumps(self._to_jsonable(body), ensure_ascii=False).encode("utf-8")

    def _read_json(self, body: bytes) -> Any:
        if not body:
            return {}
        try:
            return json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            return body.decode("utf-8", errors="replace")

    def _to_jsonable(self, value: Any) -> Any:
        if is_dataclass(value):
            return asdict(value)
        if isinstance(value, dict):
            return {key: self._to_jsonable(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._to_jsonable(item) for item in value]
        if hasattr(value, "value"):
            return value.value
        return value

    def _identity_headers(self, identity: AgentIdentity) -> dict[str, str]:
        headers = {
            "X-User-Id": identity.user_id,
            "X-Role": identity.role.value,
            "X-Node-Id": identity.node_id,
            "X-Level": identity.level.value,
        }
        if identity.department_id:
            headers["X-Department-Id"] = identity.department_id
        if identity.manager_node_id:
            headers["X-Manager-Node-Id"] = identity.manager_node_id
        return headers
