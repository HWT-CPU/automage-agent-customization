"""Backend API client layer for AutoMage-2 agent skills."""

from automage_agents.api.client import AutoMageApiClient
from automage_agents.api.factory import create_api_client
from automage_agents.api.mock_client import MockAutoMageApiClient, MockBackendState
from automage_agents.api.models import ApiResponse
from automage_agents.api.sqlalchemy_client import SqlAlchemyAutoMageApiClient

__all__ = [
    "ApiResponse",
    "AutoMageApiClient",
    "MockAutoMageApiClient",
    "MockBackendState",
    "SqlAlchemyAutoMageApiClient",
    "create_api_client",
]
