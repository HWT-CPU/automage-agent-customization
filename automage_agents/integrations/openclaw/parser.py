from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from automage_agents.integrations.openclaw.config import OpenClawCommandConfig, OpenClawConfig


MANAGER_SUMMARY_ACTIONS = ("汇总", "总结", "summary", "summarize")
MANAGER_SUMMARY_CONTEXTS = ("员工日报", "日报文件", "日报", "员工报告", "团队", "部门", "下属", "组内", "文件", "附件", "staff report", "team report", "daily report")


@dataclass(slots=True)
class ParsedOpenClawCommand:
    event_type: str
    skill_name: str
    payload: dict[str, Any] = field(default_factory=dict)


class OpenClawCommandParser:
    def __init__(self, config: OpenClawConfig):
        self.config = config

    def parse(
        self,
        text: str,
        *,
        actor_user_id: str | None = None,
        manager_user_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> ParsedOpenClawCommand:
        normalized = text.strip()
        commands = self.config.commands
        if self._contains_any(normalized, commands.task_query):
            return ParsedOpenClawCommand(
                event_type=self.config.routing.default_task_query,
                skill_name="fetch_my_tasks",
                payload={},
            )
        if self._contains_any(normalized, commands.knowledge_query):
            return ParsedOpenClawCommand(
                event_type=self.config.routing.default_knowledge_query,
                skill_name="search_feishu_knowledge",
                payload={"query": self._strip_knowledge_query_prefix(normalized)},
            )
        if self._contains_any(normalized, commands.executive_decision):
            return ParsedOpenClawCommand(
                event_type=self.config.routing.default_executive_decision,
                skill_name="commit_decision",
                payload={"decision_payload": self._build_decision_payload(normalized)},
            )
        if self._contains_any(normalized, commands.manager_feedback) or self._is_manager_summary_request(normalized) or self._is_manager_file_event(
            actor_user_id=actor_user_id,
            manager_user_id=manager_user_id,
            payload=payload,
        ):
            return ParsedOpenClawCommand(
                event_type=self.config.routing.default_manager_feedback,
                skill_name="generate_manager_report",
                payload={"report": self._build_manager_payload(normalized, payload=payload)},
            )
        if self._contains_any(normalized, commands.markdown_import):
            return ParsedOpenClawCommand(
                event_type=self.config.routing.default_markdown_import,
                skill_name="import_staff_daily_report_from_markdown",
                payload={"report": self._strip_markdown_import_prefix(normalized)},
            )
        return ParsedOpenClawCommand(
            event_type=self.config.routing.default_daily_report,
            skill_name="post_daily_report",
            payload={"report": self._build_staff_payload(normalized)},
        )

    def _contains_any(self, text: str, keywords: list[str]) -> bool:
        return any(keyword and keyword in text for keyword in keywords)

    def _is_manager_summary_request(self, text: str) -> bool:
        lowered = text.lower()
        return any(action in lowered for action in MANAGER_SUMMARY_ACTIONS) and any(context in lowered for context in MANAGER_SUMMARY_CONTEXTS)

    def _is_manager_file_event(self, *, actor_user_id: str | None, manager_user_id: str | None, payload: dict[str, Any] | None) -> bool:
        if not actor_user_id or not manager_user_id or actor_user_id != manager_user_id:
            return False
        feishu_file = payload.get("feishu_file") if isinstance(payload, dict) else None
        return isinstance(feishu_file, dict) and bool(feishu_file.get("ok"))

    def _build_staff_payload(self, text: str) -> dict[str, Any]:
        return {
            "work_progress": self._extract_segment(text, ["今天完成了", "今日完成了", "完成了", "工作进展"], ["遇到的问题是", "遇到问题是", "问题是", "明天", "明日", "下一步"]) or text,
            "issues_faced": self._extract_segment(text, ["遇到的问题是", "遇到问题是", "问题是", "阻塞是"], ["已处理", "已尝试", "解决方式是", "明天", "明日", "下一步"]),
            "solution_attempt": self._extract_segment(text, ["已处理", "已尝试", "解决方式是"], ["明天", "明日", "下一步"]),
            "need_support": any(keyword in text for keyword in ["需要支持", "阻塞", "问题", "还没确定", "不确定"]),
            "next_day_plan": self._extract_segment(text, ["明天", "明日", "下一步"], []),
            "resource_usage": {"source": "openclaw_cli", "raw_text": text},
            "raw_text": text,
        }

    def _build_manager_payload(self, text: str, *, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        report = {
            "overall_health": "yellow" if any(keyword in text for keyword in ["风险", "阻塞", "问题"] ) else "green",
            "aggregated_summary": text,
            "top_3_risks": [text] if any(keyword in text for keyword in ["风险", "阻塞", "问题"]) else [],
            "workforce_efficiency": 0.8,
            "pending_approvals": 0,
        }
        feishu_file = payload.get("feishu_file") if isinstance(payload, dict) else None
        if isinstance(feishu_file, dict):
            report["feishu_file"] = dict(feishu_file)
        return report

    def _build_decision_payload(self, text: str) -> dict[str, Any]:
        selected_option_id = "B" if any(keyword in text for keyword in ["决策B", "决策 B", "选择B", "选择 B", "方案B", "方案 B"]) else "A"
        return {
            "selected_option_id": selected_option_id,
            "decision_summary": text,
            "task_candidates": [
                {
                    "assignee_user_id": "user-001",
                    "title": f"执行方案 {selected_option_id}",
                    "description": text,
                }
            ],
        }

    def _strip_markdown_import_prefix(self, text: str) -> str:
        prefixes = ["导入日报", "正式日报", "markdown日报", "Markdown日报"]
        stripped = text
        for prefix in prefixes:
            if stripped.startswith(prefix):
                stripped = stripped[len(prefix) :]
                break
        return stripped.strip(" ：:，,。\n") or text

    def _strip_knowledge_query_prefix(self, text: str) -> str:
        prefixes = ["查知识库", "查询知识库", "知识库", "项目资料", "项目文档", "查文档", "查询文档"]
        stripped = text
        for prefix in prefixes:
            if stripped.startswith(prefix):
                stripped = stripped[len(prefix) :]
                break
        return stripped.strip(" ：:，,。\n") or text

    def _extract_segment(self, text: str, start_markers: list[str], end_markers: list[str]) -> str:
        start_index = -1
        marker_length = 0
        for marker in start_markers:
            index = text.find(marker)
            if index >= 0 and (start_index < 0 or index < start_index):
                start_index = index
                marker_length = len(marker)
        if start_index < 0:
            return ""
        segment = text[start_index + marker_length :]
        end_indexes = [segment.find(marker) for marker in end_markers if segment.find(marker) >= 0]
        if end_indexes:
            segment = segment[: min(end_indexes)]
        return segment.strip(" ：:，,。.\n")
