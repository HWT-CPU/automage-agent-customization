"""
测试配置模板生成器
"""

import json
import tempfile
import unittest
from pathlib import Path

import toml

from automage_agents.config.template_generator import ConfigTemplateGenerator, UserOnboardingConfig


class TestConfigTemplateGenerator(unittest.TestCase):
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = ConfigTemplateGenerator()

    def test_generate_user_config_staff(self):
        """测试生成员工配置"""
        config = UserOnboardingConfig(
            user_id="test-user-001",
            display_name="测试员工",
            role="staff",
            department_id="dept-test",
            job_title="测试工程师",
            feishu_open_id="ou_test_001",
        )

        output_path = Path(self.temp_dir) / "user.staff.toml"
        result_path = self.generator.generate_user_config(config, output_path)

        # 验证文件存在
        self.assertTrue(result_path.exists())

        # 验证内容
        user_config = toml.load(result_path)
        self.assertEqual(user_config["user"]["user_id"], "test-user-001")
        self.assertEqual(user_config["user"]["role"], "staff")
        self.assertEqual(user_config["user"]["display_name"], "测试员工")
        self.assertEqual(user_config["user"]["level"], "l1_staff")
        self.assertEqual(user_config["user.metadata"]["feishu_open_id"], "ou_test_001")

    def test_generate_user_config_manager(self):
        """测试生成经理配置"""
        config = UserOnboardingConfig(
            user_id="test-manager-001",
            display_name="测试经理",
            role="manager",
            department_id="dept-test",
            job_title="测试部门经理",
            manager_node_id="executive-node-001",
        )

        output_path = Path(self.temp_dir) / "user.manager.toml"
        result_path = self.generator.generate_user_config(config, output_path)

        # 验证内容
        user_config = toml.load(result_path)
        self.assertEqual(user_config["user"]["role"], "manager")
        self.assertEqual(user_config["user"]["level"], "l2_manager")
        self.assertEqual(user_config["user"]["manager_node_id"], "executive-node-001")

    def test_generate_hermes_config(self):
        """测试生成 Hermes 配置"""
        config = UserOnboardingConfig(
            user_id="test-user-002",
            display_name="测试用户",
            role="staff",
            department_id="dept-test",
            job_title="测试职位",
            org_id="org-test",
        )

        user_profile_path = Path(self.temp_dir) / "user.staff.toml"
        output_path = Path(self.temp_dir) / "hermes.toml"

        result_path = self.generator.generate_hermes_config(config, output_path, user_profile_path)

        # 验证文件存在
        self.assertTrue(result_path.exists())

        # 验证内容
        hermes_config = toml.load(result_path)
        self.assertEqual(hermes_config["hermes"]["runtime_name"], "automage-hermes-test-user-002")
        self.assertEqual(hermes_config["hermes"]["context"]["org_id"], "org-test")
        self.assertTrue(hermes_config["hermes"]["agents"]["staff"]["enabled"])
        self.assertFalse(hermes_config["hermes"]["agents"]["manager"]["enabled"])

    def test_generate_openclaw_config(self):
        """测试生成 OpenClaw 配置"""
        config = UserOnboardingConfig(
            user_id="test-user-003",
            display_name="测试用户",
            role="staff",
            department_id="dept-test",
            job_title="测试职位",
        )

        output_path = Path(self.temp_dir) / "openclaw.toml"
        result_path = self.generator.generate_openclaw_config(config, output_path, enable_feishu=True)

        # 验证文件存在
        self.assertTrue(result_path.exists())

        # 验证内容
        openclaw_config = toml.load(result_path)
        self.assertEqual(openclaw_config["openclaw"]["runtime_name"], "automage-openclaw-test-user-003")
        self.assertTrue(openclaw_config["openclaw"]["channels"]["feishu"]["enabled"])

    def test_generate_knowledge_config(self):
        """测试生成知识库配置"""
        config = UserOnboardingConfig(
            user_id="test-user-004",
            display_name="测试用户",
            role="staff",
            department_id="dept-test",
            job_title="测试职位",
            org_id="org-test",
        )

        output_path = Path(self.temp_dir) / "knowledge.toml"
        result_path = self.generator.generate_knowledge_config(config, output_path)

        # 验证文件存在
        self.assertTrue(result_path.exists())

        # 验证内容
        knowledge_config = toml.load(result_path)
        self.assertEqual(knowledge_config["knowledge"]["owner_user_id"], "test-user-004")
        self.assertEqual(knowledge_config["knowledge"]["org_id"], "org-test")
        self.assertGreater(len(knowledge_config["knowledge"]["sections"]), 0)

    def test_generate_user_mapping(self):
        """测试生成用户映射"""
        config = UserOnboardingConfig(
            user_id="test-user-005",
            display_name="测试用户",
            role="staff",
            department_id="dept-test",
            job_title="测试职位",
            feishu_open_id="ou_test_005",
        )

        output_path = Path(self.temp_dir) / "feishu_user_map.json"
        result_path = self.generator.generate_user_mapping(config, output_path, append=False)

        # 验证文件存在
        self.assertTrue(result_path.exists())

        # 验证内容
        with result_path.open("r", encoding="utf-8") as f:
            user_mapping = json.load(f)
        self.assertEqual(user_mapping["ou_test_005"], "test-user-005")

    def test_generate_user_mapping_append(self):
        """测试追加用户映射"""
        output_path = Path(self.temp_dir) / "feishu_user_map.json"

        # 创建初始映射
        initial_mapping = {"ou_existing": "user-existing"}
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(initial_mapping, f)

        # 追加新用户
        config = UserOnboardingConfig(
            user_id="test-user-006",
            display_name="测试用户",
            role="staff",
            department_id="dept-test",
            job_title="测试职位",
            feishu_open_id="ou_test_006",
        )

        result_path = self.generator.generate_user_mapping(config, output_path, append=True)

        # 验证内容
        with result_path.open("r", encoding="utf-8") as f:
            user_mapping = json.load(f)
        self.assertEqual(user_mapping["ou_existing"], "user-existing")
        self.assertEqual(user_mapping["ou_test_006"], "test-user-006")

    def test_generate_all_configs(self):
        """测试一键生成所有配置"""
        config = UserOnboardingConfig(
            user_id="test-user-007",
            display_name="测试用户",
            role="manager",
            department_id="dept-test",
            job_title="测试经理",
            org_id="org-test",
            manager_node_id="executive-node-001",
            feishu_open_id="ou_test_007",
        )

        output_dir = Path(self.temp_dir) / "users"
        results = self.generator.generate_all_configs(config, output_dir=output_dir)

        # 验证所有文件都生成了
        self.assertIn("user_config", results)
        self.assertIn("hermes_config", results)
        self.assertIn("openclaw_config", results)
        self.assertIn("knowledge_config", results)
        self.assertIn("user_mapping", results)

        # 验证所有文件都存在
        for key, path in results.items():
            self.assertTrue(path.exists(), f"{key} 文件不存在: {path}")

    def test_custom_knowledge_sections(self):
        """测试自定义知识库节点"""
        custom_sections = [
            {
                "id": "custom_doc",
                "topic": "自定义文档",
                "node_token": "doccnXXXXXXXXXXXXXXXXXXXX",
                "labels": ["自定义", "测试"],
            }
        ]

        config = UserOnboardingConfig(
            user_id="test-user-008",
            display_name="测试用户",
            role="staff",
            department_id="dept-test",
            job_title="测试职位",
            knowledge_sections=custom_sections,
        )

        output_path = Path(self.temp_dir) / "knowledge.toml"
        result_path = self.generator.generate_knowledge_config(config, output_path)

        # 验证自定义节点
        knowledge_config = toml.load(result_path)
        sections = knowledge_config["knowledge"]["sections"]
        custom_section = next((s for s in sections if s["id"] == "custom_doc"), None)
        self.assertIsNotNone(custom_section)
        self.assertEqual(custom_section["topic"], "自定义文档")


if __name__ == "__main__":
    unittest.main()
