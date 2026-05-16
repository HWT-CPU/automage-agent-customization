#!/usr/bin/env python3
"""
飞书知识库同步脚本

从飞书下载知识库文档到本地缓存，供 AI 分析使用。
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from automage_agents.integrations.feishu import FeishuDocsCliClient
from automage_agents.knowledge.feishu_sync import sync_feishu_knowledge
from automage_agents.knowledge.feishu_wiki import load_feishu_knowledge_config


def main():
    parser = argparse.ArgumentParser(description="同步飞书知识库到本地缓存")
    parser.add_argument(
        "--config",
        default="configs/feishu_knowledge.toml",
        help="飞书知识库配置文件路径（默认：configs/feishu_knowledge.toml）",
    )
    parser.add_argument(
        "--cache-dir",
        default="_cache/feishu_wiki",
        help="本地缓存目录（默认：_cache/feishu_wiki）",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "docx"],
        default="markdown",
        help="文档格式（默认：markdown）",
    )
    parser.add_argument(
        "--detail",
        choices=["simple", "full"],
        default="simple",
        help="详细程度（默认：simple）",
    )
    parser.add_argument(
        "--no-linked-docs",
        action="store_true",
        help="不下载链接的文档",
    )
    parser.add_argument(
        "--include-files",
        action="store_true",
        help="包含文件附件",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="遇到错误时停止",
    )
    
    args = parser.parse_args()
    
    # 加载配置
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        print(f"提示：请先创建配置文件，参考 configs/feishu_knowledge.example.toml")
        return 1
    
    try:
        config = load_feishu_knowledge_config(str(config_path))
    except Exception as e:
        print(f"❌ 加载配置失败: {e}")
        return 1
    
    # 创建客户端
    cache_dir = Path(args.cache_dir)
    client = FeishuDocsCliClient(cache_dir=cache_dir)
    
    print(f"[INFO] 开始同步飞书知识库...")
    print(f"   配置文件: {config_path}")
    print(f"   缓存目录: {cache_dir}")
    print(f"   文档格式: {args.format}")
    print(f"   知识库节点数: {len(config.sections)}")
    print()
    
    # 同步知识库
    try:
        result = sync_feishu_knowledge(
            config=config,
            client=client,
            doc_format=args.format,
            detail=args.detail,
            include_linked_docs=not args.no_linked_docs,
            include_files=args.include_files,
            stop_on_error=args.stop_on_error,
        )
    except Exception as e:
        print(f"❌ 同步失败: {e}")
        return 1
    
    # 输出结果
    print("[SUCCESS] 同步完成！")
    print()
    print(f"[STATS] 同步统计:")
    print(f"   主节点: {len(result.sections)}")
    print(f"   链接文档: {len(result.linked_resources)}")
    print(f"   清单文件: {result.manifest_path}")
    print()
    
    # 显示主节点状态
    success_count = sum(1 for s in result.sections if s.get("ok"))
    print(f"主节点状态: {success_count}/{len(result.sections)} 成功")
    for section in result.sections:
        status = "[OK]" if section.get("ok") else "[FAIL]"
        topic = section.get("topic", "unknown")
        error = section.get("error", "")
        print(f"  {status} {topic}")
        if error:
            print(f"     错误: {error}")
    print()
    
    # 显示链接文档状态
    if result.linked_resources:
        linked_success = sum(1 for r in result.linked_resources if r.ok)
        print(f"链接文档状态: {linked_success}/{len(result.linked_resources)} 成功")
        for resource in result.linked_resources[:10]:  # 只显示前 10 个
            status = "[OK]" if resource.ok else "[FAIL]"
            print(f"  {status} {resource.title} ({resource.token_kind})")
            if resource.error:
                print(f"     错误: {resource.error}")
        if len(result.linked_resources) > 10:
            print(f"  ... 还有 {len(result.linked_resources) - 10} 个文档")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
