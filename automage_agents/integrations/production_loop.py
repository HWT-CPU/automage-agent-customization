from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from types import SimpleNamespace
from typing import Any

from automage_agents.core.enums import InternalEventType
from automage_agents.integrations.feishu.messages import OutboundMessage
from automage_agents.integrations.hermes.runtime import HermesOpenClawRuntime
from automage_agents.skills.executive import commit_decision, dream_decision_engine
from automage_agents.skills.manager import generate_manager_report


@dataclass(slots=True)
class ProductionLoopOptions:
    manager_target_id: str | None = None
    executive_target_id: str | None = None
    auto_confirm_decision: bool = False
    option_id: str = "B"


class FeishuProductionLoop:
    def __init__(self, runtime: HermesOpenClawRuntime, options: ProductionLoopOptions | None = None):
        self.runtime = runtime
        self.options = options or ProductionLoopOptions()

    def handle_staff_daily_report(self, raw_event: dict[str, Any]) -> dict[str, Any]:
        staff_result = self.runtime.handle_feishu_message_receive_v1(raw_event)
        output: dict[str, Any] = {
            "ok": bool(staff_result.get("ok")),
            "stage": "staff_report",
            "staff_report": staff_result,
            "manager_summary": None,
            "executive_dream": None,
            "executive_decision": None,
            "notifications": [],
        }
        if not staff_result.get("ok"):
            return output

        manager_result = self._generate_manager_summary(staff_result)
        output["manager_summary"] = manager_result
        output["ok"] = bool(manager_result.get("ok"))
        output["stage"] = "manager_summary"
        if not manager_result.get("ok"):
            return output

        manager_notification = self._notify_manager(manager_result)
        if manager_notification is not None:
            output["notifications"].append(manager_notification)

        dream_result = self._generate_executive_dream(manager_result)
        output["executive_dream"] = dream_result
        output["ok"] = bool(dream_result.get("ok"))
        output["stage"] = "executive_dream"
        if not dream_result.get("ok"):
            return output

        executive_notification = self._notify_executive(dream_result)
        if executive_notification is not None:
            output["notifications"].append(executive_notification)

        if self.options.auto_confirm_decision:
            decision_result = self._confirm_decision(manager_result, dream_result)
            output["executive_decision"] = decision_result
            output["ok"] = bool(decision_result.get("ok"))
            output["stage"] = "executive_decision"
        return output

    def _generate_manager_summary(self, staff_result: dict[str, Any]) -> dict[str, Any]:
        payload = self._manager_payload_from_staff_result(staff_result)
        result = generate_manager_report(self.runtime.contexts.manager, payload)
        return self._skill_result("manager_feedback_submitted", result)

    def _generate_executive_dream(self, manager_result: dict[str, Any]) -> dict[str, Any]:
        summary_id = self._summary_id(manager_result)
        result = dream_decision_engine(self.runtime.contexts.executive, {"summary_id": summary_id, "source_summary_id": summary_id})
        return self._skill_result("dream_decision_requested", result)

    def _confirm_decision(self, manager_result: dict[str, Any], dream_result: dict[str, Any]) -> dict[str, Any]:
        summary_id = self._summary_id(manager_result)
        dream_data = dream_result.get("data", {})
        options = list(dream_data.get("decision_options") or [])
        selected = next((option for option in options if str(option.get("option_id")).upper() == self.options.option_id.upper()), None)
        selected = selected or (options[0] if options else {"option_id": self.options.option_id.upper(), "title": "默认方案", "task_candidates": []})
        payload = {
            "summary_id": summary_id,
            "source_summary_id": summary_id,
            "title": f"确认{selected.get('title') or '执行方案'}",
            "decision_summary": selected.get("summary") or "确认执行 Manager 汇总后的推荐方案。",
            "selected_option_id": selected.get("option_id") or self.options.option_id.upper(),
            "selected_option_label": selected.get("title") or f"方案 {self.options.option_id.upper()}",
            "decision_options": options,
            "priority": "high",
            "task_candidates": selected.get("task_candidates") or [],
        }
        result = commit_decision(self.runtime.contexts.executive, payload)
        return self._skill_result("executive_decision_selected", result)

    def _manager_payload_from_staff_result(self, staff_result: dict[str, Any]) -> dict[str, Any]:
        data = staff_result.get("data", {})
        record = data.get("record") if isinstance(data.get("record"), dict) else {}
        report = record.get("report") if isinstance(record.get("report"), dict) else {}
        source_record_id = data.get("work_record_id") or data.get("work_record_public_id") or record.get("work_record_id") or record.get("staff_report_id")
        raw_text = report.get("raw_text") or report.get("work_progress") or staff_result.get("message") or "员工日报已提交。"
        issues = report.get("issues_faced") or ""
        need_support = bool(report.get("need_support"))
        risks = []
        blocked_items = []
        if issues:
            risks.append({"risk_title": "员工日报风险", "description": issues, "severity": "high" if need_support else "medium", "source_record_ids": [source_record_id] if source_record_id else []})
        if need_support:
            blocked_items.append({"title": "员工需要支持", "description": issues or raw_text, "severity": "high", "source_record_ids": [source_record_id] if source_record_id else [], "need_executive_decision": True, "suggested_action": "由 Manager 确认资源支持并提交 Executive 决策。"})
        return {
            "timestamp": datetime.now().astimezone().isoformat(),
            "dept_id": self.runtime.contexts.manager.identity.department_id,
            "department_id": self.runtime.contexts.manager.identity.department_id,
            "overall_health": "yellow" if need_support else "green",
            "aggregated_summary": f"员工 {staff_result.get('actor_user_id')} 今日进展：{raw_text}",
            "top_3_risks": risks,
            "workforce_efficiency": {"score": 78 if need_support else 88, "explanation": "由 Staff 日报自动生成 Manager 汇总。"},
            "pending_approvals": 1 if need_support else 0,
            "blocked_items": blocked_items,
            "need_executive_decision": blocked_items,
            "source_record_ids": [source_record_id] if source_record_id else [],
            "summary_date": datetime.now().astimezone().date().isoformat(),
            "meta": {"source": "feishu_production_loop", "raw_staff_result": {"event_type": staff_result.get("event_type"), "actor_user_id": staff_result.get("actor_user_id")}},
        }

    def _notify_manager(self, manager_result: dict[str, Any]) -> dict[str, Any] | None:
        if not self.options.manager_target_id:
            return None
        summary_id = self._summary_id(manager_result)
        return self.runtime.feishu_messages.send_message(
            OutboundMessage(
                target_user_id=self.options.manager_target_id,
                title="Manager 日报汇总已生成",
                body=f"员工日报已汇总。汇总 ID：{summary_id}\n请检查风险、阻塞和待审批项。",
                card={"type": "manager_summary", "summary_id": summary_id, "data": manager_result.get("data", {})},
            )
        )

    def _notify_executive(self, dream_result: dict[str, Any]) -> dict[str, Any] | None:
        if not self.options.executive_target_id:
            return None
        options = dream_result.get("data", {}).get("decision_options") or []
        message = self.runtime.feishu_messages.build_decision_card(self.options.executive_target_id, options)
        message.body = self.runtime.feishu_messages._result_body(InternalEventType.DREAM_DECISION_REQUESTED.value, self._to_skill_result_like(dream_result))
        return self.runtime.feishu_messages.send_message(message)

    def _summary_id(self, manager_result: dict[str, Any]) -> str:
        data = manager_result.get("data", {})
        record = data.get("record") if isinstance(data.get("record"), dict) else {}
        report = record.get("report") if isinstance(record.get("report"), dict) else {}
        return str(data.get("summary_public_id") or data.get("summary_id") or report.get("summary_public_id") or report.get("summary_id") or "pending")

    def _skill_result(self, event_type: str, result: Any) -> dict[str, Any]:
        return {
            "event_type": event_type,
            "ok": bool(result.ok),
            "message": result.message,
            "error_code": result.error_code,
            "data": result.data,
        }

    def _to_skill_result_like(self, result: dict[str, Any]) -> Any:
        return SimpleNamespace(
            ok=bool(result.get("ok")),
            data=result.get("data", {}),
            message=result.get("message"),
            error_code=result.get("error_code"),
        )
