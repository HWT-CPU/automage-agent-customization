from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.integrations.feishu import FeishuDocsCliClient
from automage_agents.knowledge.feishu_sync import sync_feishu_knowledge
from automage_agents.knowledge.feishu_wiki import load_feishu_knowledge_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync Feishu Wiki section indexes and linked docs into local cache.")
    parser.add_argument("--config", default="configs/feishu_knowledge.example.toml")
    parser.add_argument("--cache-dir", default="_cache/feishu_wiki")
    parser.add_argument("--doc-format", choices=["markdown", "xml", "text"], default="markdown")
    parser.add_argument("--detail", choices=["simple", "with-ids", "full"], default="simple")
    parser.add_argument("--executable", default="lark-cli")
    parser.add_argument("--no-linked-docs", action="store_true", help="Only fetch section indexes, do not fetch obj_token documents.")
    parser.add_argument("--include-files", action="store_true", help="Also attempt to fetch file_token resources with docs +fetch.")
    parser.add_argument("--stop-on-error", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    config = load_feishu_knowledge_config(args.config)
    client = FeishuDocsCliClient(executable=args.executable, cache_dir=Path(args.cache_dir))
    result = sync_feishu_knowledge(
        config=config,
        client=client,
        doc_format=args.doc_format,
        detail=args.detail,
        include_linked_docs=not args.no_linked_docs,
        include_files=args.include_files,
        stop_on_error=args.stop_on_error,
    )
    output = result.to_dict()
    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    ok_sections = sum(1 for section in result.sections if section["ok"])
    ok_resources = sum(1 for resource in result.linked_resources if resource.ok)
    pending_files = sum(1 for resource in result.linked_resources if resource.token_kind == "file_token" and resource.ok is None)
    failed_resources = [resource for resource in result.linked_resources if resource.ok is False]
    print(f"分区索引：{ok_sections}/{len(result.sections)} 已缓存")
    print(f"正文文档：{ok_resources}/{len(result.linked_resources)} 已缓存")
    if pending_files:
        print(f"附件资源：{pending_files} 个 file_token 已记录，默认未抓取")
    if failed_resources:
        print(f"失败资源：{len(failed_resources)}")
    print(f"Manifest：{result.manifest_path}")
    if any(not section["ok"] for section in result.sections) or failed_resources:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
