"""
Agent Runtime API - 为全栈前端和 OpenClaw 提供统一的 Agent 调用接口

此模块提供 HTTP API 端点，允许外部系统调用客制化的 Hermes Runtime 和 Skills。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from automage_agents.core.enums import AgentRole
from automage_agents.integrations.hermes.client import LocalHermesClient
from automage_agents.integrations.hermes.contracts import HermesInvokeRequest, HermesTrace
from automage_agents.skills.registry import SKILL_REGISTRY


router = APIRouter(prefix="/api/v1/agent", tags=["agent-runtime"])


# ============================================================================
# Request/Response Models (与全栈前端约定的接口)
# ============================================================================


class AgentRunRequest(BaseModel):
    """Agent 运行请求 - 与全栈前端 AgentRunRequest 接口对齐"""

    agent_type: str = Field(..., description="Agent 类型: staff, manager, executive")
    org_id: str = Field(..., description="组织 ID")
    department_id: str | None = Field(None, description="部门 ID")
    user_id: str = Field(..., description="用户 ID")
    node_id: str = Field(..., description="节点 ID")
    run_date: str = Field(..., description="运行日期 YYYY-MM-DD")
    input: dict[str, Any] = Field(..., description="输入数据，包含 skill_name 和 skill_args")
    context: dict[str, Any] | None = Field(None, description="额外上下文")


class AgentRunResponse(BaseModel):
    """Agent 运行响应 - 与全栈前端 AgentRunResponse 接口对齐"""

    ok: bool = Field(..., description="执行是否成功")
    agent_type: str = Field(..., description="Agent 类型")
    node_id: str = Field(..., description="节点 ID")
    output_schema_id: str = Field(..., description="输出 Schema ID")
    output: dict[str, Any] = Field(..., description="输出数据")
    warnings: list[str] = Field(default_factory=list, description="警告信息")
    trace_id: str = Field(..., description="追踪 ID")
    fallback: bool = Field(False, description="是否使用了降级逻辑")


class SkillListResponse(BaseModel):
    """Skill 列表响应"""

    agent_type: str
    skills: list[SkillInfo]


class SkillInfo(BaseModel):
    """Skill 信息"""

    name: str
    description: str
    category: str


class HealthCheckResponse(BaseModel):
    """健康检查响应"""

    status: str
    service: str
    timestamp: str
    hermes_enabled: bool
    available_skills: int


# ============================================================================
# Global State (由 FastAPI 应用初始化时注入)
# ============================================================================


@dataclass
class AgentRuntimeState:
    """Agent Runtime 全局状态"""

    hermes_client: LocalHermesClient | None = None


_runtime_state = AgentRuntimeState()


def initialize_agent_runtime(hermes_client: LocalHermesClient) -> None:
    """
    初始化 Agent Runtime 状态
    
    此函数应在 FastAPI 应用启动时调用，注入 LocalHermesClient 实例。
    
    Args:
        hermes_client: Hermes 客户端实例
    """
    _runtime_state.hermes_client = hermes_client


# ============================================================================
# API Endpoints
# ============================================================================


@router.post("/run", response_model=AgentRunResponse)
async def run_agent(
    request: AgentRunRequest,
    x_user_id: str = Header(..., alias="X-User-Id"),
    x_role: str = Header(..., alias="X-Role"),
    x_node_id: str = Header(..., alias="X-Node-Id"),
) -> AgentRunResponse:
    """
    运行 Agent Skill
    
    此端点接收前端的 Agent 运行请求，转发给 Hermes Runtime 执行对应的 Skill。
    
    **使用示例**:
    ```bash
    curl -X POST http://localhost:8000/api/v1/agent/run \\
      -H "Content-Type: application/json" \\
      -H "X-User-Id: zhangsan" \\
      -H "X-Role: staff" \\
      -H "X-Node-Id: staff_agent_mvp_001" \\
      -d '{
        "agent_type": "staff",
        "org_id": "org_automage_mvp",
        "user_id": "zhangsan",
        "node_id": "staff_agent_mvp_001",
        "run_date": "2026-05-13",
        "input": {
          "skill_name": "fetch_my_tasks",
          "skill_args": {}
        }
      }'
    ```
    
    Args:
        request: Agent 运行请求
        x_user_id: 请求用户 ID (Header)
        x_role: 请求用户角色 (Header)
        x_node_id: 请求节点 ID (Header)
    
    Returns:
        AgentRunResponse: Agent 运行结果
    
    Raises:
        HTTPException: 当 Hermes Runtime 未初始化或请求参数无效时
    """
    if _runtime_state.hermes_client is None:
        raise HTTPException(
            status_code=503,
            detail="Agent Runtime not initialized. Hermes client is not available.",
        )

    # 验证 Header 与 Body 一致性
    if x_user_id != request.user_id:
        raise HTTPException(
            status_code=400,
            detail=f"X-User-Id header ({x_user_id}) does not match request.user_id ({request.user_id})",
        )

    # 提取 skill_name 和 skill_args
    skill_name = request.input.get("skill_name")
    if not skill_name:
        raise HTTPException(
            status_code=400,
            detail="Missing 'skill_name' in request.input",
        )

    skill_args = request.input.get("skill_args", {})
    if not isinstance(skill_args, dict):
        raise HTTPException(
            status_code=400,
            detail="'skill_args' must be a dictionary",
        )

    # 构造 Hermes 请求
    trace = HermesTrace(
        run_id=f"agent-run-{uuid4()}",
        trace_id=f"trace-{uuid4()}",
        correlation_id=request.context.get("correlation_id") if request.context else None,
    )

    hermes_request = HermesInvokeRequest(
        skill_name=skill_name,
        actor_user_id=request.user_id,
        payload=skill_args,
        trace=trace,
    )

    # 调用 Hermes Runtime
    hermes_response = _runtime_state.hermes_client.invoke_skill(hermes_request)

    # 推断 output_schema_id
    output_schema_id = _infer_output_schema_id(request.agent_type, skill_name, hermes_response.result.data)

    # 构造响应
    return AgentRunResponse(
        ok=hermes_response.ok,
        agent_type=request.agent_type,
        node_id=request.node_id,
        output_schema_id=output_schema_id,
        output=hermes_response.result.data or {},
        warnings=[hermes_response.result.message] if not hermes_response.ok else [],
        trace_id=hermes_response.trace.trace_id,
        fallback=False,
    )


@router.get("/skills", response_model=SkillListResponse)
async def list_skills(
    agent_type: str,
    x_user_id: str = Header(..., alias="X-User-Id"),
    x_role: str = Header(..., alias="X-Role"),
) -> SkillListResponse:
    """
    列出指定 Agent 类型可用的 Skills
    
    **使用示例**:
    ```bash
    curl -X GET "http://localhost:8000/api/v1/agent/skills?agent_type=staff" \\
      -H "X-User-Id: zhangsan" \\
      -H "X-Role: staff"
    ```
    
    Args:
        agent_type: Agent 类型 (staff, manager, executive)
        x_user_id: 请求用户 ID (Header)
        x_role: 请求用户角色 (Header)
    
    Returns:
        SkillListResponse: Skill 列表
    """
    skills = _get_skills_by_agent_type(agent_type)
    return SkillListResponse(agent_type=agent_type, skills=skills)


@router.post("/batch-run", response_model=list[AgentRunResponse])
async def batch_run_agents(
    requests: list[AgentRunRequest],
    x_user_id: str = Header(..., alias="X-User-Id"),
    x_role: str = Header(..., alias="X-Role"),
    x_node_id: str = Header(..., alias="X-Node-Id"),
) -> list[AgentRunResponse]:
    """
    批量运行 Agent Skills
    
    此端点接收多个 Agent 运行请求，并发执行以提升性能。
    
    **使用示例**:
    ```bash
    curl -X POST http://localhost:8000/api/v1/agent/batch-run \\
      -H "Content-Type: application/json" \\
      -H "X-User-Id: zhangsan" \\
      -H "X-Role: staff" \\
      -H "X-Node-Id: staff_agent_mvp_001" \\
      -d '[
        {
          "agent_type": "staff",
          "org_id": "org_automage_mvp",
          "user_id": "zhangsan",
          "node_id": "staff_agent_mvp_001",
          "run_date": "2026-05-13",
          "input": {"skill_name": "fetch_my_tasks", "skill_args": {}}
        },
        {
          "agent_type": "staff",
          "org_id": "org_automage_mvp",
          "user_id": "zhangsan",
          "node_id": "staff_agent_mvp_001",
          "run_date": "2026-05-13",
          "input": {"skill_name": "read_staff_daily_report", "skill_args": {"record_date": "2026-05-13"}}
        }
      ]'
    ```
    
    Args:
        requests: Agent 运行请求列表
        x_user_id: 请求用户 ID (Header)
        x_role: 请求用户角色 (Header)
        x_node_id: 请求节点 ID (Header)
    
    Returns:
        list[AgentRunResponse]: Agent 运行结果列表
    
    Raises:
        HTTPException: 当请求参数无效时
    """
    if not requests:
        raise HTTPException(status_code=400, detail="Request list cannot be empty")

    if len(requests) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 requests per batch")

    # 并发执行所有请求
    responses = []
    for request in requests:
        try:
            response = await run_agent(request, x_user_id, x_role, x_node_id)
            responses.append(response)
        except HTTPException as exc:
            # 单个请求失败不影响其他请求
            responses.append(
                AgentRunResponse(
                    ok=False,
                    agent_type=request.agent_type,
                    node_id=request.node_id,
                    output_schema_id=f"schema_v1_{request.agent_type}",
                    output={},
                    warnings=[f"HTTP {exc.status_code}: {exc.detail}"],
                    trace_id=f"error-{uuid4()}",
                    fallback=False,
                )
            )

    return responses


@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Agent Runtime 健康检查
    
    **使用示例**:
    ```bash
    curl -X GET http://localhost:8000/api/v1/agent/health
    ```
    
    Returns:
        HealthCheckResponse: 健康状态
    """
    return HealthCheckResponse(
        status="ok" if _runtime_state.hermes_client is not None else "degraded",
        service="automage-agent-runtime",
        timestamp=datetime.now().astimezone().isoformat(),
        hermes_enabled=_runtime_state.hermes_client is not None,
        available_skills=len(SKILL_REGISTRY),
    )


