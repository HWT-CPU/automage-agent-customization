from __future__ import annotations

from dataclasses import replace
from typing import Any

from automage_agents.core.enums import AgentRole
from automage_agents.core.enums import InternalEventType
from automage_agents.core.models import InternalEvent, SkillResult
from automage_agents.schemas.executive_v1 import coerce_task_v1_payload
from automage_agents.schemas.placeholders import ManagerReportDraft, StaffReportDraft
from automage_agents.skills.context import SkillContext
from automage_agents.skills.executive import commit_decision, dream_decision_engine
from automage_agents.skills.manager import generate_manager_report
from automage_agents.skills.staff import fetch_my_tasks, post_daily_report, update_my_task


class InternalEventRouter:
    def __init__(self, staff_context: SkillContext, manager_context: SkillContext, executive_context: SkillContext):
        self.staff_context = staff_context
        self.manager_context = manager_context
        self.executive_context = executive_context

    def route(self, event: InternalEvent) -> SkillResult:
        if event.event_type == InternalEventType.DAILY_REPORT_SUBMITTED:
            return post_daily_report(self._context_for_actor(self.staff_context, event.actor_user_id), self._build_staff_report(event.payload))
        if event.event_type == InternalEventType.TASK_QUERY_REQUESTED:
            return fetch_my_tasks(self._context_for_actor(self.staff_context, event.actor_user_id), status=event.payload.get("status"))
        if event.event_type in {InternalEventType.TASK_UPDATE_REQUESTED, InternalEventType.TASK_COMPLETED}:
            if not str(event.payload.get("task_id") or "").strip():
                return SkillResult(ok=False, data=event.payload, message="更新任务需要提供任务 ID。", error_code="schema_validation_failed")
            status = event.payload.get("status") or ("completed" if event.event_type == InternalEventType.TASK_COMPLETED else None)
            return update_my_task(
                self._context_for_actor(self.staff_context, event.actor_user_id),
                str(event.payload["task_id"]),
                status=status,
                title=event.payload.get("title"),
                description=event.payload.get("description"),
                task_payload=event.payload.get("task_payload"),
            )
        if event.event_type == InternalEventType.MANAGER_FEEDBACK_SUBMITTED:
            return generate_manager_report(self.manager_context, self._build_manager_report(event.payload))
        if event.event_type == InternalEventType.DREAM_DECISION_REQUESTED:
            if not self._actor_has_role(event.actor_user_id, AgentRole.EXECUTIVE):
                return self._permission_denied(event, "只有 Executive 账号可以生成 Dream 决策草案。")
            if not event.payload.get("summary_id") and not event.payload.get("source_summary_id"):
                return SkillResult(ok=False, data=event.payload, message="生成决策草案需要提供 Manager 汇总 ID。", error_code="schema_validation_failed")
            return dream_decision_engine(self._context_for_actor(self.executive_context, event.actor_user_id), event.payload)
        if event.event_type == InternalEventType.EXECUTIVE_DECISION_SELECTED:
            if not self._actor_has_role(event.actor_user_id, AgentRole.EXECUTIVE):
                return self._permission_denied(event, "只有 Executive 账号可以确认高层决策。")
            return self._commit_executive_decision(event.payload, event.actor_user_id)
        if event.event_type == InternalEventType.AUTH_FAILED:
            return SkillResult(ok=False, data=event.payload, message="Auth failed event received.", error_code="auth_failed")
        return SkillResult(ok=False, data=event.payload, message="Unsupported event type.", error_code="unsupported_event")

    def _context_for_actor(self, base_context: SkillContext, actor_user_id: str) -> SkillContext:
        actor = str(actor_user_id or "").strip()
        if not actor or actor == base_context.identity.user_id:
            return base_context
        identity = replace(
            base_context.identity,
            user_id=actor,
            node_id=f"{base_context.identity.role.value}-node-{actor}",
            metadata={**dict(base_context.identity.metadata), "routed_actor_user_id": actor},
        )
        user_profile = replace(base_context.user_profile, identity=identity, display_name=actor)
        return SkillContext(
            settings=base_context.settings,
            api_client=base_context.api_client,
            user_profile=user_profile,
            runtime=base_context.runtime,
        )

    def run_dream_decision(self, payload: dict[str, Any]) -> SkillResult:
        return dream_decision_engine(self.executive_context, payload)

    def _actor_has_role(self, actor_user_id: str, role: AgentRole) -> bool:
        actor = str(actor_user_id or "").strip()
        role_by_user_id = {
            self.staff_context.identity.user_id: self.staff_context.identity.role,
            self.manager_context.identity.user_id: self.manager_context.identity.role,
            self.executive_context.identity.user_id: self.executive_context.identity.role,
        }
        return role_by_user_id.get(actor) == role

    def _permission_denied(self, event: InternalEvent, message: str) -> SkillResult:
        return SkillResult(
            ok=False,
            data={
                "actor_user_id": event.actor_user_id,
                "event_type": event.event_type.value,
                **event.payload,
            },
            message=message,
            error_code="permission_denied",
        )

    def _commit_executive_decision(self, payload: dict[str, Any], actor_user_id: str | None = None) -> SkillResult:
        executive_context = self._context_for_actor(self.executive_context, actor_user_id or self.executive_context.identity.user_id)
        summary_id = payload.get("summary_id") or payload.get("source_summary_id")
        option_id = str(payload.get("selected_option_id") or payload.get("selected_option_key") or "A").strip().upper()
        if not summary_id:
            return commit_decision(executive_context, payload)
        dream_result = dream_decision_engine(executive_context, {"summary_id": str(summary_id)})
        if not dream_result.ok:
            return dream_result
        decision_payload = self._build_decision_from_dream(dream_result.data, payload, option_id, executive_context)
        return commit_decision(executive_context, decision_payload)

    def _build_decision_from_dream(self, dream_data: dict[str, Any], payload: dict[str, Any], option_id: str, executive_context: SkillContext) -> dict[str, Any]:
        options = list(dream_data.get("decision_options") or [])
        selected_option = next((option for option in options if str(option.get("option_id")).upper() == option_id), None)
        if selected_option is None and options:
            selected_option = options[0]
        selected_option = selected_option or {"option_id": option_id, "title": f"方案 {option_id}", "task_candidates": []}
        summary_public_id = str(
            payload.get("summary_id")
            or payload.get("source_summary_id")
            or dream_data.get("summary_public_id")
            or dream_data.get("summary_id")
            or ""
        )
        task_candidates = [self._normalize_task_candidate(task, payload, summary_public_id, executive_context) for task in selected_option.get("task_candidates", [])]
        return {
            "org_id": payload.get("org_id") or self._context_org_id(executive_context),
            "department_id": payload.get("department_id") or executive_context.identity.department_id,
            "summary_id": summary_public_id,
            "title": payload.get("title") or f"确认{selected_option.get('title') or f'方案 {option_id}'}",
            "decision_summary": payload.get("decision_summary") or selected_option.get("summary") or f"确认执行方案 {option_id}",
            "selected_option_id": selected_option.get("option_id") or option_id,
            "selected_option_label": selected_option.get("title") or f"方案 {option_id}",
            "decision_options": options,
            "priority": payload.get("priority") or "high",
            "task_candidates": task_candidates,
            "meta": self._decision_meta(payload),
        }

    def _normalize_task_candidate(self, task: dict[str, Any], payload: dict[str, Any], summary_public_id: str, executive_context: SkillContext) -> dict[str, Any]:
        normalized = dict(task)
        normalized["org_id"] = payload.get("org_id") or self._context_org_id(executive_context)
        normalized["department_id"] = payload.get("department_id") or executive_context.identity.department_id
        normalized.setdefault("source_summary_id", summary_public_id)
        normalized.setdefault("creator_user_id", executive_context.identity.user_id)
        normalized.setdefault("created_by_node_id", executive_context.identity.node_id)
        normalized.setdefault("manager_user_id", payload.get("manager_user_id") or self.manager_context.identity.user_id)
        normalized.setdefault("manager_node_id", payload.get("manager_node_id") or self.manager_context.identity.node_id)
        assignee_user_id = payload.get("assignee_user_id") or normalized.get("assignee_user_id")
        if not assignee_user_id or assignee_user_id == executive_context.identity.user_id:
            assignee_user_id = self.staff_context.identity.user_id
        normalized["assignee_user_id"] = assignee_user_id
        normalized.setdefault("assignee_node_id", payload.get("assignee_node_id") or self.staff_context.identity.node_id)
        normalized.setdefault("task_title", normalized.get("title") or "执行高层确认任务")
        normalized.setdefault("task_description", normalized.get("description") or "由 Feishu IM 确认决策后自动生成。")
        normalized.setdefault("status", "pending")
        return coerce_task_v1_payload(normalized, executive_context.identity, executive_context.runtime_payload(), decision_payload=payload)

    def _context_org_id(self, context: SkillContext) -> str:
        return str(context.identity.metadata.get("org_id") or context.runtime.org_id)

    def _decision_meta(self, payload: dict[str, Any]) -> dict[str, Any]:
        meta = dict(payload.get("meta", {})) if isinstance(payload.get("meta"), dict) else {}
        meta.setdefault("source", "feishu_im")
        meta["raw_text"] = payload.get("raw_text")
        return meta

    def _build_staff_report(self, payload: dict[str, Any]) -> StaffReportDraft | dict[str, Any]:
        if payload.get("schema_id") == "schema_v1_staff":
            return dict(payload)
        return StaffReportDraft(
            timestamp=str(payload["timestamp"]),
            work_progress=str(payload["work_progress"]),
            issues_faced=str(payload["issues_faced"]),
            solution_attempt=str(payload["solution_attempt"]),
            need_support=bool(payload["need_support"]),
            next_day_plan=str(payload["next_day_plan"]),
            resource_usage=dict(payload.get("resource_usage", {})),
        )

    def _build_manager_report(self, payload: dict[str, Any]) -> ManagerReportDraft:
        return ManagerReportDraft(
            dept_id=str(payload["dept_id"]),
            overall_health=payload["overall_health"],
            aggregated_summary=str(payload["aggregated_summary"]),
            top_3_risks=list(payload["top_3_risks"]),
            workforce_efficiency=float(payload["workforce_efficiency"]),
            pending_approvals=int(payload["pending_approvals"]),
        )
