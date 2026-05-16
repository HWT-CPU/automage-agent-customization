from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def _env(name: str, default: str | None = None, prefix: str = "AUTOMAGE_") -> str | None:
    return os.getenv(f"{prefix}{name}") or os.getenv(name) or default


@dataclass(slots=True)
class PostgresSettings:
    host: str = "localhost"
    port: int = 5432
    database: str = "automage"
    user: str = "automage"
    password: str | None = None
    sslmode: str = "prefer"

    @classmethod
    def from_env(cls) -> "PostgresSettings":
        return cls(
            host=os.getenv("AUTOMAGE_DB_HOST") or os.getenv("AUTOMAGE_DATABASE_HOST") or "localhost",
            port=int(os.getenv("AUTOMAGE_DB_PORT") or os.getenv("AUTOMAGE_DATABASE_PORT") or "5432"),
            database=os.getenv("AUTOMAGE_DB_NAME") or os.getenv("AUTOMAGE_DATABASE_NAME") or "automage",
            user=os.getenv("AUTOMAGE_DB_USER") or os.getenv("AUTOMAGE_DATABASE_USER") or "automage",
            password=os.getenv("AUTOMAGE_DB_PASSWORD") or os.getenv("AUTOMAGE_DATABASE_PASSWORD"),
            sslmode=os.getenv("AUTOMAGE_DB_SSLMODE") or "prefer",
        )

    def dsn(self) -> str:
        password = self.password or ""
        return f"postgresql://{self.user}:{password}@{self.host}:{self.port}/{self.database}?sslmode={self.sslmode}"


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
            {"name": "staff_daily_reminder_job", "interval_seconds": 300, "enabled": True},
            {"name": "manager_summary_reminder_job", "interval_seconds": 600, "enabled": True},
            {"name": "manager_summary_auto_generate_job", "interval_seconds": 600, "enabled": True},
        ]
    )
    scheduler_task_record_limit: int = 100
    rbac_enabled: bool = True
    abuse_protection_enabled: bool = False
    abuse_protection_backend: str = "memory"
    rate_limit_window_seconds: int = 60
    rate_limit_max_requests: int = 60
    idempotency_ttl_seconds: int = 300
    redis_url: str | None = None
    redis_key_prefix: str = "automage"
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
    feishu_event_mode: str = "mock"
    database_driver: str = "postgresql"
    database_host: str | None = None
    database_port: int = 5432
    database_name: str | None = None
    database_user: str | None = None
    database_password: str | None = None
    postgres: PostgresSettings = field(default_factory=PostgresSettings)

    @classmethod
    def from_env(cls, prefix: str = "AUTOMAGE_") -> "RuntimeSettings":
        _load_env_file(Path(__file__).resolve().parents[2] / ".env")
        scheduler_jobs_raw = _env("SCHEDULER_JOBS", "", prefix) or ""
        write_paths_raw = _env("WRITE_PROTECTED_PATHS", "", prefix) or ""
        return cls(
            environment=_env("ENV", "local", prefix) or "local",
            backend_mode=_env("BACKEND_MODE", "http", prefix) or "http",
            audit_enabled=(_env("AUDIT_ENABLED", "true", prefix) or "true").lower() == "true",
            audit_org_id=int(_env("AUDIT_ORG_ID", "0", prefix) or "0"),
            auth_enabled=(_env("AUTH_ENABLED", "false", prefix) or "false").lower() == "true",
            scheduler_enabled=(_env("SCHEDULER_ENABLED", "false", prefix) or "false").lower() == "true",
            scheduler_timezone=_env("SCHEDULER_TIMEZONE", "Asia/Shanghai", prefix) or "Asia/Shanghai",
            scheduler_jobs=_parse_scheduler_jobs(scheduler_jobs_raw),
            scheduler_task_record_limit=int(_env("SCHEDULER_TASK_RECORD_LIMIT", "100", prefix) or "100"),
            rbac_enabled=(_env("RBAC_ENABLED", "true", prefix) or "true").lower() == "true",
            abuse_protection_enabled=(_env("ABUSE_PROTECTION_ENABLED", "false", prefix) or "false").lower() == "true",
            abuse_protection_backend=(_env("ABUSE_PROTECTION_BACKEND", "memory", prefix) or "memory").lower(),
            rate_limit_window_seconds=int(_env("RATE_LIMIT_WINDOW_SECONDS", "60", prefix) or "60"),
            rate_limit_max_requests=int(_env("RATE_LIMIT_MAX_REQUESTS", "60", prefix) or "60"),
            idempotency_ttl_seconds=int(_env("IDEMPOTENCY_TTL_SECONDS", "300", prefix) or "300"),
            redis_url=_env("REDIS_URL", prefix=prefix),
            redis_key_prefix=_env("REDIS_KEY_PREFIX", "automage", prefix) or "automage",
            write_protected_paths=_parse_write_protected_paths(write_paths_raw),
            api_base_url=_env("API_BASE_URL", "http://localhost:8000", prefix) or "http://localhost:8000",
            api_timeout_seconds=float(_env("API_TIMEOUT_SECONDS", "10", prefix) or "10"),
            max_schema_correction_attempts=int(_env("MAX_SCHEMA_CORRECTION_ATTEMPTS", "2", prefix) or "2"),
            auth_token=_env("AUTH_TOKEN", prefix=prefix),
            openclaw_enabled=(_env("OPENCLAW_ENABLED", "false", prefix) or "false").lower() == "true",
            feishu_enabled=(_env("FEISHU_ENABLED", "false", prefix) or "false").lower() == "true",
            feishu_app_id=_env("FEISHU_APP_ID", prefix=prefix),
            feishu_app_secret=_env("FEISHU_APP_SECRET", prefix=prefix),
            feishu_event_mode=_env("FEISHU_EVENT_MODE", "mock", prefix) or "mock",
            database_driver=_env("DATABASE_DRIVER", "postgresql", prefix) or "postgresql",
            database_host=_env("DATABASE_HOST", prefix=prefix),
            database_port=int(_env("DATABASE_PORT", "5432", prefix) or "5432"),
            database_name=_env("DATABASE_NAME", prefix=prefix),
            database_user=_env("DATABASE_USER", prefix=prefix),
            database_password=_env("DATABASE_PASSWORD", prefix=prefix),
            postgres=PostgresSettings.from_env(),
        )

    def auth_headers(self) -> dict[str, str]:
        # TODO(熊锦文): 确认最终鉴权方式，是 Bearer Token、API Key、签名，还是 role_id 物理隔离。
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}

    def database_configured(self) -> bool:
        legacy_configured = bool(self.database_host and self.database_name and self.database_user and self.database_password)
        postgres_configured = bool(self.postgres.host and self.postgres.database and self.postgres.user and self.postgres.password)
        return legacy_configured or postgres_configured


def _parse_scheduler_jobs(raw: str) -> list[dict[str, Any]]:
    if not raw:
        return [
            {"name": "staff_daily_reminder_job", "interval_seconds": 300, "enabled": True},
            {"name": "manager_summary_reminder_job", "interval_seconds": 600, "enabled": True},
            {"name": "manager_summary_auto_generate_job", "interval_seconds": 600, "enabled": True},
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