@router.get("/health/detailed")
async def detailed_health_check():
    """
    详细健康检查
    
    返回各组件的详细健康状态和性能指标。
    
    **使用示例**:
    ```bash
    curl -X GET http://localhost:8000/api/v1/agent/health/detailed
    ```
    
    Returns:
        dict: 详细健康状态
    """
    from automage_agents.integrations.hermes.cached_client import CachedHermesClient

    # 基础状态
    health_status = {
        "status": "ok",
        "timestamp": datetime.now().astimezone().isoformat(),
        "service": "automage-agent-runtime",
        "version": "1.0.0",
    }

    # 组件健康状态
    components = {}

    # Hermes Runtime
    if _runtime_state.hermes_client is not None:
        components["hermes_runtime"] = {
            "status": "ok",
            "type": _runtime_state.hermes_client.__class__.__name__,
        }

        # 如果使用缓存客户端，添加缓存统计
        if isinstance(_runtime_state.hermes_client, CachedHermesClient):
            stats = _runtime_state.hermes_client.get_stats()
            components["hermes_runtime"]["cache_stats"] = stats
    else:
        components["hermes_runtime"] = {
            "status": "unavailable",
            "message": "Hermes client not initialized",
        }

    # Skills
    components["skills"] = {
        "status": "ok",
        "total_skills": len(SKILL_REGISTRY),
        "available_skills": list(SKILL_REGISTRY.keys()),
    }

    # 数据库连接池（如果可用）
    try:
        from automage_agents.db.pool import get_database_pool
        from automage_agents.config.loader import load_runtime_settings

        settings = load_runtime_settings()
        pool = get_database_pool(settings)
        pool_status = pool.get_pool_status()

        components["database"] = {
            "status": "ok" if "error" not in pool_status else "degraded",
            "pool_status": pool_status,
        }
    except Exception as exc:
        components["database"] = {
            "status": "unknown",
            "message": str(exc),
        }

    # Redis 缓存（如果可用）
    try:
        from automage_agents.api.redis_cache import get_redis_skill_cache
        from automage_agents.config.loader import load_runtime_settings

        settings = load_runtime_settings()
        if settings.redis_url:
            redis_cache = get_redis_skill_cache(settings.redis_url)
            components["redis"] = {
                "status": "ok" if redis_cache.is_available() else "unavailable",
                "available": redis_cache.is_available(),
            }
        else:
            components["redis"] = {
                "status": "disabled",
                "message": "Redis not configured",
            }
    except Exception as exc:
        components["redis"] = {
            "status": "unknown",
            "message": str(exc),
        }

    health_status["components"] = components

    # 性能指标
    metrics = {
        "total_skills": len(SKILL_REGISTRY),
    }

    # 如果有缓存统计，添加到指标
    if isinstance(_runtime_state.hermes_client, CachedHermesClient):
        stats = _runtime_state.hermes_client.get_stats()
        metrics.update(
            {
                "total_requests": stats["total_requests"],
                "cache_hit_rate": f"{stats['cache_hit_rate']:.2%}",
                "avg_response_time_ms": f"{stats['avg_duration_ms']:.2f}",
            }
        )

    health_status["metrics"] = metrics

    # 判断整体状态
    component_statuses = [comp.get("status") for comp in components.values()]
    if "unavailable" in component_statuses:
        health_status["status"] = "degraded"
    elif all(status == "ok" for status in component_statuses if status != "disabled"):
        health_status["status"] = "ok"
    else:
        health_status["status"] = "degraded"

    return health_status


