"""
配置和数据验证工具

优化点：
1. 配置文件验证
2. Skill 参数验证
3. 数据格式验证
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from automage_agents.core.exceptions import ConfigurationError


def validate_config_file(config_path: str | Path) -> dict[str, Any]:
    """
    验证配置文件是否存在且格式正确
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        dict: 验证结果
    
    Raises:
        ConfigurationError: 配置文件无效时
    """
    path = Path(config_path)
    
    if not path.exists():
        raise ConfigurationError(f"配置文件不存在: {path}")
    
    if not path.is_file():
        raise ConfigurationError(f"配置路径不是文件: {path}")
    
    if path.suffix not in {".toml", ".json", ".yaml", ".yml"}:
        raise ConfigurationError(f"不支持的配置文件格式: {path.suffix}")
    
    return {
        "valid": True,
        "path": str(path.absolute()),
        "format": path.suffix[1:],
    }


def validate_skill_payload(skill_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """
    验证 Skill 参数是否完整
    
    Args:
        skill_name: Skill 名称
        payload: Skill 参数
    
    Returns:
        dict: 验证结果
    """
    # Skill 必需参数定义
    required_params = {
        "post_daily_report": [
            "timestamp",
            "work_progress",
            "issues_faced",
            "solution_attempt",
            "need_support",
            "next_day_plan",
        ],
        "update_my_task": ["task_id"],
        "import_staff_daily_report_from_markdown": ["markdown_text"],
        "read_staff_daily_report": ["record_date"],
        "generate_manager_report": [
            "dept_id",
            "overall_health",
            "aggregated_summary",
            "top_3_risks",
            "workforce_efficiency",
            "pending_approvals",
        ],
        "delegate_task": [
            "assignee_user_id",
            "task_title",
            "task_description",
            "priority",
        ],
        "dream_decision_engine": ["summary_id"],
        "commit_decision": ["summary_id", "selected_option_id", "task_candidates"],
    }
    
    if skill_name not in required_params:
        # 未定义必需参数的 Skill，跳过验证
        return {"valid": True, "missing_params": []}
    
    required = required_params[skill_name]
    missing = [param for param in required if param not in payload]
    
    return {
        "valid": len(missing) == 0,
        "missing_params": missing,
        "skill_name": skill_name,
    }


def validate_identity_headers(headers: dict[str, str]) -> dict[str, Any]:
    """
    验证身份认证 Headers 是否完整
    
    Args:
        headers: HTTP Headers
    
    Returns:
        dict: 验证结果
    """
    required_headers = ["X-User-Id", "X-Role", "X-Node-Id"]
    missing = [h for h in required_headers if h not in headers]
    
    return {
        "valid": len(missing) == 0,
        "missing_headers": missing,
    }


def validate_agent_run_request(request_data: dict[str, Any]) -> dict[str, Any]:
    """
    验证 AgentRunRequest 数据格式
    
    Args:
        request_data: 请求数据
    
    Returns:
        dict: 验证结果
    """
    required_fields = [
        "agent_type",
        "org_id",
        "user_id",
        "node_id",
        "run_date",
        "input",
    ]
    
    missing_fields = [f for f in required_fields if f not in request_data]
    
    if missing_fields:
        return {
            "valid": False,
            "missing_fields": missing_fields,
            "error": f"缺少必需字段: {', '.join(missing_fields)}",
        }
    
    # 验证 input 字段
    input_data = request_data.get("input", {})
    if not isinstance(input_data, dict):
        return {
            "valid": False,
            "error": "'input' 必须是字典类型",
        }
    
    if "skill_name" not in input_data:
        return {
            "valid": False,
            "error": "'input.skill_name' 是必需的",
        }
    
    if "skill_args" not in input_data:
        return {
            "valid": False,
            "error": "'input.skill_args' 是必需的",
        }
    
    return {"valid": True}
