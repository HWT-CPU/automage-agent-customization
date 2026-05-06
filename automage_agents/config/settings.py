from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(slots=True)
class PostgresSettings:
    host: str = "localhost"
    port: int = 5432
    database: str = "automage"
    user: str = "automage"
    password: str | None = None
    sslmode: str = "prefer"

    @classmethod
    def from_env(cls, prefix: str = "AUTOMAGE_DB_") -> "PostgresSettings":
        return cls(
            host=os.getenv(f"{prefix}HOST", "localhost"),
            port=int(os.getenv(f"{prefix}PORT", "5432")),
            database=os.getenv(f"{prefix}NAME", "automage"),
            user=os.getenv(f"{prefix}USER", "automage"),
            password=os.getenv(f"{prefix}PASSWORD"),
            sslmode=os.getenv(f"{prefix}SSLMODE", "prefer"),
        )

    def dsn(self) -> str:
        password = self.password or ""
        return (
            f"postgresql://{self.user}:{password}@{self.host}:{self.port}/"
            f"{self.database}?sslmode={self.sslmode}"
        )


@dataclass(slots=True)
class RuntimeSettings:
    environment: str = "local"
    backend_mode: str = "http"
    audit_enabled: bool = True
    audit_org_id: int = 0
    api_base_url: str = "http://localhost:8000"
    api_timeout_seconds: float = 10.0
    retry_backoff_seconds: list[float] = field(default_factory=lambda: [1, 2, 4, 8, 16])
    max_schema_correction_attempts: int = 2
    auth_token: str | None = None
    openclaw_enabled: bool = False
    feishu_enabled: bool = False
    feishu_app_id: str | None = None
    feishu_app_secret: str | None = None
    postgres: PostgresSettings = field(default_factory=PostgresSettings)

    @classmethod
    def from_env(cls, prefix: str = "AUTOMAGE_") -> "RuntimeSettings":
        return cls(
            environment=os.getenv(f"{prefix}ENV", "local"),
            backend_mode=os.getenv(f"{prefix}BACKEND_MODE", "http"),
            audit_enabled=os.getenv(f"{prefix}AUDIT_ENABLED", "true").lower() == "true",
            audit_org_id=int(os.getenv(f"{prefix}AUDIT_ORG_ID", "0")),
            api_base_url=os.getenv(f"{prefix}API_BASE_URL", "http://localhost:8000"),
            api_timeout_seconds=float(os.getenv(f"{prefix}API_TIMEOUT_SECONDS", "10")),
            max_schema_correction_attempts=int(os.getenv(f"{prefix}MAX_SCHEMA_CORRECTION_ATTEMPTS", "2")),
            auth_token=os.getenv(f"{prefix}AUTH_TOKEN"),
            openclaw_enabled=os.getenv(f"{prefix}OPENCLAW_ENABLED", "false").lower() == "true",
            feishu_enabled=os.getenv(f"{prefix}FEISHU_ENABLED", "false").lower() == "true",
            feishu_app_id=os.getenv(f"{prefix}FEISHU_APP_ID"),
            feishu_app_secret=os.getenv(f"{prefix}FEISHU_APP_SECRET"),
            postgres=PostgresSettings.from_env(),
        )

    def auth_headers(self) -> dict[str, str]:
        # TODO: confirm the final auth mechanism for backend requests.
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}
