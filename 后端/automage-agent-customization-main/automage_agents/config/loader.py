from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

from automage_agents.config.settings import PostgresSettings, RuntimeSettings
from automage_agents.core.enums import AgentLevel, AgentRole
from automage_agents.core.exceptions import ConfigurationError, UserProfileError
from automage_agents.core.models import AgentIdentity, UserProfile


_REQUIRED_USER_FIELDS = {
    "node_id",
    "user_id",
    "role",
    "level",
    "display_name",
    "job_title",
}


def load_toml(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigurationError(f"Config file not found: {config_path}")
    with config_path.open("rb") as file:
        return tomllib.load(file)


def load_runtime_settings(path: str | Path | None = None) -> RuntimeSettings:
    config_override = os.getenv("AUTOMAGE_CONFIG_PATH", "").strip()
    if config_override:
        path = config_override
    settings = RuntimeSettings.from_env()
    if path is None:
        return settings

    config_path = Path(path)
    if not config_path.exists():
        return settings
    config = load_toml(config_path)
    raw = config.get("runtime", {})
    database = config.get("database", {})
    postgres_raw = config.get("postgres", {})
    postgres = PostgresSettings(
        host=postgres_raw.get("host") or database.get("host") or settings.postgres.host,
        port=int(postgres_raw.get("port", database.get("port", settings.postgres.port))),
        database=postgres_raw.get("database") or database.get("name") or settings.postgres.database,
        user=postgres_raw.get("user") or database.get("user") or settings.postgres.user,
        password=postgres_raw.get("password") or database.get("password") or settings.postgres.password,
        sslmode=postgres_raw.get("sslmode", settings.postgres.sslmode),
    )
    return RuntimeSettings(
        environment=raw.get("environment", settings.environment),
        backend_mode=raw.get("backend_mode", settings.backend_mode),
        audit_enabled=_bool(raw.get("audit_enabled", settings.audit_enabled)),
        audit_org_id=int(raw.get("audit_org_id", settings.audit_org_id)),
        auth_enabled=_bool(raw.get("auth_enabled", settings.auth_enabled)),
        scheduler_enabled=_bool(raw.get("scheduler_enabled", settings.scheduler_enabled)),
        scheduler_timezone=raw.get("scheduler_timezone", settings.scheduler_timezone),
        scheduler_jobs=list(raw.get("scheduler_jobs", settings.scheduler_jobs)),
        scheduler_task_record_limit=int(raw.get("scheduler_task_record_limit", settings.scheduler_task_record_limit)),
        rbac_enabled=_bool(raw.get("rbac_enabled", settings.rbac_enabled)),
        abuse_protection_enabled=_bool(raw.get("abuse_protection_enabled", settings.abuse_protection_enabled)),
        abuse_protection_backend=str(raw.get("abuse_protection_backend", settings.abuse_protection_backend)),
        rate_limit_window_seconds=int(raw.get("rate_limit_window_seconds", settings.rate_limit_window_seconds)),
        rate_limit_max_requests=int(raw.get("rate_limit_max_requests", settings.rate_limit_max_requests)),
        idempotency_ttl_seconds=int(raw.get("idempotency_ttl_seconds", settings.idempotency_ttl_seconds)),
        redis_url=raw.get("redis_url", settings.redis_url),
        redis_key_prefix=str(raw.get("redis_key_prefix", settings.redis_key_prefix)),
        write_protected_paths=list(raw.get("write_protected_paths", settings.write_protected_paths)),
        api_base_url=raw.get("api_base_url", settings.api_base_url),
        api_timeout_seconds=float(raw.get("api_timeout_seconds", settings.api_timeout_seconds)),
        retry_backoff_seconds=list(raw.get("retry_backoff_seconds", settings.retry_backoff_seconds)),
        max_schema_correction_attempts=int(
            raw.get("max_schema_correction_attempts", settings.max_schema_correction_attempts)
        ),
        auth_token=raw.get("auth_token", settings.auth_token),
        openclaw_enabled=bool(raw.get("openclaw_enabled", settings.openclaw_enabled)),
        feishu_enabled=bool(raw.get("feishu_enabled", settings.feishu_enabled)),
        feishu_app_id=raw.get("feishu_app_id") or settings.feishu_app_id,
        feishu_app_secret=raw.get("feishu_app_secret") or settings.feishu_app_secret,
        feishu_event_mode=raw.get("feishu_event_mode") or settings.feishu_event_mode,
        database_driver=database.get("driver") or settings.database_driver,
        database_host=database.get("host") or postgres_raw.get("host") or settings.database_host,
        database_port=int(database.get("port", postgres_raw.get("port", settings.database_port))),
        database_name=database.get("name") or postgres_raw.get("database") or settings.database_name,
        database_user=database.get("user") or postgres_raw.get("user") or settings.database_user,
        database_password=database.get("password") or postgres_raw.get("password") or settings.database_password,
        postgres=postgres,
    )


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def build_user_profile(raw: dict[str, Any]) -> UserProfile:
    missing = sorted(_REQUIRED_USER_FIELDS - set(raw))
    if missing:
        raise UserProfileError(f"Missing required user profile fields: {', '.join(missing)}")

    identity = AgentIdentity(
        node_id=str(raw["node_id"]),
        user_id=str(raw["user_id"]),
        role=AgentRole(str(raw["role"])),
        level=AgentLevel(str(raw["level"])),
        department_id=raw.get("department_id"),
        manager_node_id=raw.get("manager_node_id"),
        metadata=dict(raw.get("metadata", {})),
    )
    return UserProfile(
        identity=identity,
        display_name=str(raw["display_name"]),
        job_title=str(raw["job_title"]),
        responsibilities=list(raw.get("responsibilities", [])),
        input_sources=list(raw.get("input_sources", [])),
        output_requirements=list(raw.get("output_requirements", [])),
        personalized_context=str(raw.get("personalized_context", "")),
        permission_notes=list(raw.get("permission_notes", [])),
    )


def load_user_profile_toml(path: str | Path) -> UserProfile:
    raw = load_toml(path).get("user", {})
    return build_user_profile(raw)
