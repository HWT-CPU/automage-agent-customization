from __future__ import annotations

from dataclasses import dataclass

from automage_agents.integrations.hermes.client import LocalHermesClient
from automage_agents.integrations.hermes.contracts import HermesInvokeRequest, HermesTrace
from automage_agents.integrations.openclaw.contracts import OpenClawEvent, OpenClawResponse
from automage_agents.integrations.openclaw.parser import OpenClawCommandParser


@dataclass(slots=True)
class LocalOpenClawClient:
    hermes_client: LocalHermesClient
    parser: OpenClawCommandParser
    user_mapping: dict[str, str]

    def submit_event(self, event: OpenClawEvent) -> OpenClawResponse:
        actor_user_id = self.user_mapping.get(event.actor_external_id, event.actor_external_id)
        missing_file_response = self._missing_feishu_file_response(event)
        if missing_file_response is not None:
            return missing_file_response
        parsed = self.parser.parse(
            event.text,
            actor_user_id=actor_user_id,
            manager_user_id=self.hermes_client.manager_context.identity.user_id,
            payload=event.payload,
        )
        hermes_response = self.hermes_client.invoke_skill(
            HermesInvokeRequest(
                skill_name=parsed.skill_name,
                actor_user_id=actor_user_id,
                payload=parsed.payload,
                trace=HermesTrace(correlation_id=event.event_id),
            )
        )
        reply_text = self._reply_text(parsed.event_type, hermes_response.result.message, hermes_response.result.data, hermes_response.result.ok)
        return OpenClawResponse(
            ok=hermes_response.ok,
            event=event,
            event_type=parsed.event_type,
            skill_name=parsed.skill_name,
            reply_text=reply_text,
            hermes=hermes_response,
            error_code=hermes_response.result.error_code,
        )

    def _missing_feishu_file_response(self, event: OpenClawEvent) -> OpenClawResponse | None:
        feishu_file = event.payload.get("feishu_file") if isinstance(event.payload, dict) else None
        if not isinstance(feishu_file, dict) or not feishu_file.get("requested") or feishu_file.get("ok"):
            return None
        return OpenClawResponse(
            ok=False,
            event=event,
            event_type=self.parser.config.routing.default_manager_feedback,
            skill_name="generate_manager_report",
            reply_text="没有收到可汇总的文件附件。请直接上传 .md/.txt/.docx/.xlsx 文件，或先上传文件后再回复“汇总这个员工日报文件”。",
            hermes=None,
            error_code="feishu_file_missing",
        )

    def _reply_text(self, event_type: str, message: str, data: dict, ok: bool) -> str:
        if not ok:
            return f"处理失败：{message}"
        if event_type == self.parser.config.routing.default_daily_report:
            return f"日报已收到，记录 ID：{data.get('work_record_id') or data.get('record', {}).get('work_record_id', 'mock-pending')}"
        if event_type == self.parser.config.routing.default_markdown_import:
            return f"正式日报已导入，记录 ID：{data.get('work_record_id', 'mock-pending')}"
        if event_type == self.parser.config.routing.default_task_query:
            tasks = data.get("tasks") or data.get("items", [])
            if not tasks:
                return "当前没有待处理任务。"
            lines = ["你的当前任务："]
            for index, task in enumerate(tasks[:5], start=1):
                lines.append(f"{index}. {task.get('title', '未命名任务')}（{task.get('status', 'unknown')}）")
            return "\n".join(lines)
        if event_type == self.parser.config.routing.default_knowledge_query:
            hits = data.get("hits", [])
            if not hits:
                return "本地知识库缓存中没有找到相关内容。"
            lines = ["知识库命中："]
            for index, hit in enumerate(hits[:3], start=1):
                lines.append(f"{index}. {hit.get('title', '未命名文档')}（score={hit.get('score', 0)}）")
            return "\n".join(lines)
        if event_type == self.parser.config.routing.default_manager_feedback:
            return f"Manager 汇总已生成，报告 ID：{data.get('manager_report_id', 'mock-pending')}"
        if event_type == self.parser.config.routing.default_executive_decision:
            return f"决策已提交，生成任务：{', '.join(data.get('generated_task_ids', [])) or '无'}"
        return message or "OpenClaw 已处理该事件。"
