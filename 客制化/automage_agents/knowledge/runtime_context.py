from __future__ import annotations

from copy import deepcopy
from typing import Any

from automage_agents.core.models import RuntimeContextV0
from automage_agents.knowledge.local_cache import KnowledgeContextBlock, build_feishu_knowledge_context


FEISHU_KNOWLEDGE_INPUT_REF_KEY = "feishu_knowledge"


def build_feishu_knowledge_input_ref(context_block: KnowledgeContextBlock) -> dict[str, Any]:
    return {
        "source": "feishu_wiki_cache",
        "query": context_block.query,
        "context_text": context_block.context_text,
        "sources": context_block.sources,
    }


def build_feishu_knowledge_reference(runtime_context: dict[str, Any]) -> dict[str, Any] | None:
    input_refs = runtime_context.get("input_refs", {})
    if not isinstance(input_refs, dict):
        return None
    feishu_knowledge = input_refs.get(FEISHU_KNOWLEDGE_INPUT_REF_KEY)
    if not isinstance(feishu_knowledge, dict):
        return None
    sources = feishu_knowledge.get("sources", [])
    if not isinstance(sources, list):
        sources = []
    context_text = str(feishu_knowledge.get("context_text") or "")
    return {
        "source": str(feishu_knowledge.get("source") or "feishu_wiki_cache"),
        "query": str(feishu_knowledge.get("query") or ""),
        "runtime_input_ref_key": FEISHU_KNOWLEDGE_INPUT_REF_KEY,
        "has_context_text": bool(context_text),
        "context_chars": len(context_text),
        "source_count": len(sources),
        "sources": [_lightweight_source_ref(source) for source in sources if isinstance(source, dict)],
    }


def knowledge_refs_from_runtime(runtime_context: dict[str, Any]) -> dict[str, Any]:
    feishu_ref = build_feishu_knowledge_reference(runtime_context)
    if not feishu_ref:
        return {}
    return {FEISHU_KNOWLEDGE_INPUT_REF_KEY: feishu_ref}


def attach_feishu_knowledge_to_runtime(
    runtime: RuntimeContextV0,
    query: str,
    cache_dir: str = "_cache/feishu_wiki",
    limit: int = 5,
    max_context_chars: int = 4000,
) -> KnowledgeContextBlock:
    context_block = build_feishu_knowledge_context(
        query=query,
        cache_dir=cache_dir,
        limit=limit,
        max_context_chars=max_context_chars,
    )
    runtime.input_refs[FEISHU_KNOWLEDGE_INPUT_REF_KEY] = build_feishu_knowledge_input_ref(context_block)
    return context_block


def runtime_payload_with_feishu_knowledge(
    runtime: RuntimeContextV0,
    query: str,
    cache_dir: str = "_cache/feishu_wiki",
    limit: int = 5,
    max_context_chars: int = 4000,
) -> dict[str, Any]:
    cloned_runtime = deepcopy(runtime)
    attach_feishu_knowledge_to_runtime(
        runtime=cloned_runtime,
        query=query,
        cache_dir=cache_dir,
        limit=limit,
        max_context_chars=max_context_chars,
    )
    return cloned_runtime.to_dict()


def _lightweight_source_ref(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": str(source.get("title") or ""),
        "token": str(source.get("token") or ""),
        "token_kind": str(source.get("token_kind") or ""),
        "score": source.get("score"),
        "source_section_id": source.get("source_section_id"),
    }
