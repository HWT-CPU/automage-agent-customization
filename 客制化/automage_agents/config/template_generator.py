"""
配置模板生成器

用于新员工注册时自动生成 Hermes、OpenClaw 和知识库配置
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import toml


@dataclass
class UserOnboardingConfig:
    """新员工入职配置"""

    # 用户基本信息
    user_id: str
    display_name: str
    role: str  # staff, manager, executive
    department_id: str
    job_title: str
    feishu_open_id: str = ""

    # 组织信息
    org_id: str = "org-001"
    manager_node_id: str = ""

    # 知识库配置
    knowledge_sections: list[dict[str, Any]] | None = None


class ConfigTemplateGenerator:
    """配置模板生成器"""

    def __init__(self, base_config_dir: str | Path = "configs", examples_dir: str | Path = "examples"):
        self.base_config_dir = Path(base_config_dir)
        self.examples_dir = Path(examples_dir)

    def generate_user_config(self, config: UserOnboardingConfig, output_path: str | Path) -> Path:
        """
        生成用户配置文件

        Args:
            config: 用户入职配置
            output_path: 输出路径

        Returns:
            生成的配置文件路径
        """
        node_id = f"{config.role}-node-{config.user_id}"

        user_config = {
            "user": {
                "node_id": node_id,
                "user_id": config.user_id,
                "role": config.role,
                "level": self._get_level_by_role(config.role),
                "department_id": config.department_id,
                "manager_node_id": config.manager_node_id,
                "display_name": config.display_name,
                "job_title": config.job_title,
                "responsibilities": self._get_default_responsibilities(config.role),
                "input_sources": self._get_default_input_sources(config.role),
                "output_requirements": self._get_default_output_requirements(config.role),
                "permission_notes": self._get_default_permission_notes(config.role),
                "personalized_context": f"{config.display_name} 的个性化上下文，请根据实际情况填写。",
            },
            "user.metadata": {
                "feishu_open_id": config.feishu_open_id or f"ou_{config.user_id}",
                "created_at": datetime.now().isoformat(),
                "created_by": "config_template_generator",
            },
        }

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with output_file.open("w", encoding="utf-8") as f:
            toml.dump(user_config, f)

        return output_file

    def generate_hermes_config(
        self,
        config: UserOnboardingConfig,
        output_path: str | Path,
        user_profile_path: str | Path,
    ) -> Path:
        """
        生成 Hermes 配置文件

        Args:
            config: 用户入职配置
            output_path: 输出路径
            user_profile_path: 用户配置文件路径

        Returns:
            生成的配置文件路径
        """
        # 加载示例配置
        example_config = self._load_toml(self.base_config_dir / "hermes.example.toml")

        # 更新配置
        hermes_config = example_config.copy()
        hermes_config["hermes"]["runtime_name"] = f"automage-hermes-{config.user_id}"
        hermes_config["hermes"]["context"]["org_id"] = config.org_id
        hermes_config["hermes"]["context"]["source_channel"] = "openclaw"

        # 根据角色启用对应的 agent
        for role in ["staff", "manager", "executive"]:
            if role in hermes_config["hermes"]["agents"]:
                hermes_config["hermes"]["agents"][role]["enabled"] = role == config.role
                if role == config.role:
                    hermes_config["hermes"]["agents"][role]["profile_path"] = str(user_profile_path)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with output_file.open("w", encoding="utf-8") as f:
            toml.dump(hermes_config, f)

        return output_file

    def generate_openclaw_config(
        self,
        config: UserOnboardingConfig,
        output_path: str | Path,
        enable_feishu: bool = True,
    ) -> Path:
        """
        生成 OpenClaw 配置文件

        Args:
            config: 用户入职配置
            output_path: 输出路径
            enable_feishu: 是否启用飞书集成

        Returns:
            生成的配置文件路径
        """
        # 加载示例配置
        example_config = self._load_toml(self.base_config_dir / "openclaw.example.toml")

        # 更新配置
        openclaw_config = example_config.copy()
        openclaw_config["openclaw"]["runtime_name"] = f"automage-openclaw-{config.user_id}"
        openclaw_config["openclaw"]["channels"]["feishu"]["enabled"] = enable_feishu

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with output_file.open("w", encoding="utf-8") as f:
            toml.dump(openclaw_config, f)

        return output_file

    def generate_knowledge_config(
        self,
        config: UserOnboardingConfig,
        output_path: str | Path,
    ) -> Path:
        """
        生成知识库配置文件

        Args:
            config: 用户入职配置
            output_path: 输出路径

        Returns:
            生成的配置文件路径
        """
        knowledge_config = {
            "knowledge": {
                "name": f"{config.display_name} 的知识库",
                "version": "1.0.0",
                "description": f"{config.role} 角色相关的业务知识、流程规范、技术文档",
                "owner_user_id": config.user_id,
                "org_id": config.org_id,
                "department_id": config.department_id,
            }
        }

        # 添加默认知识库节点
        sections = config.knowledge_sections or self._get_default_knowledge_sections(config.role)
        knowledge_config["knowledge"]["sections"] = sections

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with output_file.open("w", encoding="utf-8") as f:
            toml.dump(knowledge_config, f)

        return output_file

    def generate_user_mapping(
        self,
        config: UserOnboardingConfig,
        output_path: str | Path,
        append: bool = True,
    ) -> Path:
        """
        生成或更新用户映射文件（飞书 open_id -> user_id）

        Args:
            config: 用户入职配置
            output_path: 输出路径
            append: 是否追加到现有文件

        Returns:
            生成的映射文件路径
        """
        output_file = Path(output_path)

        # 加载现有映射
        user_mapping = {}
        if append and output_file.exists():
            with output_file.open("r", encoding="utf-8") as f:
                user_mapping = json.load(f)

        # 添加新用户映射
        feishu_open_id = config.feishu_open_id or f"ou_{config.user_id}"
        user_mapping[feishu_open_id] = config.user_id

        # 保存映射
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(user_mapping, f, ensure_ascii=False, indent=2)

        return output_file

    def generate_all_configs(
        self,
        config: UserOnboardingConfig,
        output_dir: str | Path = "configs/users",
    ) -> dict[str, Path]:
        """
        一键生成所有配置文件

        Args:
            config: 用户入职配置
            output_dir: 输出目录

        Returns:
            生成的配置文件路径字典
        """
        output_dir = Path(output_dir) / config.user_id
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {}

        # 1. 生成用户配置
        user_config_path = output_dir / f"user.{config.role}.toml"
        results["user_config"] = self.generate_user_config(config, user_config_path)

        # 2. 生成 Hermes 配置
        hermes_config_path = output_dir / "hermes.toml"
        results["hermes_config"] = self.generate_hermes_config(config, hermes_config_path, user_config_path)

        # 3. 生成 OpenClaw 配置
        openclaw_config_path = output_dir / "openclaw.toml"
        results["openclaw_config"] = self.generate_openclaw_config(config, openclaw_config_path)

        # 4. 生成知识库配置
        knowledge_config_path = output_dir / "knowledge.toml"
        results["knowledge_config"] = self.generate_knowledge_config(config, knowledge_config_path)

        # 5. 更新用户映射
        user_mapping_path = self.base_config_dir / "feishu_user_map.json"
        results["user_mapping"] = self.generate_user_mapping(config, user_mapping_path, append=True)

        return results

    # ========== 辅助方法 ==========

    def _load_toml(self, path: Path) -> dict[str, Any]:
        """加载 TOML 文件"""
        with path.open("r", encoding="utf-8") as f:
            return toml.load(f)

    def _get_level_by_role(self, role: str) -> str:
        """根据角色获取层级"""
        mapping = {
            "staff": "l1_staff",
            "manager": "l2_manager",
            "executive": "l3_executive",
        }
        return mapping.get(role, "l1_staff")

    def _get_default_responsibilities(self, role: str) -> list[str]:
        """获取默认职责"""
        mapping = {
            "staff": [
                "完成日常工作任务",
                "记录每日工作进展",
                "提交需要上级支持的问题",
            ],
            "manager": [
                "汇总部门日报",
                "识别部门风险",
                "权限内任务分发",
            ],
            "executive": [
                "审阅部门汇总",
                "确认 Dream 决策",
                "下发战略任务",
            ],
        }
        return mapping.get(role, [])

    def _get_default_input_sources(self, role: str) -> list[str]:
        """获取默认输入源"""
        mapping = {
            "staff": [
                "Manager Agent 下发的任务",
                "飞书日报卡片",
                "工作记录",
            ],
            "manager": [
                "Staff Agent 日报",
                "部门群反馈",
                "后端部门数据",
            ],
            "executive": [
                "Manager Agent 汇总",
                "Dream 机制",
                "经营目标",
            ],
        }
        return mapping.get(role, [])

    def _get_default_output_requirements(self, role: str) -> list[str]:
        """获取默认输出要求"""
        mapping = {
            "staff": [
                "每日工作进度",
                "遇到的问题",
                "已尝试解决方案",
                "是否需要上级支持",
                "明日计划",
            ],
            "manager": [
                "部门健康度",
                "聚合摘要",
                "Top 3 风险",
                "效率观察",
                "待审批事项",
            ],
            "executive": [
                "A/B 决策",
                "战略任务",
                "资源配置说明",
            ],
        }
        return mapping.get(role, [])

    def _get_default_permission_notes(self, role: str) -> list[str]:
        """获取默认权限说明"""
        mapping = {
            "staff": [
                "只能访问自己的任务与日报",
                "不能读取其他员工数据",
                "不能做部门级决策",
            ],
            "manager": [
                "只能访问本部门数据",
                "不能做公司级决策",
            ],
            "executive": [
                "重大决策需要人工确认",
                "不直接修改员工日报",
            ],
        }
        return mapping.get(role, [])

    def _get_default_knowledge_sections(self, role: str) -> list[dict[str, Any]]:
        """获取默认知识库节点"""
        base_sections = [
            {
                "id": "project_overview",
                "topic": "项目概览",
                "node_token": "YOUR_FEISHU_DOC_TOKEN_HERE",
                "labels": ["项目", "概览"],
            },
            {
                "id": "business_glossary",
                "topic": "业务术语表",
                "node_token": "YOUR_FEISHU_DOC_TOKEN_HERE",
                "labels": ["术语", "词汇表"],
            },
        ]

        role_specific = {
            "staff": [
                {
                    "id": "staff_report_template",
                    "topic": "Staff 日报模板",
                    "node_token": "YOUR_FEISHU_DOC_TOKEN_HERE",
                    "labels": ["日报", "模板", "staff"],
                },
            ],
            "manager": [
                {
                    "id": "manager_summary_guide",
                    "topic": "Manager 汇总指南",
                    "node_token": "YOUR_FEISHU_DOC_TOKEN_HERE",
                    "labels": ["汇总", "指南", "manager"],
                },
            ],
            "executive": [
                {
                    "id": "executive_decision_process",
                    "topic": "Executive 决策流程",
                    "node_token": "YOUR_FEISHU_DOC_TOKEN_HERE",
                    "labels": ["决策", "流程", "executive"],
                },
            ],
        }

        return base_sections + role_specific.get(role, [])
