from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from automage_agents.config.settings import RuntimeSettings
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
    settings = RuntimeSettings.from_env()
    if path is None:
        return settings

    raw = load_toml(path).get("runtime", {})
    return RuntimeSettings(
        environment=raw.get("environment", settings.environment),
        api_base_url=raw.get("api_base_url", settings.api_base_url),
        api_timeout_seconds=float(raw.get("api_timeout_seconds", settings.api_timeout_seconds)),
        retry_backoff_seconds=list(raw.get("retry_backoff_seconds", settings.retry_backoff_seconds)),
        max_schema_correction_attempts=int(
            raw.get("max_schema_correction_attempts", settings.max_schema_correction_attempts)
        ),
        auth_token=raw.get("auth_token", settings.auth_token),
        openclaw_enabled=bool(raw.get("openclaw_enabled", settings.openclaw_enabled)),
        feishu_enabled=bool(raw.get("feishu_enabled", settings.feishu_enabled)),
        feishu_app_id=raw.get("feishu_app_id", settings.feishu_app_id),
        feishu_app_secret=raw.get("feishu_app_secret", settings.feishu_app_secret),
    )


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
