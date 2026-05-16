from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any

from automage_agents.core.enums import InternalEventType
from automage_agents.core.models import SkillResult


@dataclass(slots=True)
class OutboundMessage:
    target_user_id: str
    title: str
    body: str
    card: dict[str, Any] = field(default_factory=dict)
    receive_id_type: str = "user_id"


class FeishuMessageAdapter:
    def __init__(self, lark_client: Any | None = None):
        """
        Args:
            lark_client: 飞书 SDK 客户端，如果为 None 则 send_message 返回 mock 响应
        """
        self.lark_client = lark_client
    
    def send_message(self, message: OutboundMessage) -> dict[str, Any]:
        """发送飞书消息（如果配置了 lark_client 则使用真实 API，否则返回 mock）"""
        if self.lark_client is not None:
            return self.send_lark_text(self.lark_client, message)
        
        # Fallback to mock if no lark_client configured
        return {
            "ok": True,
            "channel": "feishu_mock",
            "target_user_id": message.target_user_id,
            "receive_id_type": message.receive_id_type,
            "title": message.title,
            "body": message.body,
            "card": message.card,
        }

    def send_lark_text(self, lark_client: Any, message: OutboundMessage) -> dict[str, Any]:
        from lark_oapi.api.im.v1 import CreateMessageRequest, CreateMessageRequestBody

        request = (
            CreateMessageRequest.builder()
            .receive_id_type(message.receive_id_type)
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(message.target_user_id)
                .msg_type("text")
                .content(json.dumps({"text": message.body}, ensure_ascii=False))
                .build()
            )
            .build()
        )
        response = lark_client.im.v1.message.create(request)
        data = response.data
        return {
            "ok": response.success(),
            "channel": "feishu",
            "code": response.code,
            "msg": response.msg,
            "log_id": response.get_log_id(),
            "message_id": getattr(data, "message_id", None) if data else None,
            "chat_id": getattr(data, "chat_id", None) if data else None,
        }

    def build_daily_report_card(self, target_user_id: str) -> OutboundMessage:
        return OutboundMessage(
            target_user_id=target_user_id,
            title="日报填写提醒",
            body="请填写今日工作进度、问题、明日计划和资源使用情况。",
            card={"type": "daily_report", "schema_id": "schema_v1_staff"},
        )

    def build_decision_card(self, target_user_id: str, decision_options: list[dict[str, Any]]) -> OutboundMessage:
        return OutboundMessage(
            target_user_id=target_user_id,
            title="A/B 决策确认",
            body="请选择需要执行的策略方案。",
            card={"type": "executive_decision", "options": decision_options},
        )

    def build_processing_result_reply(self, chat_id: str, event_type: str, result: SkillResult) -> OutboundMessage:
        return OutboundMessage(
            target_user_id=chat_id,
            receive_id_type="chat_id",
            title="AutoMage 处理结果",
            body=self._result_body(event_type, result),
            card={"type": "processing_result", "event_type": event_type, "ok": result.ok},
        )

    def _result_body(self, event_type: str, result: SkillResult) -> str:
        if not result.ok:
            return self._failure_body(event_type, result)
        if event_type == InternalEventType.DAILY_REPORT_SUBMITTED.value:
            work_record_id = result.data.get("work_record_id") or result.data.get("record", {}).get("work_record_id")
            work_record_public_id = result.data.get("work_record_public_id") or result.data.get("record", {}).get("work_record_public_id")
            lines = [
                "日报已收到。",
                "已按 schema_v1_staff v1.0.0 记录。",
                f"记录 ID：{work_record_id or work_record_public_id or 'pending'}",
                "已写入 AutoMage 后端。",
            ]
            return "\n".join(lines)
        if event_type == InternalEventType.TASK_QUERY_REQUESTED.value:
            tasks = result.data.get("tasks") or result.data.get("items", [])
            if not tasks:
                return "当前没有待处理任务。"
            lines = ["你的当前任务："]
            for index, task in enumerate(tasks[:5], start=1):
                title = task.get("title", "未命名任务")
                status = task.get("status", "unknown")
                task_id = task.get("task_id") or task.get("public_id") or ""
                prefix = f"{task_id}：" if task_id else ""
                lines.append(f"{index}. {prefix}{title}（{status}）")
            return "\n".join(lines)
        if event_type == InternalEventType.DREAM_DECISION_REQUESTED.value:
            options = result.data.get("decision_options") or []
            summary_id = result.data.get("summary_public_id") or result.data.get("summary_id") or "pending"
            lines = [f"Dream 决策草案已生成。", f"汇总 ID：{summary_id}", "可选方案："]
            for option in options:
                option_id = option.get("option_id") or option.get("key") or "?"
                title = option.get("title") or option.get("label") or "未命名方案"
                summary = option.get("summary") or ""
                task_count = len(option.get("task_candidates") or [])
                lines.append(f"- 方案 {option_id}：{title}；候选任务 {task_count} 个。{summary}")
            lines.append(f"如确认执行，请回复：确认方案B {summary_id}")
            return "\n".join(lines)
        if event_type == InternalEventType.EXECUTIVE_DECISION_SELECTED.value:
            task_ids = result.data.get("task_ids") or result.data.get("generated_task_ids") or []
            if not task_ids and isinstance(result.data.get("task_queue"), list):
                task_ids = [task.get("task_id") for task in result.data["task_queue"] if isinstance(task, dict) and task.get("task_id")]
            lines = ["决策已提交。"]
            if task_ids:
                lines.append("已生成任务：")
                lines.extend(f"- {task_id}" for task_id in task_ids)
            else:
                lines.append("本次没有生成任务。")
            return "\n".join(lines)
        if event_type in {InternalEventType.TASK_UPDATE_REQUESTED.value, InternalEventType.TASK_COMPLETED.value}:
            task = result.data.get("task") or {}
            task_id = task.get("task_id") or task.get("public_id") or "pending"
            status = task.get("status") or "updated"
            return f"任务已更新。\n任务 ID：{task_id}\n当前状态：{status}"
        return result.message or "AutoMage 已处理该事件。"

    def _failure_body(self, event_type: str, result: SkillResult) -> str:
        backend_error_code = self._backend_error_code(result)
        backend_message = self._backend_message(result)
        error_code = backend_error_code or result.error_code or "unknown"
        if result.error_code == "conflict":
            if event_type == InternalEventType.DAILY_REPORT_SUBMITTED.value:
                lines = [
                    "今天的日报已存在，且这次内容与已提交内容不一致。",
                    "为避免覆盖正式记录，后端已拦截本次重复提交。",
                    "如需修改，请使用更新/修订入口，或在 Web 端编辑当天日报。",
                    f"错误码：{error_code}",
                ]
                if backend_message:
                    lines.append(f"后端说明：{backend_message}")
                return "\n".join(lines)
            return self._generic_failure("请求与已有正式记录冲突，后端已阻止重复写入。", error_code, backend_message)
        if result.error_code == "permission_denied":
            return self._generic_failure("当前账号没有权限执行这个操作，请确认 open_id 映射、角色、部门和 node_id 是否正确。", error_code, backend_message)
        if result.error_code == "rate_limited":
            return self._generic_failure("请求过于频繁，请稍后再试。", error_code, backend_message)
        if result.error_code == "auth_failed":
            return self._generic_failure("后端认证失败，请检查 AutoMage 访问令牌或请求头配置。", error_code, backend_message)
        if result.error_code == "schema_validation_failed":
            return self._generic_failure("日报内容未通过 schema 校验，请补充今日进展、问题、处理方式和明日计划。", error_code, backend_message)
        if result.error_code == "server_error":
            return self._generic_failure("后端服务暂时异常，请稍后重试或联系运维查看 API 日志。", error_code, backend_message)
        return self._generic_failure(result.message or "AutoMage 处理失败。", error_code, backend_message)

    def _generic_failure(self, headline: str, error_code: str, backend_message: str) -> str:
        lines = [headline, f"错误码：{error_code}"]
        if backend_message:
            lines.append(f"后端说明：{backend_message}")
        return "\n".join(lines)

    def _backend_error_code(self, result: SkillResult) -> str:
        response = result.data.get("response")
        if isinstance(response, dict):
            error = response.get("error")
            if isinstance(error, dict):
                return str(error.get("error_code") or "").strip()
            return str(response.get("detail") or response.get("code") or "").strip()
        return ""

    def _backend_message(self, result: SkillResult) -> str:
        response = result.data.get("response")
        if isinstance(response, dict):
            error = response.get("error")
            if isinstance(error, dict):
                return str(error.get("message") or response.get("msg") or result.message or "").strip()
            return str(response.get("detail") or response.get("msg") or result.message or "").strip()
        return str(result.message or "").strip()
