from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ApiResponse:
    status_code: int
    code: int | str | None = None
    data: dict[str, Any] | list[Any] | None = None
    msg: str = ""
    headers: dict[str, str] = field(default_factory=dict)
    raw: Any = None

    @property
    def ok(self) -> bool:
        if self.code is None:
            return 200 <= self.status_code < 300
        return str(self.code).lower() in {"0", "200", "success", "ok"} and 200 <= self.status_code < 300

    @classmethod
    def from_payload(cls, status_code: int, payload: Any, headers: dict[str, str] | None = None) -> "ApiResponse":
        if isinstance(payload, dict):
            error = payload.get("error") if isinstance(payload.get("error"), dict) else {}
            return cls(
                status_code=status_code,
                code=payload.get("code", error.get("code")),
                data=payload.get("data"),
                msg=str(payload.get("msg", payload.get("message", error.get("message", "")))),
                headers=headers or {},
                raw=payload,
            )
        return cls(status_code=status_code, data=None, msg=str(payload), headers=headers or {}, raw=payload)
