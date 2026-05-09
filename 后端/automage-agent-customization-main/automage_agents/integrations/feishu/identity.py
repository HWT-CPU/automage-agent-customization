from __future__ import annotations

from automage_agents.core.models import UserProfile


def build_feishu_user_mapping(profiles: list[UserProfile]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for profile in profiles:
        open_id = str(profile.identity.metadata.get("feishu_open_id") or "").strip()
        if open_id and open_id.upper() != "TODO":
            mapping[open_id] = profile.identity.user_id
    return mapping
