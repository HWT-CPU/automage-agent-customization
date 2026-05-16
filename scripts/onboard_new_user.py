#!/usr/bin/env python3
"""
新员工入职脚本

自动生成 Hermes、OpenClaw 和知识库配置
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.config.template_generator import ConfigTemplateGenerator, UserOnboardingConfig


def main():
    parser = argparse.ArgumentParser(description="新员工入职配置生成工具")

    # 必填参数
    parser.add_argument("--user-id", required=True, help="用户 ID，例如：user-001")
    parser.add_argument("--display-name", required=True, help="显示名称，例如：张三")
    parser.add_argument(
        "--role",
        required=True,
        choices=["staff", "manager", "executive"],
        help="角色：staff（员工）、manager（经理）、executive（高管）",
    )
    parser.add_argument("--department-id", required=True, help="部门 ID，例如：dept-sales")
    parser.add_argument("--job-title", required=True, help="职位名称，例如：销售专员")

    # 可选参数
    parser.add_argument("--org-id", default="org-001", help="组织 ID（默认：org-001）")
    parser.add_argument("--manager-node-id", default="", help="上级节点 ID（可选）")
    parser.add_argument("--feishu-open-id", default="", help="飞书 Open ID（可选，默认自动生成）")
    parser.add_argument("--output-dir", default="configs/users", help="输出目录（默认：configs/users）")

    args = parser.parse_args()

    # 创建配置对象
    config = UserOnboardingConfig(
        user_id=args.user_id,
        display_name=args.display_name,
        role=args.role,
        department_id=args.department_id,
        job_title=args.job_title,
        org_id=args.org_id,
        manager_node_id=args.manager_node_id,
        feishu_open_id=args.feishu_open_id,
    )

    # 生成配置
    generator = ConfigTemplateGenerator()
    print(f"\n🚀 开始为 {config.display_name} ({config.user_id}) 生成配置...\n")

    try:
        results = generator.generate_all_configs(config, output_dir=args.output_dir)

        print("✅ 配置生成成功！\n")
        print("📁 生成的文件：")
        for key, path in results.items():
            print(f"  - {key}: {path}")

        print("\n📝 后续步骤：")
        print(f"  1. 检查并编辑用户配置：{results['user_config']}")
        print(f"  2. 如需启用飞书集成，请配置飞书凭证")
        print(f"  3. 更新知识库配置中的飞书文档 token：{results['knowledge_config']}")
        print(f"  4. 运行系统测试确认配置正确")

    except Exception as e:
        print(f"❌ 配置生成失败：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
