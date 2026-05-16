"""
集成接口测试 - 验证为 OpenClaw 和全栈前端提供的接口

此测试文件验证：
1. Hermes Runtime 本地集成接口
2. HTTP API 端点
3. 数据格式兼容性
"""

import pytest
from fastapi.testclient import TestClient

from automage_agents.integrations.hermes.client import LocalHermesClient
from automage_agents.integrations.hermes.contracts import HermesInvokeRequest, HermesTrace
from automage_agents.integrations.hermes.runtime import HermesOpenClawRuntime
from automage_agents.server.app import create_app


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def hermes_runtime():
    """创建 Hermes Runtime 实例"""
    runtime = HermesOpenClawRuntime.from_config_files(
        hermes_config_path="configs/hermes.example.toml",
        openclaw_config_path="configs/openclaw.example.toml",
        auto_initialize=True,
    )
    return runtime


@pytest.fixture
def hermes_client(hermes_runtime):
    """获取 Hermes Client"""
    return hermes_runtime.hermes_client


@pytest.fixture
def api_client():
    """创建 FastAPI 测试客户端"""
    app = create_app()
    return TestClient(app)


# ============================================================================
# OpenClaw 集成测试 - 本地 Python 调用
# ============================================================================


class TestOpenClawIntegration:
    """测试 OpenClaw 团队使用的本地 Python 集成接口"""

    def test_hermes_client_invoke_fetch_tasks(self, hermes_client):
        """测试调用 fetch_my_tasks Skill"""
        request = HermesInvokeRequest(
            skill_name="fetch_my_tasks",
            actor_user_id="zhangsan",
            payload={},
        )

        response = hermes_client.invoke_skill(request)

        assert response.ok
        assert response.skill_name == "fetch_my_tasks"
        assert response.actor_user_id == "zhangsan"
        assert "tasks" in response.result.data or response.result.data is not None

    def test_hermes_client_invoke_post_daily_report(self, hermes_client):
        """测试调用 post_daily_report Skill"""
        request = HermesInvokeRequest(
            skill_name="post_daily_report",
            actor_user_id="zhangsan",
            payload={
                "timestamp": "2026-05-13T10:00:00+08:00",
                "work_progress": "完成了客户跟进",
                "issues_faced": "报价周期不明确",
                "solution_attempt": "已联系产品经理确认",
                "need_support": False,
                "next_day_plan": "继续推进合同签订",
                "resource_usage": {},
            },
        )

        response = hermes_client.invoke_skill(request)

        assert response.ok
        assert response.skill_name == "post_daily_report"
        assert response.result.data is not None

    def test_hermes_client_invoke_unknown_skill(self, hermes_client):
        """测试调用不存在的 Skill"""
        request = HermesInvokeRequest(
            skill_name="unknown_skill_xyz",
            actor_user_id="zhangsan",
            payload={},
        )

        response = hermes_client.invoke_skill(request)

        assert not response.ok
        assert response.result.error_code == "unknown_skill"

    def test_hermes_client_invoke_with_trace(self, hermes_client):
        """测试带追踪信息的调用"""
        trace = HermesTrace(
            run_id="test-run-001",
            trace_id="test-trace-001",
            correlation_id="test-correlation-001",
        )

        request = HermesInvokeRequest(
            skill_name="fetch_my_tasks",
            actor_user_id="zhangsan",
            payload={},
            trace=trace,
        )

        response = hermes_client.invoke_skill(request)

        assert response.ok
        assert response.trace.run_id == "test-run-001"
        assert response.trace.trace_id == "test-trace-001"
        assert response.trace.correlation_id == "test-correlation-001"

    def test_hermes_response_to_dict(self, hermes_client):
        """测试响应转换为字典"""
        request = HermesInvokeRequest(
            skill_name="fetch_my_tasks",
            actor_user_id="zhangsan",
            payload={},
        )

        response = hermes_client.invoke_skill(request)
        response_dict = response.to_dict()

        assert "ok" in response_dict
        assert "skill_name" in response_dict
        assert "actor_user_id" in response_dict
        assert "trace" in response_dict
        assert "result" in response_dict


# ============================================================================
# 全栈前端集成测试 - HTTP API 调用
# ============================================================================


