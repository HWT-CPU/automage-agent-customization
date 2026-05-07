from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any


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
    auth_enabled: bool = False
    scheduler_enabled: bool = False
    scheduler_timezone: str = "Asia/Shanghai"
    scheduler_jobs: list[dict[str, Any]] = field(
        default_factory=lambda: [
            {
                "name": "staff_daily_reminder_job",
                "interval_seconds": 300,
                "enabled": True,
            },
            {
                "name": "manager_summary_reminder_job",
                "interval_seconds": 600,
                "enabled": True,
            },
        ]
    )
    scheduler_task_record_limit: int = 100
    rbac_enabled: bool = True
    abuse_protection_enabled: bool = False
    rate_limit_window_seconds: int = 60
    rate_limit_max_requests: int = 60
    idempotency_ttl_seconds: int = 300
    write_protected_paths: list[str] = field(
        default_factory=lambda: [
            "/api/v1/report/staff",
            "/api/v1/report/manager",
            "/api/v1/decision/commit",
            "/api/v1/tasks",
        ]
    )
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
        scheduler_jobs_raw = os.getenv(f"{prefix}SCHEDULER_JOBS", "").strip()
        write_paths_raw = os.getenv(f"{prefix}WRITE_PROTECTED_PATHS", "").strip()
        return cls(
            environment=os.getenv(f"{prefix}ENV", "local"),
            backend_mode=os.getenv(f"{prefix}BACKEND_MODE", "http"),
            audit_enabled=os.getenv(f"{prefix}AUDIT_ENABLED", "true").lower() == "true",
            audit_org_id=int(os.getenv(f"{prefix}AUDIT_ORG_ID", "0")),
            auth_enabled=os.getenv(f"{prefix}AUTH_ENABLED", "false").lower() == "true",
            scheduler_enabled=os.getenv(f"{prefix}SCHEDULER_ENABLED", "false").lower() == "true",
            scheduler_timezone=os.getenv(f"{prefix}SCHEDULER_TIMEZONE", "Asia/Shanghai"),
            scheduler_jobs=_parse_scheduler_jobs(scheduler_jobs_raw),
            scheduler_task_record_limit=int(os.getenv(f"{prefix}SCHEDULER_TASK_RECORD_LIMIT", "100")),
            abuse_protection_enabled=os.getenv(f"{prefix}ABUSE_PROTECTION_ENABLED", "false").lower() == "true",
            rbac_enabled=os.getenv(f"{prefix}RBAC_ENABLED", "true").lower() == "true",
            rate_limit_window_seconds=int(os.getenv(f"{prefix}RATE_LIMIT_WINDOW_SECONDS", "60")),
            rate_limit_max_requests=int(os.getenv(f"{prefix}RATE_LIMIT_MAX_REQUESTS", "60")),
            idempotency_ttl_seconds=int(os.getenv(f"{prefix}IDEMPOTENCY_TTL_SECONDS", "300")),
            write_protected_paths=_parse_write_protected_paths(write_paths_raw),
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
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}


def _parse_scheduler_jobs(raw: str) -> list[dict[str, Any]]:
    if not raw:
        return [
            {
                "name": "staff_daily_reminder_job",
                "interval_seconds": 300,
                "enabled": True,
            },
            {
                "name": "manager_summary_reminder_job",
                "interval_seconds": 600,
                "enabled": True,
            },
        ]
    jobs: list[dict[str, Any]] = []
    for chunk in raw.split(","):
        name, _, interval = chunk.partition(":")
        name = name.strip()
        if not name:
            continue
        try:
            interval_seconds = int(interval.strip()) if interval.strip() else 300
        except ValueError:
            interval_seconds = 300
        jobs.append({"name": name, "interval_seconds": interval_seconds, "enabled": True})
    return jobs or [
        {"name": "staff_daily_reminder_job", "interval_seconds": 300, "enabled": True},
        {"name": "manager_summary_reminder_job", "interval_seconds": 600, "enabled": True},
    ]


def _parse_write_protected_paths(raw: str) -> list[str]:
    if not raw:
        return [
            "/api/v1/report/staff",
            "/api/v1/report/manager",
            "/api/v1/decision/commit",
            "/api/v1/tasks",
        ]
    return [item.strip() for item in raw.split(",") if item.strip()]
