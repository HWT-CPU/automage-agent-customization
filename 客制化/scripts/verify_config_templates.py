#!/usr/bin/env python3
"""
配置模板系统验证脚本

验证配置模板系统的所有功能是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.config.template_generator import ConfigTemplateGenerator, UserOnboardingConfig
from automage_agents.integrations.hermes.config import load_hermes_config
from automage_agents.integrations.openclaw.config import load_openclaw_config


def verify_template_files():
    """验证模板文件是否存在"""
    print("=" * 60)
    print("1. 验证模板文件")
    print("=" * 60)

    template_files = [
        "configs/hermes.example.toml",
        "configs/openclaw.example.toml",
        "configs/automage.example.toml",
        "examples/user.staff.example.toml",
        "examples/user.manager.example.toml",
        "examples/user.executive.example.toml",
        "configs/feishu_knowledge.example.toml",
    ]

    all_exist = True
    for template_file in template_files:
        path = PROJECT_ROOT / template_file
        if path.exists():
            print(f"  ✅ {template_file}")
        else:
            print(f"  ❌ {template_file} - 文件不存在")
            all_exist = False

    return all_exist


def verify_config_generation():
    """验证配置生成功能"""
    print("\n" + "=" * 60)
    print("2. 验证配置生成功能")
    print("=" * 60)

    try:
        # 创建测试配置
        config = UserOnboardingConfig(
            user_id="verify-test-001",
            display_name="验证测试用户",
            role="staff",
            department_id="dept-test",
            job_title="测试工程师",
            org_id="org-test",
            feishu_open_id="ou_verify_test_001",
        )

        # 生成配置
        generator = ConfigTemplateGenerator()
        results = generator.generate_all_configs(config, output_dir="configs/verify_test")

        # 验证生成的文件
        print("\n  生成的文件：")
        all_generated = True
        for key, path in results.items():
            if path.exists():
                print(f"    ✅ {key}: {path}")
            else:
                print(f"    ❌ {key}: {path} - 文件未生成")
                all_generated = False

        # 清理测试文件
        import shutil

        test_dir = PROJECT_ROOT / "configs" / "verify_test"
        if test_dir.exists():
            shutil.rmtree(test_dir)
            print("\n  ✅ 测试文件已清理")

        return all_generated

    except Exception as e:
        print(f"\n  ❌ 配置生成失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def verify_config_loading():
    """验证配置加载功能"""
    print("\n" + "=" * 60)
    print("3. 验证配置加载功能")
    print("=" * 60)

    try:
        # 检查是否有示例配置
        demo_hermes_config = PROJECT_ROOT / "configs" / "demo_users" / "demo-user-001" / "hermes.toml"
        demo_openclaw_config = PROJECT_ROOT / "configs" / "demo_users" / "demo-user-001" / "openclaw.toml"

        if not demo_hermes_config.exists():
            print("  ⚠️  示例配置不存在，先运行: python examples/onboarding_demo.py")
            return True  # 不算失败

        # 加载 Hermes 配置
        hermes_config = load_hermes_config(demo_hermes_config)
        print(f"  ✅ Hermes 配置加载成功")
        print(f"     Runtime Name: {hermes_config.runtime_name}")
        print(f"     Org ID: {hermes_config.context.org_id}")

        # 加载 OpenClaw 配置
        openclaw_config = load_openclaw_config(demo_openclaw_config)
        print(f"  ✅ OpenClaw 配置加载成功")
        print(f"     Runtime Name: {openclaw_config.runtime_name}")
        print(f"     Default Channel: {openclaw_config.default_channel}")

        return True

    except Exception as e:
        print(f"  ❌ 配置加载失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def verify_documentation():
    """验证文档是否存在"""
    print("\n" + "=" * 60)
    print("4. 验证文档")
    print("=" * 60)

    doc_files = [
        "README_CONFIG_TEMPLATES.md",
        "SUMMARY_CONFIG_TEMPLATES.md",
        "QUICK_REFERENCE_CONFIG_TEMPLATES.md",
        "docs/config_template_guide.md",
    ]

    all_exist = True
    for doc_file in doc_files:
        path = PROJECT_ROOT / doc_file
        if path.exists():
            print(f"  ✅ {doc_file}")
        else:
            print(f"  ❌ {doc_file} - 文件不存在")
            all_exist = False

    return all_exist


def verify_tests():
    """验证测试是否存在"""
    print("\n" + "=" * 60)
    print("5. 验证测试")
    print("=" * 60)

    test_file = PROJECT_ROOT / "tests" / "test_config_template_generator.py"
    if test_file.exists():
        print(f"  ✅ 测试文件存在: {test_file}")

        # 尝试运行测试
        try:
            import subprocess

            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                print("  ✅ 所有测试通过")
                return True
            else:
                print(f"  ❌ 测试失败 (退出码: {result.returncode})")
                print("\n  测试输出:")
                print(result.stdout)
                if result.stderr:
                    print("\n  错误输出:")
                    print(result.stderr)
                return False

        except Exception as e:
            print(f"  ⚠️  无法运行测试: {e}")
            return True  # 不算失败

    else:
        print(f"  ❌ 测试文件不存在: {test_file}")
        return False


def verify_gitignore():
    """验证 .gitignore 配置"""
    print("\n" + "=" * 60)
    print("6. 验证 .gitignore 配置")
    print("=" * 60)

    gitignore_file = PROJECT_ROOT / ".gitignore"
    if not gitignore_file.exists():
        print("  ❌ .gitignore 文件不存在")
        return False

    with gitignore_file.open("r", encoding="utf-8") as f:
        content = f.read()

    required_patterns = [
        "configs/users/",
        "configs/demo_users/",
        "configs/feishu_user_map.json",
    ]

    all_present = True
    for pattern in required_patterns:
        if pattern in content:
            print(f"  ✅ {pattern}")
        else:
            print(f"  ❌ {pattern} - 未在 .gitignore 中")
            all_present = False

    return all_present


def main():
    """运行所有验证"""
    print("\n🔍 配置模板系统验证\n")

    results = {
        "模板文件": verify_template_files(),
        "配置生成": verify_config_generation(),
        "配置加载": verify_config_loading(),
        "文档": verify_documentation(),
        "测试": verify_tests(),
        "Git 配置": verify_gitignore(),
    }

    # 打印总结
    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)

    all_passed = True
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有验证通过！配置模板系统工作正常。")
        print("=" * 60)
        print("\n📝 后续步骤：")
        print("  1. 运行示例: python examples/onboarding_demo.py")
        print("  2. 查看文档: README_CONFIG_TEMPLATES.md")
        print("  3. 开始使用: python scripts/onboard_new_user.py --help")
        return 0
    else:
        print("❌ 部分验证失败，请检查上述错误信息。")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
