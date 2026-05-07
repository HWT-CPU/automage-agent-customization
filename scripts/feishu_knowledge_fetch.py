from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.integrations.feishu import FeishuDocsCliClient
from automage_agents.knowledge.feishu_wiki import load_feishu_knowledge_config, route_knowledge_query


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Feishu Wiki/Docs content through lark-cli and cache it locally.")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--query", help="Route a project question to a Wiki section before fetching.")
    target.add_argument("--doc", help="Fetch a direct Feishu doc/wiki token or URL.")
    parser.add_argument("--config", default="configs/feishu_knowledge.example.toml")
    parser.add_argument("--cache-dir", default="_cache/feishu_wiki")
    parser.add_argument("--doc-format", choices=["markdown", "xml", "text"], default="markdown")
    parser.add_argument("--detail", choices=["simple", "with-ids", "full"], default="simple")
    parser.add_argument("--scope", choices=["outline", "range", "keyword", "section"])
    parser.add_argument("--keyword")
    parser.add_argument("--start-block-id")
    parser.add_argument("--end-block-id")
    parser.add_argument("--max-depth", type=int)
    parser.add_argument("--executable", default="lark-cli")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    route = None
    doc = args.doc
    if args.query:
        config = load_feishu_knowledge_config(args.config)
        route = route_knowledge_query(args.query, config)
        doc = route.section.node_token

    client = FeishuDocsCliClient(executable=args.executable, cache_dir=Path(args.cache_dir))
    command = client._build_fetch_command(
        doc=doc,
        doc_format=args.doc_format,
        detail=args.detail,
        scope=args.scope,
        keyword=args.keyword,
        start_block_id=args.start_block_id,
        end_block_id=args.end_block_id,
        max_depth=args.max_depth,
    )
    if args.dry_run:
        output = {"doc": doc, "route": route.to_dict() if route else None, "command": command}
        print(json.dumps(output, ensure_ascii=False, indent=2) if args.json else " ".join(command))
        return

    result = client.fetch_doc(
        doc=doc,
        doc_format=args.doc_format,
        detail=args.detail,
        scope=args.scope,
        keyword=args.keyword,
        start_block_id=args.start_block_id,
        end_block_id=args.end_block_id,
        max_depth=args.max_depth,
    )
    output = {"route": route.to_dict() if route else None, "fetch": result.to_dict()}
    if args.json or not result.ok:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"已缓存：{result.cache_path}")
    if not result.ok:
        raise SystemExit(result.returncode or 1)


if __name__ == "__main__":
    main()
