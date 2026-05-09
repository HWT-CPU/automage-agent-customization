from __future__ import annotations

from dataclasses import dataclass, field

from automage_agents.api import create_api_client
from automage_agents.api.mock_client import MockBackendState
from automage_agents.config.settings import RuntimeSettings
from automage_agents.core.models import AgentIdentity, RuntimeContextV0, UserProfile


@dataclass(slots=True)
class SkillContext:
    settings: RuntimeSettings
    api_client: object
    user_profile: UserProfile
    runtime: RuntimeContextV0 = field(default_factory=RuntimeContextV0)

    @property
    def identity(self) -> AgentIdentity:
        return self.user_profile.identity

    def runtime_payload(self) -> dict:
        return self.runtime.to_dict(self.identity)

    @classmethod
    def from_user_profile(
        cls,
        settings: RuntimeSettings,
        user_profile: UserProfile,
        *,
        mock_state: MockBackendState | None = None,
        api_client: object | None = None,
        runtime: RuntimeContextV0 | None = None,
    ) -> "SkillContext":
        client = api_client if api_client is not None else create_api_client(settings, mock_state=mock_state)
        return cls(settings=settings, api_client=client, user_profile=user_profile, runtime=runtime or RuntimeContextV0())
