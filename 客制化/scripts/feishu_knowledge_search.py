from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.knowledge.local_cache import search_cached_feishu_knowledge


def main() -> None:
    parser = argparse.ArgumentParser(description="Search locally cached Feishu knowledge content.")
    parser.add_argument("query")
    parser.add_argument("--cache-dir", default="_cache/feishu_wiki")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--max-snippet-chars", type=int, default=1200)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    hits = search_cached_feishu_knowledge(
        query=args.query,
        cache_dir=args.cache_dir,
        limit=args.limit,
        max_snippet_chars=args.max_snippet_chars,
    )
    if args.json:
        print(json.dumps({"query": args.query, "hits": [hit.to_dict() for hit in hits]}, ensure_ascii=False, indent=2))
        return
    for index, hit in enumerate(hits, start=1):
        print(f"[{index}] {hit.title} score={hit.score}")
        print(f"token={hit.token} cache={hit.cache_path}")
        print(hit.snippet)
        print()


if __name__ == "__main__":
    main()
