from __future__ import annotations

from automage_agents.core.models import SkillResult
from automage_agents.knowledge.local_cache import build_feishu_knowledge_context, search_cached_feishu_knowledge
from automage_agents.knowledge.runtime_context import FEISHU_KNOWLEDGE_INPUT_REF_KEY, build_feishu_knowledge_input_ref
from automage_agents.skills.context import SkillContext


def search_feishu_knowledge(
    context: SkillContext,
    query: str,
    limit: int = 5,
    cache_dir: str = "_cache/feishu_wiki",
    max_context_chars: int = 4000,
) -> SkillResult:
    hits = search_cached_feishu_knowledge(query=query, cache_dir=cache_dir, limit=limit)
    knowledge_context = build_feishu_knowledge_context(
        query=query,
        cache_dir=cache_dir,
        limit=limit,
        max_context_chars=max_context_chars,
    )
    context.runtime.input_refs[FEISHU_KNOWLEDGE_INPUT_REF_KEY] = build_feishu_knowledge_input_ref(knowledge_context)
    return SkillResult(
        ok=True,
        data={
            "query": query,
            "cache_dir": cache_dir,
            "hits": [hit.to_dict() for hit in hits],
            "knowledge_context": knowledge_context.to_dict(),
            "runtime_input_ref_key": FEISHU_KNOWLEDGE_INPUT_REF_KEY,
        },
        message=f"found {len(hits)} cached Feishu knowledge hits",
    )
