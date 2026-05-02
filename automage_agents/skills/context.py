from __future__ import annotations

from dataclasses import dataclass

from automage_agents.api.client import AutoMageApiClient
from automage_agents.config.settings import RuntimeSettings
from automage_agents.core.models import AgentIdentity, UserProfile


@dataclass(slots=True)
class SkillContext:
    settings: RuntimeSettings
    api_client: AutoMageApiClient
    user_profile: UserProfile

    @property
    def identity(self) -> AgentIdentity:
        return self.user_profile.identity

    @classmethod
    def from_user_profile(cls, settings: RuntimeSettings, user_profile: UserProfile) -> "SkillContext":
        return cls(settings=settings, api_client=AutoMageApiClient(settings), user_profile=user_profile)
