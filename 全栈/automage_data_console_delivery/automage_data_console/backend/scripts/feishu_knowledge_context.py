from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.knowledge.local_cache import build_feishu_knowledge_context


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an Agent prompt context block from cached Feishu knowledge.")
    parser.add_argument("query")
    parser.add_argument("--cache-dir", default="_cache/feishu_wiki")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--max-snippet-chars", type=int, default=1200)
    parser.add_argument("--max-context-chars", type=int, default=4000)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    context_block = build_feishu_knowledge_context(
        query=args.query,
        cache_dir=args.cache_dir,
        limit=args.limit,
        max_snippet_chars=args.max_snippet_chars,
        max_context_chars=args.max_context_chars,
    )
    if args.json:
        print(json.dumps(context_block.to_dict(), ensure_ascii=False, indent=2))
        return
    print(context_block.context_text)


if __name__ == "__main__":
    main()
