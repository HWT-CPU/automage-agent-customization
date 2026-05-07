from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.core.enums import RuntimeChannel
from automage_agents.core.models import RuntimeContextV0
from automage_agents.knowledge.runtime_context import attach_feishu_knowledge_to_runtime
from automage_agents.templates.prompt_builder import build_agent_prompt_preview


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview Agent prompt with injected Feishu knowledge runtime context.")
    parser.add_argument("query")
    parser.add_argument("--role", choices=["staff", "manager", "executive"], default="staff")
    parser.add_argument("--cache-dir", default="_cache/feishu_wiki")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--max-context-chars", type=int, default=3000)
    parser.add_argument("--workflow-stage", default="knowledge_query")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    runtime = RuntimeContextV0(
        workflow_stage=args.workflow_stage,
        source_channel=RuntimeChannel.CLI,
    )
    attach_feishu_knowledge_to_runtime(
        runtime=runtime,
        query=args.query,
        cache_dir=args.cache_dir,
        limit=args.limit,
        max_context_chars=args.max_context_chars,
    )
    preview = build_agent_prompt_preview(role=args.role, runtime_payload=runtime.to_dict())
    if args.json:
        print(json.dumps(preview.to_dict(), ensure_ascii=False, indent=2))
        return
    print(preview.prompt_text)


if __name__ == "__main__":
    main()
