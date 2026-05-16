from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from automage_agents.config.loader import load_toml


@dataclass(slots=True)
class FeishuKnowledgeSection:
    id: str
    topic: str
    node_token: str
    keywords: list[str]


@dataclass(slots=True)
class FeishuKnowledgeConfig:
    enabled: bool
    source: str
    entry_title: str
    fetch_command: str
    sections: list[FeishuKnowledgeSection]


@dataclass(slots=True)
class KnowledgeRoute:
    query: str
    section: FeishuKnowledgeSection
    matched_keywords: list[str]
    score: int
    fetch_command: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "section": {
                "id": self.section.id,
                "topic": self.section.topic,
                "node_token": self.section.node_token,
                "keywords": self.section.keywords,
            },
            "matched_keywords": self.matched_keywords,
            "score": self.score,
            "fetch_command": self.fetch_command,
        }


def load_feishu_knowledge_config(path: str | Path = "configs/feishu_knowledge.example.toml") -> FeishuKnowledgeConfig:
    raw = load_toml(path).get("knowledge", {})
    return FeishuKnowledgeConfig(
        enabled=bool(raw.get("enabled", True)),
        source=str(raw.get("source", "feishu_wiki")),
        entry_title=str(raw.get("entry_title", "00 Agent 入口与索引协议")),
        fetch_command=str(raw.get("fetch_command", "lark-cli docs +fetch --api-version v2 --doc {token}")),
        sections=[_build_section(section) for section in raw.get("sections", [])],
    )


def route_knowledge_query(query: str, config: FeishuKnowledgeConfig | None = None) -> KnowledgeRoute:
    config = config or load_feishu_knowledge_config()
    if not config.sections:
        raise ValueError("No Feishu knowledge sections configured.")

    best_section = config.sections[0]
    best_keywords: list[str] = []
    best_score = -1
    normalized = query.lower()
    for section in config.sections:
        matched = [keyword for keyword in section.keywords if keyword.lower() in normalized]
        score = sum(len(keyword) for keyword in matched)
        if score > best_score:
            best_section = section
            best_keywords = matched
            best_score = score

    return KnowledgeRoute(
        query=query,
        section=best_section,
        matched_keywords=best_keywords,
        score=max(best_score, 0),
        fetch_command=config.fetch_command.format(token=best_section.node_token),
    )


def _build_section(raw: dict[str, Any]) -> FeishuKnowledgeSection:
    return FeishuKnowledgeSection(
        id=str(raw["id"]),
        topic=str(raw["topic"]),
        node_token=str(raw["node_token"]),
        keywords=list(raw.get("keywords", [])),
    )
