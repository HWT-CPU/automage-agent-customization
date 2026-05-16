#!/usr/bin/env python3
"""
新员工入职配置生成示例

演示如何使用配置模板生成器为新员工创建完整的配置
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.config.template_generator import ConfigTemplateGenerator, UserOnboardingConfig


def demo_single_user_onboarding():
    """示例 1: 单个用户入职"""
    print("=" * 60)
    print("示例 1: 单个用户入职")
    print("=" * 60)

    # 创建用户配置
    config = UserOnboardingConfig(
        user_id="demo-user-001",
        display_name="张三",
        role="staff",
        department_id="dept-sales",
        job_title="销售专员",
        org_id="org-automage",
        manager_node_id="manager-node-001",
        feishu_open_id="ou_demo_001",
    )

    # 生成配置
    generator = ConfigTemplateGenerator()
    results = generator.generate_all_configs(config, output_dir="configs/demo_users")

    print("\n✅ 配置生成成功！")
    print("\n生成的文件：")
    for key, path in results.items():
        print(f"  - {key}: {path}")


def demo_manager_onboarding():
    """示例 2: 经理入职"""
    print("\n" + "=" * 60)
    print("示例 2: 经理入职")
    print("=" * 60)

    config = UserOnboardingConfig(
        user_id="demo-manager-001",
        display_name="李四",
        role="manager",
        department_id="dept-sales",
        job_title="销售部门经理",
        org_id="org-automage",
        manager_node_id="executive-node-001",
        feishu_open_id="ou_demo_manager_001",
    )

    generator = ConfigTemplateGenerator()
    results = generator.generate_all_configs(config, output_dir="configs/demo_users")

    print("\n✅ 经理配置生成成功！")
    print(f"\n用户配置: {results['user_config']}")


def demo_custom_knowledge():
    """示例 3: 自定义知识库节点"""
    print("\n" + "=" * 60)
    print("示例 3: 自定义知识库节点")
    print("=" * 60)

    # 自定义知识库节点
    custom_knowledge = [
        {
            "id": "sales_playbook",
            "topic": "销售手册",
            "node_token": "doccnSalesPlaybookXXXXXXXX",
            "labels": ["销售", "手册", "培训"],
        },
        {
            "id": "customer_cases",
            "topic": "客户案例库",
            "node_token": "doccnCustomerCasesXXXXXXXX",
            "labels": ["客户", "案例", "参考"],
        },
        {
            "id": "product_catalog",
            "topic": "产品目录",
            "node_token": "doccnProductCatalogXXXXXXXX",
            "labels": ["产品", "目录", "价格"],
        },
    ]

    config = UserOnboardingConfig(
        user_id="demo-user-002",
        display_name="王五",
        role="staff",
        department_id="dept-sales",
        job_title="高级销售专员",
        org_id="org-automage",
        manager_node_id="manager-node-001",
        feishu_open_id="ou_demo_002",
        knowledge_sections=custom_knowledge,
    )

    generator = ConfigTemplateGenerator()
    results = generator.generate_all_configs(config, output_dir="configs/demo_users")

    print("\n✅ 自定义知识库配置生成成功！")
    print(f"\n知识库配置: {results['knowledge_config']}")


def demo_batch_onboarding():
    """示例 4: 批量用户入职"""
    print("\n" + "=" * 60)
    print("示例 4: 批量用户入职")
    print("=" * 60)

    # 批量用户列表
    users = [
        {
            "user_id": "demo-user-003",
            "display_name": "赵六",
            "role": "staff",
            "department_id": "dept-engineering",
            "job_title": "软件工程师",
            "manager_node_id": "manager-node-002",
            "feishu_open_id": "ou_demo_003",
        },
        {
            "user_id": "demo-user-004",
            "display_name": "孙七",
            "role": "staff",
            "department_id": "dept-engineering",
            "job_title": "测试工程师",
            "manager_node_id": "manager-node-002",
            "feishu_open_id": "ou_demo_004",
        },
        {
            "user_id": "demo-user-005",
            "display_name": "周八",
            "role": "staff",
            "department_id": "dept-engineering",
            "job_title": "DevOps 工程师",
            "manager_node_id": "manager-node-002",
            "feishu_open_id": "ou_demo_005",
        },
    ]

    generator = ConfigTemplateGenerator()
    print("\n开始批量生成配置...")

    for user_data in users:
        config = UserOnboardingConfig(org_id="org-automage", **user_data)
        results = generator.generate_all_configs(config, output_dir="configs/demo_users")
        print(f"  ✅ {config.display_name} ({config.user_id})")

    print("\n✅ 批量配置生成完成！")


def demo_executive_onboarding():
    """示例 5: 高管入职"""
    print("\n" + "=" * 60)
    print("示例 5: 高管入职")
    print("=" * 60)

    config = UserOnboardingConfig(
        user_id="demo-executive-001",
        display_name="郑九",
        role="executive",
        department_id="company",
        job_title="公司 CEO",
        org_id="org-automage",
        manager_node_id="",  # 高管没有上级
        feishu_open_id="ou_demo_executive_001",
    )

    generator = ConfigTemplateGenerator()
    results = generator.generate_all_configs(config, output_dir="configs/demo_users")

    print("\n✅ 高管配置生成成功！")
    print(f"\n用户配置: {results['user_config']}")
    print(f"Hermes 配置: {results['hermes_config']}")


def main():
    """运行所有示例"""
    print("\n🚀 AutoMage 新员工入职配置生成示例\n")

    try:
        # 运行所有示例
        demo_single_user_onboarding()
        demo_manager_onboarding()
        demo_custom_knowledge()
        demo_batch_onboarding()
        demo_executive_onboarding()

        print("\n" + "=" * 60)
        print("✅ 所有示例运行完成！")
        print("=" * 60)
        print("\n📁 生成的配置文件位于: configs/demo_users/")
        print("\n📝 后续步骤：")
        print("  1. 检查生成的配置文件")
        print("  2. 根据实际情况修改配置")
        print("  3. 更新知识库配置中的飞书文档 token")
        print("  4. 配置飞书应用凭证（如需启用飞书集成）")
        print("  5. 运行测试验证配置正确性")

    except Exception as e:
        print(f"\n❌ 示例运行失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