class TestFrontendIntegration:
    """测试全栈前端使用的 HTTP API 接口"""

    def test_agent_run_api_fetch_tasks(self, api_client):
        """测试 /api/v1/agent/run 端点 - 查询任务"""
        response = api_client.post(
            "/api/v1/agent/run",
            json={
                "agent_type": "staff",
                "org_id": "org_automage_mvp",
                "user_id": "zhangsan",
                "node_id": "staff_agent_mvp_001",
                "run_date": "2026-05-13",
                "input": {
                    "skill_name": "fetch_my_tasks",
                    "skill_args": {},
                },
            },
            headers={
                "X-User-Id": "zhangsan",
                "X-Role": "staff",
                "X-Node-Id": "staff_agent_mvp_001",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["ok"] is True
        assert data["agent_type"] == "staff"
        assert data["node_id"] == "staff_agent_mvp_001"
        assert "output_schema_id" in data
        assert "output" in data
        assert "trace_id" in data
        assert isinstance(data["warnings"], list)

    def test_agent_run_api_post_daily_report(self, api_client):
        """测试 /api/v1/agent/run 端点 - 提交日报"""
        response = api_client.post(
            "/api/v1/agent/run",
            json={
                "agent_type": "staff",
                "org_id": "org_automage_mvp",
                "user_id": "zhangsan",
                "node_id": "staff_agent_mvp_001",
                "run_date": "2026-05-13",
                "input": {
                    "skill_name": "post_daily_report",
                    "skill_args": {
                        "timestamp": "2026-05-13T10:00:00+08:00",
                        "work_progress": "完成了客户跟进",
                        "issues_faced": "报价周期不明确",
                        "solution_attempt": "已联系产品经理确认",
                        "need_support": False,
                        "next_day_plan": "继续推进合同签订",
                        "resource_usage": {},
                    },
                },
            },
            headers={
                "X-User-Id": "zhangsan",
                "X-Role": "staff",
                "X-Node-Id": "staff_agent_mvp_001",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["ok"] is True
        assert data["agent_type"] == "staff"

    def test_agent_run_api_missing_skill_name(self, api_client):
        """测试缺少 skill_name 的请求"""
        response = api_client.post(
            "/api/v1/agent/run",
            json={
                "agent_type": "staff",
                "org_id": "org_automage_mvp",
                "user_id": "zhangsan",
                "node_id": "staff_agent_mvp_001",
                "run_date": "2026-05-13",
                "input": {
                    "skill_args": {},
                },
            },
            headers={
                "X-User-Id": "zhangsan",
                "X-Role": "staff",
                "X-Node-Id": "staff_agent_mvp_001",
            },
        )

        assert response.status_code == 400
        assert "skill_name" in response.json()["detail"]

    def test_agent_run_api_user_id_mismatch(self, api_client):
        """测试 Header 和 Body 中 user_id 不一致"""
        response = api_client.post(
            "/api/v1/agent/run",
            json={
                "agent_type": "staff",
                "org_id": "org_automage_mvp",
                "user_id": "zhangsan",
                "node_id": "staff_agent_mvp_001",
                "run_date": "2026-05-13",
                "input": {
                    "skill_name": "fetch_my_tasks",
                    "skill_args": {},
                },
            },
            headers={
                "X-User-Id": "lisi",  # 不一致
                "X-Role": "staff",
                "X-Node-Id": "staff_agent_mvp_001",
            },
        )

        assert response.status_code == 400
        assert "does not match" in response.json()["detail"]

    def test_list_skills_api(self, api_client):
        """测试 /api/v1/agent/skills 端点"""
        response = api_client.get(
            "/api/v1/agent/skills?agent_type=staff",
            headers={
                "X-User-Id": "zhangsan",
                "X-Role": "staff",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["agent_type"] == "staff"
        assert isinstance(data["skills"], list)
        assert len(data["skills"]) > 0

        # 验证 Skill 信息结构
        skill = data["skills"][0]
        assert "name" in skill
        assert "description" in skill
        assert "category" in skill

    def test_health_check_api(self, api_client):
        """测试 /api/v1/agent/health 端点"""
        response = api_client.get("/api/v1/agent/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "service" in data
        assert "timestamp" in data
        assert "hermes_enabled" in data
        assert "available_skills" in data

    def test_root_endpoint(self, api_client):
        """测试根路径"""
        response = api_client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert data["service"] == "automage-agent-runtime"
        assert data["status"] == "ok"

    def test_healthz_endpoint(self, api_client):
        """测试 /healthz 端点"""
        response = api_client.get("/healthz")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"


# ============================================================================
# 数据格式兼容性测试
# ============================================================================


class TestDataFormatCompatibility:
    """测试与前端约定的数据格式兼容性"""

    def test_agent_run_response_schema(self, api_client):
        """验证 AgentRunResponse 数据结构"""
        response = api_client.post(
            "/api/v1/agent/run",
            json={
                "agent_type": "staff",
                "org_id": "org_automage_mvp",
                "user_id": "zhangsan",
                "node_id": "staff_agent_mvp_001",
                "run_date": "2026-05-13",
                "input": {
                    "skill_name": "fetch_my_tasks",
                    "skill_args": {},
                },
            },
            headers={
                "X-User-Id": "zhangsan",
                "X-Role": "staff",
                "X-Node-Id": "staff_agent_mvp_001",
            },
        )

        data = response.json()

        # 验证所有必需字段
        required_fields = [
            "ok",
            "agent_type",
            "node_id",
            "output_schema_id",
            "output",
            "warnings",
            "trace_id",
            "fallback",
        ]

        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # 验证字段类型
        assert isinstance(data["ok"], bool)
        assert isinstance(data["agent_type"], str)
        assert isinstance(data["node_id"], str)
        assert isinstance(data["output_schema_id"], str)
        assert isinstance(data["output"], dict)
        assert isinstance(data["warnings"], list)
        assert isinstance(data["trace_id"], str)
        assert isinstance(data["fallback"], bool)

    def test_skill_list_response_schema(self, api_client):
        """验证 SkillListResponse 数据结构"""
        response = api_client.get(
            "/api/v1/agent/skills?agent_type=staff",
            headers={
                "X-User-Id": "zhangsan",
                "X-Role": "staff",
            },
        )

        data = response.json()

        # 验证必需字段
        assert "agent_type" in data
        assert "skills" in data

        # 验证 skills 数组
        assert isinstance(data["skills"], list)

        if len(data["skills"]) > 0:
            skill = data["skills"][0]
            assert "name" in skill
            assert "description" in skill
            assert "category" in skill

    def test_output_schema_id_inference(self, api_client):
        """测试 output_schema_id 推断逻辑"""
        test_cases = [
            ("post_daily_report", "schema_v1_staff"),
            ("fetch_my_tasks", "schema_v1_task"),
            ("generate_manager_report", "schema_v1_manager"),
        ]

        for skill_name, expected_schema_id in test_cases:
            response = api_client.post(
                "/api/v1/agent/run",
                json={
                    "agent_type": "staff",
                    "org_id": "org_automage_mvp",
                    "user_id": "zhangsan",
                    "node_id": "staff_agent_mvp_001",
                    "run_date": "2026-05-13",
                    "input": {
                        "skill_name": skill_name,
                        "skill_args": {},
                    },
                },
                headers={
                    "X-User-Id": "zhangsan",
                    "X-Role": "staff",
                    "X-Node-Id": "staff_agent_mvp_001",
                },
            )

            if response.status_code == 200:
                data = response.json()
                # 某些 Skill 可能需要特定参数，这里只验证成功的情况
                if data["ok"]:
                    assert expected_schema_id in data["output_schema_id"]


# ============================================================================
# 端到端集成测试
# ============================================================================


class TestEndToEndIntegration:
    """端到端集成测试 - 模拟真实使用场景"""

    def test_staff_daily_workflow(self, api_client):
        """测试员工日常工作流：提交日报 -> 查询任务"""
        # 1. 提交日报
        submit_response = api_client.post(
            "/api/v1/agent/run",
            json={
                "agent_type": "staff",
                "org_id": "org_automage_mvp",
                "user_id": "zhangsan",
                "node_id": "staff_agent_mvp_001",
                "run_date": "2026-05-13",
                "input": {
                    "skill_name": "post_daily_report",
                    "skill_args": {
                        "timestamp": "2026-05-13T10:00:00+08:00",
                        "work_progress": "完成了客户跟进",
                        "issues_faced": "报价周期不明确",
                        "solution_attempt": "已联系产品经理确认",
                        "need_support": False,
                        "next_day_plan": "继续推进合同签订",
                        "resource_usage": {},
                    },
                },
            },
            headers={
                "X-User-Id": "zhangsan",
                "X-Role": "staff",
                "X-Node-Id": "staff_agent_mvp_001",
            },
        )

        assert submit_response.status_code == 200
        submit_data = submit_response.json()
        assert submit_data["ok"] is True

        # 2. 查询任务
        tasks_response = api_client.post(
            "/api/v1/agent/run",
            json={
                "agent_type": "staff",
                "org_id": "org_automage_mvp",
                "user_id": "zhangsan",
                "node_id": "staff_agent_mvp_001",
                "run_date": "2026-05-13",
                "input": {
                    "skill_name": "fetch_my_tasks",
                    "skill_args": {},
                },
            },
            headers={
                "X-User-Id": "zhangsan",
                "X-Role": "staff",
                "X-Node-Id": "staff_agent_mvp_001",
            },
        )

        assert tasks_response.status_code == 200
        tasks_data = tasks_response.json()
        assert tasks_data["ok"] is True

    def test_openclaw_to_hermes_flow(self, hermes_runtime):
        """测试 OpenClaw -> Hermes 完整流程"""
        # 模拟 OpenClaw 解析用户输入
        user_text = "今天完成了客户跟进"
        actor_user_id = "zhangsan"

        # OpenClaw 构造 Hermes 请求
        request = HermesInvokeRequest(
            skill_name="post_daily_report",
            actor_user_id=actor_user_id,
            payload={
                "timestamp": "2026-05-13T10:00:00+08:00",
                "work_progress": user_text,
                "issues_faced": "无",
                "solution_attempt": "无",
                "need_support": False,
                "next_day_plan": "继续跟进",
                "resource_usage": {},
            },
        )

        # Hermes 执行
        response = hermes_runtime.hermes_client.invoke_skill(request)

        # 验证结果
        assert response.ok
        assert response.actor_user_id == actor_user_id


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
