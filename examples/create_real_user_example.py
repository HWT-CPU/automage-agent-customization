#!/usr/bin/env python3
"""
真实用户配置生成示例

演示如何为真实的新员工生成配置
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.config.template_generator import ConfigTemplateGenerator, UserOnboardingConfig


def create_real_staff_user():
    """示例：为真实员工生成配置"""
    print("=" * 60)
    print("为真实员工生成配置")
    print("=" * 60)

    # 真实员工信息
    config = UserOnboardingConfig(
        user_id="user-zhangsan-001",
        display_name="张三",
        role="staff",
        department_id="dept-sales",
        job_title="销售专员",
        org_id="org-automage",
        manager_node_id="manager-node-sales-001",
        feishu_open_id="ou_zhangsan_real_001",
    )

    # 生成配置（注意：output_dir 使用 configs/users）
    generator = ConfigTemplateGenerator()
    results = generator.generate_all_configs(config, output_dir="configs/users")

    print("\n✅ 配置生成成功！")
    print("\n生成的文件：")
    for key, path in results.items():
        print(f"  - {key}: {path}")

    print("\n📝 后续步骤：")
    print("  1. 检查并编辑用户配置")
    print("  2. 更新知识库配置中的飞书文档 token")
    print("  3. 配置飞书应用凭证（如需启用飞书集成）")
    print("  4. 运行测试验证配置正确性")


def create_real_manager_user():
    """示例：为真实经理生成配置"""
    print("\n" + "=" * 60)
    print("为真实经理生成配置")
    print("=" * 60)

    config = UserOnboardingConfig(
        user_id="manager-lisi-001",
        display_name="李四",
        role="manager",
        department_id="dept-sales",
        job_title="销售部门经理",
        org_id="org-automage",
        manager_node_id="executive-node-001",
        feishu_open_id="ou_lisi_real_001",
    )

    generator = ConfigTemplateGenerator()
    results = generator.generate_all_configs(config, output_dir="configs/users")

    print("\n✅ 经理配置生成成功！")
    print(f"\n用户配置: {results['user_config']}")


def create_real_user_with_custom_knowledge():
    """示例：为员工生成配置并自定义知识库"""
    print("\n" + "=" * 60)
    print("为员工生成配置（自定义知识库）")
    print("=" * 60)

    # 自定义知识库节点（替换为真实的飞书文档 token）
    custom_knowledge = [
        {
            "id": "sales_playbook",
            "topic": "销售手册",
            "node_token": "doccnSalesPlaybookXXXXXXXX",  # 替换为真实 token
            "labels": ["销售", "手册", "培训"],
        },
        {
            "id": "customer_cases",
            "topic": "客户案例库",
            "node_token": "doccnCustomerCasesXXXXXXXX",  # 替换为真实 token
            "labels": ["客户", "案例", "参考"],
        },
        {
            "id": "product_catalog",
            "topic": "产品目录",
            "node_token": "doccnProductCatalogXXXXXXXX",  # 替换为真实 token
            "labels": ["产品", "目录", "价格"],
        },
    ]

    config = UserOnboardingConfig(
        user_id="user-wangwu-001",
        display_name="王五",
        role="staff",
        department_id="dept-sales",
        job_title="高级销售专员",
        org_id="org-automage",
        manager_node_id="manager-node-sales-001",
        feishu_open_id="ou_wangwu_real_001",
        knowledge_sections=custom_knowledge,
    )

    generator = ConfigTemplateGenerator()
    results = generator.generate_all_configs(config, output_dir="configs/users")

    print("\n✅ 自定义知识库配置生成成功！")
    print(f"\n知识库配置: {results['knowledge_config']}")


def main():
    """运行示例"""
    print("\n🚀 真实用户配置生成示例\n")

    try:
        # 运行示例
        create_real_staff_user()
        create_real_manager_user()
        create_real_user_with_custom_knowledge()

        print("\n" + "=" * 60)
        print("✅ 所有示例运行完成！")
        print("=" * 60)
        print("\n📁 生成的配置文件位于: configs/users/")
        print("\n⚠️  注意事项：")
        print("  - configs/users/ 目录已添加到 .gitignore")
        print("  - 不要将包含真实凭证的配置文件提交到版本控制")
        print("  - 生产环境使用环境变量或密钥管理器")

    except Exception as e:
        print(f"\n❌ 示例运行失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
