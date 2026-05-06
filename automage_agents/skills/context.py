from __future__ import annotations

from dataclasses import dataclass

from automage_agents.api import create_api_client
from automage_agents.api.mock_client import MockBackendState
from automage_agents.config.settings import RuntimeSettings
from automage_agents.core.models import AgentIdentity, UserProfile


@dataclass(slots=True)
class SkillContext:
    settings: RuntimeSettings
    api_client: object
    user_profile: UserProfile

    @property
    def identity(self) -> AgentIdentity:
        return self.user_profile.identity

    @classmethod
    def from_user_profile(
        cls,
        settings: RuntimeSettings,
        user_profile: UserProfile,
        *,
        mock_state: MockBackendState | None = None,
        api_client: object | None = None,
    ) -> "SkillContext":
        client = api_client if api_client is not None else create_api_client(settings, mock_state=mock_state)
        return cls(settings=settings, api_client=client, user_profile=user_profile)
