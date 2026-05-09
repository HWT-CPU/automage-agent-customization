from __future__ import annotations

from automage_agents.core.models import InternalEvent, SkillResult
from automage_agents.integrations.router import InternalEventRouter


class OpenClawAdapter:
    def __init__(self, router: InternalEventRouter):
        self.router = router

    def handle_event(self, event: InternalEvent) -> SkillResult:
        # TODO(OpenClaw): Replace direct router call with real OpenClaw plugin/channel lifecycle when confirmed.
        return self.router.route(event)
