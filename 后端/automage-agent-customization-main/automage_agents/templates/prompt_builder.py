from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROLE_TEMPLATE_PATHS = {
    "staff": Path("automage_agents/templates/line_worker/agents.md"),
    "manager": Path("automage_agents/templates/manager/agents.md"),
    "executive": Path("automage_agents/templates/executive/agents.md"),
}
BASE_TEMPLATE_PATH = Path("automage_agents/templates/base/agents.md")


@dataclass(slots=True)
class AgentPromptPreview:
    role: str
    prompt_text: str
    runtime_payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "prompt_text": self.prompt_text,
            "runtime_payload": self.runtime_payload,
        }


def build_agent_prompt_preview(
    role: str,
    runtime_payload: dict[str, Any],
    base_template_path: str | Path = BASE_TEMPLATE_PATH,
    role_template_path: str | Path | None = None,
) -> AgentPromptPreview:
    normalized_role = role.lower()
    selected_role_template = Path(role_template_path) if role_template_path else ROLE_TEMPLATE_PATHS[normalized_role]
    base_template = Path(base_template_path).read_text(encoding="utf-8")
    role_template = selected_role_template.read_text(encoding="utf-8")
    knowledge_context = _knowledge_context_from_payload(runtime_payload)
    prompt_text = "\n\n".join(
        [
            base_template.strip(),
            role_template.strip(),
            "## 当前 Runtime Context",
            "```json\n" + json.dumps(runtime_payload, ensure_ascii=False, indent=2) + "\n```",
            "## 注入的 Feishu 知识库上下文",
            knowledge_context or "无可用 Feishu 知识库上下文。",
        ]
    )
    return AgentPromptPreview(role=normalized_role, prompt_text=prompt_text, runtime_payload=runtime_payload)


def _knowledge_context_from_payload(runtime_payload: dict[str, Any]) -> str:
    input_refs = runtime_payload.get("input_refs", {})
    if not isinstance(input_refs, dict):
        return ""
    feishu_knowledge = input_refs.get("feishu_knowledge", {})
    if not isinstance(feishu_knowledge, dict):
        return ""
    context_text = feishu_knowledge.get("context_text")
    return str(context_text) if context_text else ""
