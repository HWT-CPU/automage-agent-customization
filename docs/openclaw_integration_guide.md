# OpenClaw 集成指南

本文档说明 OpenClaw 团队如何集成和使用客制化团队提供的 Hermes Runtime 和 Skills。

## 概述

客制化团队提供了完整的 Hermes Runtime 实现，OpenClaw 团队可以通过以下方式集成：

1. **本地集成**：直接导入 Python 模块，调用 `LocalHermesClient`
2. **HTTP 集成**：通过 HTTP API 调用 Agent Runtime 服务

## 方式一：本地 Python 集成（推荐）

### 1. 导入依赖

```python
from automage_agents.integrations.hermes.client import LocalHermesClient
from automage_agents.integrations.hermes.contracts import HermesInvokeRequest, HermesTrace
from automage_agents.integrations.hermes.runtime import HermesOpenClawRuntime
```

### 2. 初始化 Runtime

```python
# 从配置文件初始化
runtime = HermesOpenClawRuntime.from_config_files(
    hermes_config_path="configs/hermes.example.toml",
    openclaw_config_path="configs/openclaw.example.toml",
    auto_initialize=True,
)

# 获取 Hermes Client
hermes_client = runtime.hermes_client
```

### 3. 调用 Skill

```python
# 构造请求
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

# 调用 Hermes
response = hermes_client.invoke_skill(request)

# 处理响应
if response.ok:
    print(f"✅ Skill 执行成功: {response.result.data}")
else:
    print(f"❌ Skill 执行失败: {response.result.message}")
    print(f"   错误码: {response.result.error_code}")
```

### 4. 完整示例：OpenClaw 命令解析与 Hermes 调用

```python
from automage_agents.integrations.openclaw.parser import OpenClawCommandParser, ParsedOpenClawCommand
from automage_agents.integrations.openclaw.config import load_openclaw_config
from automage_agents.integrations.hermes.client import LocalHermesClient
from automage_agents.integrations.hermes.contracts import HermesInvokeRequest

# 初始化
openclaw_config = load_openclaw_config("configs/openclaw.example.toml")
parser = OpenClawCommandParser(openclaw_config)
runtime = HermesOpenClawRuntime.from_config_files()
hermes_client = runtime.hermes_client

# 解析用户输入
user_text = "今天完成了客户跟进，遇到的问题是报价周期不明确，明天继续推进。"
parsed = parser.parse(user_text, actor_user_id="zhangsan", source_channel="cli")

# 根据解析结果调用对应 Skill
if parsed.command_type == "daily_report_submit":
    request = HermesInvokeRequest(
        skill_name="post_daily_report",
        actor_user_id=parsed.actor_user_id,
        payload=parsed.extracted_payload,
    )
    response = hermes_client.invoke_skill(request)
    print(response.to_dict())
```

## 方式二：HTTP API 集成

### 1. 启动 Agent Runtime 服务

```bash
cd 客制化
python -m automage_agents.server.app
```

服务将在 `http://localhost:8000` 启动。

### 2. 调用 HTTP API

#### 2.1 运行 Skill

```bash
curl -X POST http://localhost:8000/api/v1/agent/run \
  -H "Content-Type: application/json" \
  -H "X-User-Id: zhangsan" \
  -H "X-Role: staff" \
  -H "X-Node-Id: staff_agent_mvp_001" \
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

#### 2.2 查询可用 Skills

```bash
curl -X GET "http://localhost:8000/api/v1/agent/skills?agent_type=staff" \
  -H "X-User-Id: zhangsan" \
  -H "X-Role: staff"
```

#### 2.3 健康检查

```bash
curl -X GET http://localhost:8000/api/v1/agent/health
```

## 可用的 Skills

### Staff Skills

| Skill 名称 | 描述 | 参数 |
|-----------|------|------|
| `post_daily_report` | 提交员工日报 | `timestamp`, `work_progress`, `issues_faced`, `solution_attempt`, `need_support`, `next_day_plan`, `resource_usage` |
| `fetch_my_tasks` | 查询我的任务 | `status` (可选) |
| `update_my_task` | 更新任务状态 | `task_id`, `status`, `title`, `description`, `task_payload` |
| `import_staff_daily_report_from_markdown` | 从 Markdown 导入日报 | `markdown_text` |
| `read_staff_daily_report` | 读取员工日报 | `record_date`, `user_id` |
| `search_feishu_knowledge` | 搜索飞书知识库 | `query` |

### Manager Skills

| Skill 名称 | 描述 | 参数 |
|-----------|------|------|
| `analyze_team_reports` | 分析团队日报 | `department_id`, `record_date` |
| `generate_manager_report` | 生成经理汇总 | `dept_id`, `overall_health`, `aggregated_summary`, `top_3_risks`, `workforce_efficiency`, `pending_approvals` |
| `generate_manager_schema` | 生成经理 Schema | `dept_id`, `summary_date` |
| `delegate_task` | 分配任务 | `assignee_user_id`, `task_title`, `task_description`, `priority` |
| `search_feishu_knowledge` | 搜索飞书知识库 | `query` |

### Executive Skills

| Skill 名称 | 描述 | 参数 |
|-----------|------|------|
| `dream_decision_engine` | 生成 A/B 决策方案 | `summary_id` |
| `commit_decision` | 提交高层决策 | `summary_id`, `selected_option_id`, `task_candidates` |
| `broadcast_strategy` | 广播战略决策 | `decision_id`, `target_departments` |
| `search_feishu_knowledge` | 搜索飞书知识库 | `query` |

## 配置文件

### Hermes 配置 (`configs/hermes.example.toml`)

```toml
[hermes]
enabled = true
runtime_name = "automage-hermes-local"
mode = "local"
settings_path = "configs/automage.example.toml"
use_mock_api = true
skill_registry = "automage_agents.skills.registry.SKILL_REGISTRY"

