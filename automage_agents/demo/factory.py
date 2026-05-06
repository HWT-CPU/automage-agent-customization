from __future__ import annotations

from dataclasses import dataclass

from automage_agents.api import create_api_client
from automage_agents.api.mock_client import MockBackendState
from automage_agents.config.loader import load_runtime_settings, load_user_profile_toml
from automage_agents.skills.context import SkillContext


@dataclass(slots=True)
class DemoContexts:
    state: MockBackendState | None
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
    state = MockBackendState() if settings.backend_mode.strip().lower() == "mock" else None
    client = create_api_client(settings, mock_state=state)

    staff = SkillContext.from_user_profile(
        settings,
        load_user_profile_toml(staff_user_path),
        mock_state=state,
        api_client=client,
    )
    manager = SkillContext.from_user_profile(
        settings,
        load_user_profile_toml(manager_user_path),
        mock_state=state,
        api_client=client,
    )
    executive = SkillContext.from_user_profile(
        settings,
        load_user_profile_toml(executive_user_path),
        mock_state=state,
        api_client=client,
    )
    return DemoContexts(state=state, staff=staff, manager=manager, executive=executive)
