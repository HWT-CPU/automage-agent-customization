from __future__ import annotations

from typing import Any

from automage_agents.api.client import AutoMageApiClient
from automage_agents.api.mock_client import MockAutoMageApiClient, MockBackendState
from automage_agents.api.sqlalchemy_client import SqlAlchemyAutoMageApiClient
from automage_agents.config.settings import RuntimeSettings
from automage_agents.db import create_session_factory


def create_api_client(
    settings: RuntimeSettings,
    *,
    mock_state: MockBackendState | None = None,
) -> Any:
    mode = settings.backend_mode.strip().lower()
    if mode == "mock":
        return MockAutoMageApiClient(mock_state or MockBackendState())
    if mode == "sqlalchemy":
        return SqlAlchemyAutoMageApiClient(create_session_factory(settings.postgres))
    return AutoMageApiClient(settings)