[hermes.context]
org_id = "org-001"
run_date = ""
workflow_name = "automage_mvp_dag"
source_channel = "mock"

[hermes.agents.staff]
enabled = true
profile_path = "examples/user.staff.example.toml"
workflow_stage = "staff_daily_report"

[hermes.agents.manager]
enabled = true
profile_path = "examples/user.manager.example.toml"
workflow_stage = "manager_summary"

[hermes.agents.executive]
enabled = true
profile_path = "examples/user.executive.example.toml"
workflow_stage = "executive_decision"
```

### OpenClaw 配置 (`configs/openclaw.example.toml`)

```toml
[openclaw]
enabled = true
runtime_name = "automage-openclaw-local"
default_channel = "cli"
reply_enabled = true

[openclaw.channels.cli]
enabled = true

[openclaw.channels.feishu]
enabled = false
event_mode = "websocket"
reply_enabled = true

[openclaw.routing]
default_daily_report = "daily_report_submit"
default_task_query = "task_query"
default_knowledge_query = "knowledge_query"
default_manager_feedback = "manager_feedback"
default_executive_decision = "executive_decision"
default_markdown_import = "daily_report_markdown_import"

[openclaw.commands.daily_report]
keywords = ["今天完成", "今日完成", "完成了", "日报", "工作进展"]

[openclaw.commands.task_query]
keywords = ["查任务", "查询任务", "我的任务", "任务列表"]

[openclaw.commands.executive_decision]
keywords = ["决策A", "决策 A", "选择A", "选择 A", "方案A", "方案 A", "决策B", "决策 B", "选择B", "选择 B", "方案B", "方案 B"]
```

## 数据结构

### HermesInvokeRequest

```python
@dataclass
class HermesInvokeRequest:
    skill_name: str              # Skill 名称
    actor_user_id: str           # 执行用户 ID
    payload: dict[str, Any]      # Skill 参数
    trace: HermesTrace           # 追踪信息
```

### HermesInvokeResponse

```python
@dataclass
class HermesInvokeResponse:
    ok: bool                     # 执行是否成功
    skill_name: str              # Skill 名称
    actor_user_id: str           # 执行用户 ID
    result: SkillResult          # 执行结果
    trace: HermesTrace           # 追踪信息
```

### SkillResult

```python
@dataclass
class SkillResult:
    ok: bool                     # 执行是否成功
    data: dict[str, Any]         # 返回数据
    message: str                 # 消息
    error_code: str | None       # 错误码
```

## 错误处理

### 常见错误码

| 错误码 | 描述 | 处理建议 |
|--------|------|---------|
| `unknown_skill` | Skill 不存在 | 检查 Skill 名称是否正确 |
| `skill_signature_mismatch` | Skill 参数不匹配 | 检查 payload 参数是否完整 |
| `skill_invocation_failed` | Skill 执行失败 | 查看 message 字段获取详细错误信息 |
| `auth_failed` | 认证失败 | 检查用户身份和权限 |
| `permission_denied` | 权限不足 | 确认用户角色是否有权限执行该 Skill |

### 错误处理示例

```python
response = hermes_client.invoke_skill(request)

if not response.ok:
    error_code = response.result.error_code
    
    if error_code == "unknown_skill":
        print(f"Skill 不存在: {request.skill_name}")
        # 提示用户可用的 Skills
    
    elif error_code == "skill_signature_mismatch":
        print(f"参数不匹配: {response.result.message}")
        # 检查并修正参数
    
    elif error_code == "permission_denied":
        print(f"权限不足: {response.result.message}")
        # 提示用户权限问题
    
    else:
        print(f"执行失败: {response.result.message}")
        # 记录日志并通知管理员
```

## 测试

### 单元测试

```python
import pytest
from automage_agents.integrations.hermes.client import LocalHermesClient
from automage_agents.integrations.hermes.contracts import HermesInvokeRequest

def test_hermes_invoke_fetch_tasks():
    runtime = HermesOpenClawRuntime.from_config_files()
    hermes_client = runtime.hermes_client
    
    request = HermesInvokeRequest(
        skill_name="fetch_my_tasks",
        actor_user_id="zhangsan",
        payload={},
    )
    
    response = hermes_client.invoke_skill(request)
    
    assert response.ok
    assert "tasks" in response.result.data
```

### 集成测试

```bash
# 启动服务
python -m automage_agents.server.app &

# 运行测试
pytest 客制化/tests/test_openclaw_hermes_integration.py
```

## 联系方式

如有问题，请联系客制化团队：

- 技术负责人：[姓名]
- 邮箱：[邮箱]
- 文档仓库：`客制化/docs/`

## 更新日志

- **2026-05-13**: 初始版本，提供 Hermes Runtime 和 Skills 集成接口