@router.get("/stats/cache")
async def get_cache_stats():
    """
    获取缓存统计信息
    
    **使用示例**:
    ```bash
    curl -X GET http://localhost:8000/api/v1/agent/stats/cache
    ```
    
    Returns:
        dict: 缓存统计信息
    """
    from automage_agents.integrations.hermes.cached_client import CachedHermesClient

    if isinstance(_runtime_state.hermes_client, CachedHermesClient):
        return _runtime_state.hermes_client.get_stats()

    return {"error": "Cache not enabled or not using CachedHermesClient"}


@router.get("/stats/pool")
async def get_pool_stats():
    """
    获取数据库连接池统计信息
    
    **使用示例**:
    ```bash
    curl -X GET http://localhost:8000/api/v1/agent/stats/pool
    ```
    
    Returns:
        dict: 连接池统计信息
    """
    try:
        from automage_agents.db.pool import get_database_pool
        from automage_agents.config.loader import load_runtime_settings

        settings = load_runtime_settings()
        pool = get_database_pool(settings)
        return pool.get_pool_status()
    except Exception as exc:
        return {"error": str(exc)}


# ============================================================================
# Helper Functions
# ============================================================================


def _infer_output_schema_id(agent_type: str, skill_name: str, output_data: Any) -> str:
    """
    推断输出 Schema ID
    
    Args:
        agent_type: Agent 类型
        skill_name: Skill 名称
        output_data: 输出数据
    
    Returns:
        str: Schema ID
    """
    # 根据 skill_name 推断 schema_id
    if skill_name in {"post_daily_report", "read_staff_daily_report", "import_staff_daily_report_from_markdown"}:
        return "schema_v1_staff"
    if skill_name in {"generate_manager_report", "analyze_team_reports"}:
        return "schema_v1_manager"
    if skill_name in {"dream_decision_engine", "commit_decision"}:
        return "schema_v1_executive"
    if skill_name in {"fetch_my_tasks", "update_my_task"}:
        return "schema_v1_task"

    # 从输出数据中提取 schema_id
    if isinstance(output_data, dict):
        if "schema_id" in output_data:
            return output_data["schema_id"]
        if "report" in output_data and isinstance(output_data["report"], dict):
            return output_data["report"].get("schema_id", f"schema_v1_{agent_type}")

    # 默认根据 agent_type 返回
    return f"schema_v1_{agent_type}"


