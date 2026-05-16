from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from automage_agents.integrations.feishu import FeishuDocsCliClient, FeishuDocsFetchResult
from automage_agents.knowledge.feishu_wiki import FeishuKnowledgeConfig, FeishuKnowledgeSection


TOKEN_PATTERN = re.compile(r"\b[A-Za-z0-9_-]{20,}\b")
MARKDOWN_TABLE_ROW_PATTERN = re.compile(r"^\|(.+)\|$")


@dataclass(slots=True)
class FeishuLinkedResource:
    title: str
    token: str
    token_kind: str
    labels: list[str] = field(default_factory=list)
    source_section_id: str | None = None
    cache_path: str | None = None
    ok: bool | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "token": self.token,
            "token_kind": self.token_kind,
            "labels": self.labels,
            "source_section_id": self.source_section_id,
            "cache_path": self.cache_path,
            "ok": self.ok,
            "error": self.error,
        }


@dataclass(slots=True)
class FeishuKnowledgeSyncResult:
    cache_dir: str
    sections: list[dict[str, Any]]
    linked_resources: list[FeishuLinkedResource]
    manifest_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "cache_dir": self.cache_dir,
            "sections": self.sections,
            "linked_resources": [resource.to_dict() for resource in self.linked_resources],
            "manifest_path": self.manifest_path,
        }


def sync_feishu_knowledge(
    config: FeishuKnowledgeConfig,
    client: FeishuDocsCliClient,
    doc_format: str = "markdown",
    detail: str = "simple",
    include_linked_docs: bool = True,
    include_files: bool = False,
    stop_on_error: bool = False,
) -> FeishuKnowledgeSyncResult:
    section_results: list[dict[str, Any]] = []
    linked_resources_by_token: dict[str, FeishuLinkedResource] = {}

    for section in config.sections:
        result = client.fetch_doc(section.node_token, doc_format=doc_format, detail=detail)
        section_result = _section_result(section, result)
        section_results.append(section_result)
        if not result.ok:
            if stop_on_error:
                break
            continue
        for resource in extract_linked_resources(result.content or "", section):
            linked_resources_by_token.setdefault(resource.token, resource)

    if include_linked_docs:
        for resource in linked_resources_by_token.values():
            if resource.token_kind == "file_token" and not include_files:
                continue
            result = client.fetch_doc(resource.token, doc_format=doc_format, detail=detail)
            resource.ok = result.ok
            resource.cache_path = result.cache_path
            resource.error = result.error
            if not result.ok and stop_on_error:
                break

    sync_result = FeishuKnowledgeSyncResult(
        cache_dir=str(client.cache_dir),
        sections=section_results,
        linked_resources=list(linked_resources_by_token.values()),
    )
    sync_result.manifest_path = str(write_manifest(sync_result, client.cache_dir))
    return sync_result


def extract_linked_resources(content: str, section: FeishuKnowledgeSection | None = None) -> list[FeishuLinkedResource]:
    resources: list[FeishuLinkedResource] = []
    current_token_kind: str | None = None
    for line in content.splitlines():
        row = _parse_markdown_table_row(line)
        if not row:
            continue
        header_token_kind = _detect_header_token_kind(row)
        if header_token_kind:
            current_token_kind = header_token_kind
            continue
        if not current_token_kind:
            continue
        token = _first_token(row[1])
        if not token:
            continue
        labels = _split_labels(row[2]) if len(row) > 2 else []
        resources.append(
            FeishuLinkedResource(
                title=row[0].strip() or token,
                token=token,
                token_kind=current_token_kind,
                labels=labels,
                source_section_id=section.id if section else None,
            )
        )
    return resources


def write_manifest(result: FeishuKnowledgeSyncResult, cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / "manifest.json"
    path.write_text(json.dumps(result.to_dict() | {"manifest_path": str(path)}, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _section_result(section: FeishuKnowledgeSection, result: FeishuDocsFetchResult) -> dict[str, Any]:
    return {
        "id": section.id,
        "topic": section.topic,
        "node_token": section.node_token,
        "ok": result.ok,
        "cache_path": result.cache_path,
        "error": result.error,
        "document_id": _document_id(result.raw),
    }


def _document_id(raw: dict[str, Any] | None) -> str | None:
    if not raw:
        return None
    data = raw.get("data", {})
    document = data.get("document", {}) if isinstance(data, dict) else {}
    document_id = document.get("document_id") if isinstance(document, dict) else None
    return str(document_id) if document_id else None


def _parse_markdown_table_row(line: str) -> list[str] | None:
    match = MARKDOWN_TABLE_ROW_PATTERN.match(line.strip())
    if not match:
        return None
    cells = [cell.strip() for cell in match.group(1).split("|")]
    if not cells or all(_is_separator_cell(cell) for cell in cells):
        return None
    return cells


def _is_separator_cell(cell: str) -> bool:
    compact = cell.replace(" ", "")
    return bool(compact) and set(compact) <= {"-", ":"}


def _detect_header_token_kind(row: list[str]) -> str | None:
    if len(row) < 2:
        return None
    header_or_value = row[1].lower()
    if "obj_token" in header_or_value:
        return "obj_token"
    if "file_token" in header_or_value:
        return "file_token"
    return None


def _first_token(value: str) -> str | None:
    match = TOKEN_PATTERN.search(value)
    return match.group(0) if match else None


def _split_labels(value: str) -> list[str]:
    return [label.strip() for label in re.split(r"[,，]", value) if label.strip()]
