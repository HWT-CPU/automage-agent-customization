from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from automage_agents.core.models import InternalEvent, SkillResult
from automage_agents.demo.factory import DemoContexts, build_demo_contexts
from automage_agents.integrations.feishu.events import FeishuEvent, FeishuEventAdapter
from automage_agents.integrations.feishu.identity import build_feishu_user_mapping
from automage_agents.integrations.feishu.messages import FeishuMessageAdapter
from automage_agents.integrations.hermes.client import LocalHermesClient
from automage_agents.integrations.hermes.config import HermesConfig, load_hermes_config
from automage_agents.integrations.openclaw.adapter import OpenClawAdapter
from automage_agents.integrations.openclaw.client import LocalOpenClawClient
from automage_agents.integrations.openclaw.config import OpenClawConfig, load_openclaw_config
from automage_agents.integrations.openclaw.parser import OpenClawCommandParser
from automage_agents.integrations.router import InternalEventRouter
from automage_agents.skills.common import agent_init


@dataclass(slots=True)
class HermesOpenClawRuntime:
    contexts: DemoContexts
    router: InternalEventRouter
    openclaw: OpenClawAdapter
    feishu_events: FeishuEventAdapter
    feishu_messages: FeishuMessageAdapter
    hermes_client: LocalHermesClient | None = None
    openclaw_client: LocalOpenClawClient | None = None

    @property
    def staff_context(self):
        """获取 Staff Context - 用于 Agent Runtime API"""
        return self.contexts.staff

    @property
    def manager_context(self):
        """获取 Manager Context - 用于 Agent Runtime API"""
        return self.contexts.manager

    @property
    def executive_context(self):
        """获取 Executive Context - 用于 Agent Runtime API"""
        return self.contexts.executive

    @classmethod
    def from_settings(cls, settings: Any, user_mapping: dict[str, str] | None = None, auto_initialize: bool = True) -> "HermesOpenClawRuntime":
        """
        从 Settings 对象创建 Runtime
        
        Args:
            settings: 配置对象
            user_mapping: 用户映射
            auto_initialize: 是否自动初始化
        
        Returns:
            HermesOpenClawRuntime: Runtime 实例
        """
        # 使用默认配置路径
        return cls.from_config_files(
            hermes_config_path="configs/hermes.example.toml",
            openclaw_config_path="configs/openclaw.example.toml",
            user_mapping=user_mapping,
            auto_initialize=auto_initialize,
        )

    @classmethod
    def from_demo_configs(
        cls,
        staff_user_path: str = "examples/user.staff.example.toml",
        manager_user_path: str = "examples/user.manager.example.toml",
        executive_user_path: str = "examples/user.executive.example.toml",
        settings_path: str = "configs/automage.example.toml",
        user_mapping: dict[str, str] | None = None,
        auto_initialize: bool = True,
    ) -> "HermesOpenClawRuntime":
        contexts = build_demo_contexts(
            staff_user_path=staff_user_path,
            manager_user_path=manager_user_path,
            executive_user_path=executive_user_path,
            settings_path=settings_path,
        )
        if auto_initialize:
            for context in [contexts.staff, contexts.manager, contexts.executive]:
                agent_init(context)
        router = InternalEventRouter(contexts.staff, contexts.manager, contexts.executive)
        mapping = build_feishu_user_mapping([contexts.staff.user_profile, contexts.manager.user_profile, contexts.executive.user_profile])
        if user_mapping:
            mapping.update(user_mapping)
        return cls(
            contexts=contexts,
            router=router,
            openclaw=OpenClawAdapter(router),
            feishu_events=FeishuEventAdapter(user_mapping=mapping),
            feishu_messages=FeishuMessageAdapter(),
        )

    @classmethod
    def from_config_files(
        cls,
        hermes_config_path: str = "configs/hermes.example.toml",
        openclaw_config_path: str = "configs/openclaw.example.toml",
        user_mapping: dict[str, str] | None = None,
        auto_initialize: bool = True,
    ) -> "HermesOpenClawRuntime":
        hermes_config = load_hermes_config(hermes_config_path)
        openclaw_config = load_openclaw_config(openclaw_config_path)
        return cls.from_configs(hermes_config, openclaw_config, user_mapping=user_mapping, auto_initialize=auto_initialize)

    @classmethod
    def from_configs(
        cls,
        hermes_config: HermesConfig,
        openclaw_config: OpenClawConfig,
        user_mapping: dict[str, str] | None = None,
        auto_initialize: bool = True,
    ) -> "HermesOpenClawRuntime":
        runtime = cls.from_demo_configs(
            staff_user_path=hermes_config.staff.profile_path,
            manager_user_path=hermes_config.manager.profile_path,
            executive_user_path=hermes_config.executive.profile_path,
            settings_path=hermes_config.settings_path,
            user_mapping=user_mapping,
            auto_initialize=auto_initialize,
        )
        runtime.hermes_client = LocalHermesClient(runtime.contexts.staff, runtime.contexts.manager, runtime.contexts.executive)
        mapping = build_feishu_user_mapping(
            [runtime.contexts.staff.user_profile, runtime.contexts.manager.user_profile, runtime.contexts.executive.user_profile]
        )
        if user_mapping:
            mapping.update(user_mapping)
        runtime.openclaw_client = LocalOpenClawClient(
            hermes_client=runtime.hermes_client,
            parser=OpenClawCommandParser(openclaw_config),
            user_mapping=mapping,
        )
        return runtime

    def handle_internal_event(self, event: InternalEvent, reply_target_id: str | None = None) -> dict[str, Any]:
        result = self.openclaw.handle_event(event)
        return self._event_output(event, result, reply_target_id)

    def handle_feishu_event(self, event: FeishuEvent, reply_target_id: str | None = None) -> dict[str, Any]:
        internal_event = self.feishu_events.to_internal_event(event)
        return self.handle_internal_event(internal_event, reply_target_id)

    def handle_feishu_message_receive_v1(self, raw_event: dict[str, Any], reply_target_id: str | None = None) -> dict[str, Any]:
        event = self.feishu_events.from_message_receive_v1(raw_event)
        return self.handle_feishu_event(event, reply_target_id)

    def run_dream_decision(self, payload: dict[str, Any]) -> SkillResult:
        return self.router.run_dream_decision(payload)

    def state_summary(self) -> dict[str, int | bool]:
        state = self.contexts.state
        if state is None:
            return {"mock_state": False}
        return {
            "mock_state": True,
            "agent_sessions": len(state.agent_sessions),
            "staff_reports": len(state.staff_reports),
            "form_templates": len(state.form_templates),
            "work_records": len(state.work_records),
            "work_record_items": len(state.work_record_items),
            "manager_reports": len(state.manager_reports),
            "agent_decision_logs": len(state.agent_decision_logs),
            "decision_logs": len(state.decision_logs),
            "task_queue": len(state.task_queue),
            "audit_logs": len(state.audit_logs),
        }

    def _event_output(self, event: InternalEvent, result: SkillResult, reply_target_id: str | None) -> dict[str, Any]:
        target_id = reply_target_id or self._reply_target_from_event(event)
        reply = None
        if target_id:
            message = self.feishu_messages.build_processing_result_reply(target_id, event.event_type.value, result)
            reply = self.feishu_messages.send_message(message)
        return {
            "event_type": event.event_type.value,
            "source_channel": event.source_channel.value,
            "actor_user_id": event.actor_user_id,
            "correlation_id": event.correlation_id,
            "ok": result.ok,
            "message": result.message,
            "error_code": result.error_code,
            "data": result.data,
            "reply": reply,
        }

    def _reply_target_from_event(self, event: InternalEvent) -> str | None:
        resource_usage = event.payload.get("resource_usage", {})
        if isinstance(resource_usage, dict) and resource_usage.get("chat_id"):
            return str(resource_usage["chat_id"])
        return None
