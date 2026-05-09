from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.knowledge.feishu_wiki import load_feishu_knowledge_config, route_knowledge_query
from automage_agents.integrations.feishu import FeishuDocsCliClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Route a query to a Feishu Wiki knowledge section.")
    parser.add_argument("query", help="Question or task description to route.")
    parser.add_argument("--config", default="configs/feishu_knowledge.example.toml")
    parser.add_argument("--fetch", action="store_true", help="Fetch routed Wiki section through lark-cli docs +fetch.")
    parser.add_argument("--cache-dir", default="_cache/feishu_wiki")
    parser.add_argument("--doc-format", choices=["markdown", "xml", "text"], default="markdown")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    config = load_feishu_knowledge_config(args.config)
    route = route_knowledge_query(args.query, config)
    fetch_result = None
    if args.fetch:
        fetch_result = FeishuDocsCliClient(cache_dir=Path(args.cache_dir)).fetch_doc(
            doc=route.section.node_token,
            doc_format=args.doc_format,
        )
    if args.json:
        print(json.dumps({"route": route.to_dict(), "fetch": fetch_result.to_dict() if fetch_result else None}, ensure_ascii=False, indent=2))
        if fetch_result and not fetch_result.ok:
            raise SystemExit(fetch_result.returncode or 1)
        return
    print(f"分区：{route.section.id} {route.section.topic}")
    print(f"node_token：{route.section.node_token}")
    print(f"匹配关键词：{', '.join(route.matched_keywords) if route.matched_keywords else '无，默认使用首个分区'}")
    print(f"获取正文：{route.fetch_command}")
    if fetch_result:
        if fetch_result.ok:
            print(f"已缓存：{fetch_result.cache_path}")
        else:
            print(f"抓取失败：{fetch_result.error}")
            raise SystemExit(fetch_result.returncode or 1)


if __name__ == "__main__":
    main()
