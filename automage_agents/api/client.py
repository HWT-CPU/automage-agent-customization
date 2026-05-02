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

    def agent_init(self, identity: AgentIdentity) -> ApiResponse:
        # TODO(熊锦文): 确认 /api/v1/agent/init 的请求体、响应体、权限字段与错误码。
        return self.request("POST", "/api/v1/agent/init", json_body={"identity": identity.to_dict()})

    def post_staff_report(self, identity: AgentIdentity, report_payload: dict[str, Any]) -> ApiResponse:
        # TODO(熊锦文): 确认 /api/v1/report/staff 最终字段是否包含 role_id、node_id、user_id。
        payload = {"identity": identity.to_dict(), "report": report_payload}
        return self.request("POST", "/api/v1/report/staff", json_body=payload)

    def fetch_tasks(self, identity: AgentIdentity, status: str | None = None) -> ApiResponse:
        # TODO(熊锦文): 确认任务查询是否按 user_id、role_id、node_id 在后端物理隔离。
        query = {"user_id": identity.user_id, "role": identity.role.value, "node_id": identity.node_id}
        if status:
            query["status"] = status
        return self.request("GET", "/api/v1/tasks", query=query)

    def post_manager_report(self, identity: AgentIdentity, report_payload: dict[str, Any]) -> ApiResponse:
        # TODO(熊锦文): 确认 Manager 是否需要独立的部门日报读取接口和部门权限字段。
        payload = {"identity": identity.to_dict(), "report": report_payload}
        return self.request("POST", "/api/v1/report/manager", json_body=payload)

    def commit_decision(self, identity: AgentIdentity, decision_payload: dict[str, Any]) -> ApiResponse:
        # TODO(熊锦文): 确认 /api/v1/decision/commit 请求体与 task_queue 写入规则。
        payload = {"identity": identity.to_dict(), "decision": decision_payload}
        return self.request("POST", "/api/v1/decision/commit", json_body=payload)

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
