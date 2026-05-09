from automage_agents.knowledge.local_cache import CachedKnowledgeHit, KnowledgeContextBlock, build_feishu_knowledge_context, search_cached_feishu_knowledge
from automage_agents.knowledge.runtime_context import FEISHU_KNOWLEDGE_INPUT_REF_KEY, attach_feishu_knowledge_to_runtime, build_feishu_knowledge_input_ref, build_feishu_knowledge_reference, knowledge_refs_from_runtime, runtime_payload_with_feishu_knowledge
from automage_agents.knowledge.feishu_wiki import FeishuKnowledgeConfig, FeishuKnowledgeSection, KnowledgeRoute, route_knowledge_query

__all__ = [
    "CachedKnowledgeHit",
    "FEISHU_KNOWLEDGE_INPUT_REF_KEY",
    "FeishuKnowledgeConfig",
    "FeishuKnowledgeSection",
    "FeishuKnowledgeSyncResult",
    "FeishuLinkedResource",
    "KnowledgeContextBlock",
    "KnowledgeRoute",
    "attach_feishu_knowledge_to_runtime",
    "build_feishu_knowledge_context",
    "build_feishu_knowledge_input_ref",
    "build_feishu_knowledge_reference",
    "knowledge_refs_from_runtime",
    "runtime_payload_with_feishu_knowledge",
    "search_cached_feishu_knowledge",
    "route_knowledge_query",
    "sync_feishu_knowledge",
]


def __getattr__(name: str):
    if name in {"FeishuKnowledgeSyncResult", "FeishuLinkedResource", "sync_feishu_knowledge"}:
        from automage_agents.knowledge import feishu_sync

        return getattr(feishu_sync, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
