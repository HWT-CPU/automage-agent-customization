from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeSettings:
    environment: str = "local"
    api_base_url: str = "http://localhost:8000"
    api_timeout_seconds: float = 10.0
    retry_backoff_seconds: list[float] = field(default_factory=lambda: [1, 2, 4, 8, 16])
    max_schema_correction_attempts: int = 2
    auth_token: str | None = None
    openclaw_enabled: bool = False
    feishu_enabled: bool = False
    feishu_app_id: str | None = None
    feishu_app_secret: str | None = None

    @classmethod
    def from_env(cls, prefix: str = "AUTOMAGE_") -> "RuntimeSettings":
        return cls(
            environment=os.getenv(f"{prefix}ENV", "local"),
            api_base_url=os.getenv(f"{prefix}API_BASE_URL", "http://localhost:8000"),
            api_timeout_seconds=float(os.getenv(f"{prefix}API_TIMEOUT_SECONDS", "10")),
            max_schema_correction_attempts=int(os.getenv(f"{prefix}MAX_SCHEMA_CORRECTION_ATTEMPTS", "2")),
            auth_token=os.getenv(f"{prefix}AUTH_TOKEN"),
            openclaw_enabled=os.getenv(f"{prefix}OPENCLAW_ENABLED", "false").lower() == "true",
            feishu_enabled=os.getenv(f"{prefix}FEISHU_ENABLED", "false").lower() == "true",
            feishu_app_id=os.getenv(f"{prefix}FEISHU_APP_ID"),
            feishu_app_secret=os.getenv(f"{prefix}FEISHU_APP_SECRET"),
        )

    def auth_headers(self) -> dict[str, str]:
        # TODO(熊锦文): 确认最终鉴权方式，是 Bearer Token、API Key、签名，还是 role_id 物理隔离。
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}