def _get_skills_by_agent_type(agent_type: str) -> list[SkillInfo]:
    """
    根据 Agent 类型获取可用的 Skills
    
    Args:
        agent_type: Agent 类型
    
    Returns:
        list[SkillInfo]: Skill 信息列表
    """
    skill_categories = {
        "staff": [
            SkillInfo(name="post_daily_report", description="提交员工日报", category="staff"),
            SkillInfo(name="fetch_my_tasks", description="查询我的任务", category="staff"),
            SkillInfo(name="update_my_task", description="更新任务状态", category="staff"),
            SkillInfo(name="import_staff_daily_report_from_markdown", description="从 Markdown 导入日报", category="staff"),
            SkillInfo(name="read_staff_daily_report", description="读取员工日报", category="staff"),
            SkillInfo(name="search_feishu_knowledge", description="搜索飞书知识库", category="common"),
        ],
        "manager": [
            SkillInfo(name="analyze_team_reports", description="分析团队日报", category="manager"),
            SkillInfo(name="generate_manager_report", description="生成经理汇总", category="manager"),
            SkillInfo(name="generate_manager_schema", description="生成经理 Schema", category="manager"),
            SkillInfo(name="delegate_task", description="分配任务", category="manager"),
            SkillInfo(name="search_feishu_knowledge", description="搜索飞书知识库", category="common"),
        ],
        "executive": [
            SkillInfo(name="dream_decision_engine", description="生成 A/B 决策方案", category="executive"),
            SkillInfo(name="commit_decision", description="提交高层决策", category="executive"),
            SkillInfo(name="broadcast_strategy", description="广播战略决策", category="executive"),
            SkillInfo(name="search_feishu_knowledge", description="搜索飞书知识库", category="common"),
        ],
    }

    return skill_categories.get(agent_type, [])
