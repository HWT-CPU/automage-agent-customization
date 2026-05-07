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


def main() -> None:
    parser = argparse.ArgumentParser(description="Build RuntimeContextV0 payload with Feishu knowledge input_refs.")
    parser.add_argument("query")
    parser.add_argument("--cache-dir", default="_cache/feishu_wiki")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--max-context-chars", type=int, default=4000)
    parser.add_argument("--org-id", default="org-001")
    parser.add_argument("--run-date", default="")
    parser.add_argument("--workflow-name", default="automage_mvp_dag")
    parser.add_argument("--workflow-stage", default="knowledge_query")
    parser.add_argument("--source-channel", choices=["mock", "cli", "feishu"], default="cli")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    runtime = RuntimeContextV0(
        org_id=args.org_id,
        run_date=args.run_date,
        workflow_name=args.workflow_name,
        workflow_stage=args.workflow_stage,
        source_channel=RuntimeChannel(args.source_channel),
    )
    context_block = attach_feishu_knowledge_to_runtime(
        runtime=runtime,
        query=args.query,
        cache_dir=args.cache_dir,
        limit=args.limit,
        max_context_chars=args.max_context_chars,
    )
    output = {
        "runtime_payload": runtime.to_dict(),
        "knowledge_context": context_block.to_dict(),
    }
    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return
    print(json.dumps(runtime.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
