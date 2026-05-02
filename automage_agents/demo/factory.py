from __future__ import annotations

from dataclasses import dataclass

from automage_agents.api.mock_client import MockAutoMageApiClient, MockBackendState
from automage_agents.config.loader import load_runtime_settings, load_user_profile_toml
from automage_agents.skills.context import SkillContext


@dataclass(slots=True)
class DemoContexts:
    state: MockBackendState
    staff: SkillContext
    manager: SkillContext
    executive: SkillContext


def build_demo_contexts(
    staff_user_path: str,
    manager_user_path: str,
    executive_user_path: str,
    settings_path: str = "configs/automage.example.toml",
) -> DemoContexts:
    settings = load_runtime_settings(settings_path)
    state = MockBackendState()
    client = MockAutoMageApiClient(state)

    staff = SkillContext(settings=settings, api_client=client, user_profile=load_user_profile_toml(staff_user_path))
    manager = SkillContext(settings=settings, api_client=client, user_profile=load_user_profile_toml(manager_user_path))
    executive = SkillContext(settings=settings, api_client=client, user_profile=load_user_profile_toml(executive_user_path))
    return DemoContexts(state=state, staff=staff, manager=manager, executive=executive)
