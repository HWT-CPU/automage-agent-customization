from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class CachedKnowledgeHit:
    title: str
    token: str
    token_kind: str
    cache_path: str
    score: int
    snippet: str
    source_section_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "token": self.token,
            "token_kind": self.token_kind,
            "cache_path": self.cache_path,
            "score": self.score,
            "snippet": self.snippet,
            "source_section_id": self.source_section_id,
        }


@dataclass(slots=True)
class KnowledgeContextBlock:
    query: str
    context_text: str
    sources: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "context_text": self.context_text,
            "sources": self.sources,
        }


def search_cached_feishu_knowledge(
    query: str,
    cache_dir: str | Path = "_cache/feishu_wiki",
    limit: int = 5,
    max_snippet_chars: int = 1200,
) -> list[CachedKnowledgeHit]:
    cache_path = Path(cache_dir)
    manifest_path = cache_path / "manifest.json"
    if not manifest_path.exists():
        return []
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    terms = _query_terms(query)
    hits: list[CachedKnowledgeHit] = []
    for item in _iter_cached_items(manifest):
        path = Path(item["cache_path"])
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        score = _score_content(query, terms, item["title"], content)
        if score <= 0:
            continue
        hits.append(
            CachedKnowledgeHit(
                title=item["title"],
                token=item["token"],
                token_kind=item["token_kind"],
                cache_path=str(path),
                score=score,
                snippet=_build_snippet(content, terms, max_snippet_chars),
                source_section_id=item.get("source_section_id"),
            )
        )
    return sorted(hits, key=lambda hit: hit.score, reverse=True)[:limit]


def build_feishu_knowledge_context(
    query: str,
    cache_dir: str | Path = "_cache/feishu_wiki",
    limit: int = 5,
    max_snippet_chars: int = 1200,
    max_context_chars: int = 4000,
) -> KnowledgeContextBlock:
    hits = search_cached_feishu_knowledge(
        query=query,
        cache_dir=cache_dir,
        limit=limit,
        max_snippet_chars=max_snippet_chars,
    )
    sources = [hit.to_dict() for hit in hits]
    context_text = _format_context_text(query, hits, max_context_chars)
    return KnowledgeContextBlock(query=query, context_text=context_text, sources=sources)


def _format_context_text(query: str, hits: list[CachedKnowledgeHit], max_context_chars: int) -> str:
    lines = [
        "<feishu_knowledge_context>",
        f"<query>{_escape_text(query)}</query>",
    ]
    closing_line = "</feishu_knowledge_context>"
    if not hits:
        lines.append("<status>no_cached_match</status>")
    for index, hit in enumerate(hits, start=1):
        open_line = f'<source id="{index}" title="{_escape_attr(hit.title)}" token="{_escape_attr(hit.token)}" score="{hit.score}">'
        close_line = "</source>"
        current_text = "\n".join([*lines, open_line, close_line, closing_line])
        remaining = max_context_chars - len(current_text)
        if remaining <= 0:
            if len(lines) == 2:
                lines.append("<status>context_budget_exhausted</status>")
            break
        snippet = _escape_text(_compact_text(hit.snippet))
        if len(snippet) > remaining:
            snippet = snippet[: max(0, remaining - len("\n<truncated/>"))].rstrip() + "\n<truncated/>"
        lines.extend([open_line, snippet, close_line])
    lines.append(closing_line)
    return "\n".join(lines)


def _iter_cached_items(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for section in manifest.get("sections", []):
        if section.get("ok") and section.get("cache_path"):
            items.append(
                {
                    "title": f"{section.get('id')} {section.get('topic')}",
                    "token": section.get("node_token", ""),
                    "token_kind": "section_index",
                    "cache_path": section["cache_path"],
                    "source_section_id": section.get("id"),
                }
            )
    for resource in manifest.get("linked_resources", []):
        if resource.get("ok") and resource.get("cache_path"):
            items.append(
                {
                    "title": resource.get("title", resource.get("token", "")),
                    "token": resource.get("token", ""),
                    "token_kind": resource.get("token_kind", "obj_token"),
                    "cache_path": resource["cache_path"],
                    "source_section_id": resource.get("source_section_id"),
                }
            )
    return items


def _query_terms(query: str) -> list[str]:
    normalized = query.strip().lower()
    terms = [normalized] if normalized else []
    terms.extend(part.lower() for part in re.split(r"\s+", normalized) if part)
    terms.extend(match.group(0).lower() for match in re.finditer(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]{2,}", normalized))
    deduped: list[str] = []
    for term in terms:
        if term and term not in deduped:
            deduped.append(term)
    return deduped


def _score_content(query: str, terms: list[str], title: str, content: str) -> int:
    title_lower = title.lower()
    content_lower = content.lower()
    score = 0
    for term in terms:
        if term in title_lower:
            score += 50 + len(term)
        count = content_lower.count(term)
        if count:
            score += min(count, 20) * max(len(term), 1)
    if query and query.lower() in content_lower:
        score += 20
    return score


def _build_snippet(content: str, terms: list[str], max_chars: int) -> str:
    lower_content = content.lower()
    first_index = -1
    for term in terms:
        index = lower_content.find(term)
        if index >= 0 and (first_index < 0 or index < first_index):
            first_index = index
    if first_index < 0:
        return content[:max_chars].strip()
    start = max(first_index - max_chars // 3, 0)
    end = min(start + max_chars, len(content))
    return content[start:end].strip()


def _compact_text(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text.strip())


def _escape_attr(value: str) -> str:
    return value.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def _escape_text(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
