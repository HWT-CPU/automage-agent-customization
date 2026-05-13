"""External integration adapters for OpenClaw, Feishu, and future channels."""

from automage_agents.integrations.hermes import HermesOpenClawRuntime
from automage_agents.integrations.production_loop import FeishuProductionLoop, ProductionLoopOptions

__all__ = ["FeishuProductionLoop", "HermesOpenClawRuntime", "ProductionLoopOptions"]
