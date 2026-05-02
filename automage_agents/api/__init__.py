"""Backend API client layer for AutoMage-2 agent skills."""

from automage_agents.api.client import AutoMageApiClient
from automage_agents.api.mock_client import MockAutoMageApiClient, MockBackendState
from automage_agents.api.models import ApiResponse

__all__ = ["ApiResponse", "AutoMageApiClient", "MockAutoMageApiClient", "MockBackendState"]
