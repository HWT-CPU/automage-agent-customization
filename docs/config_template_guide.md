# 配置模板使用指南

本文档说明如何使用配置模板系统为新员工自动生成 Hermes、OpenClaw 和知识库配置。

## 📋 配置模板概览

### 现有模板文件

| 模板类型 | 文件路径 | 说明 |
|---------|---------|------|
| Hermes 配置 | `configs/hermes.example.toml` | Hermes Runtime 配置模板 |
| OpenClaw 配置 | `configs/openclaw.example.toml` | OpenClaw 集成配置模板 |
| 系统配置 | `configs/automage.example.toml` | 系统主配置（数据库、API、权限等） |
| 员工配置 | `examples/user.staff.example.toml` | 员工角色配置模板 |
| 经理配置 | `examples/user.manager.example.toml` | 经理角色配置模板 |
| 高管配置 | `examples/user.executive.example.toml` | 高管角色配置模板 |
| 知识库配置 | `configs/feishu_knowledge.example.toml` | 飞书知识库配置模板 |

## 🚀 快速开始

### 方式一：使用命令行工具（推荐）

```bash
# 为新员工生成配置
python scripts/onboard_new_user.py \
  --user-id user-002 \
  --display-name "李四" \
  --role staff \
  --department-id dept-sales \
  --job-title "销售专员" \
  --manager-node-id manager-node-001 \
  --feishu-open-id ou_abc123xyz
```

**参数说明：**

| 参数 | 必填 | 说明 | 示例 |
|-----|------|------|------|
| `--user-id` | ✅ | 用户唯一标识 | `user-002` |
| `--display-name` | ✅ | 用户显示名称 | `李四` |
| `--role` | ✅ | 角色类型 | `staff`、`manager`、`executive` |
| `--department-id` | ✅ | 部门 ID | `dept-sales` |
| `--job-title` | ✅ | 职位名称 | `销售专员` |
| `--org-id` | ❌ | 组织 ID | `org-001`（默认） |
| `--manager-node-id` | ❌ | 上级节点 ID | `manager-node-001` |
| `--feishu-open-id` | ❌ | 飞书 Open ID | `ou_abc123xyz` |
| `--output-dir` | ❌ | 输出目录 | `configs/users`（默认） |

**生成的文件结构：**

```
configs/users/user-002/
├── user.staff.toml          # 用户配置
├── hermes.toml              # Hermes 配置
├── openclaw.toml            # OpenClaw 配置
└── knowledge.toml           # 知识库配置

configs/
└── feishu_user_map.json     # 飞书用户映射（自动更新）
```

### 方式二：使用 Python API

```python
from automage_agents.config.template_generator import (
    ConfigTemplateGenerator,
    UserOnboardingConfig,
)

# 创建配置对象
config = UserOnboardingConfig(
    user_id="user-003",
    display_name="王五",
    role="manager",
    department_id="dept-engineering",
    job_title="工程部经理",
    org_id="org-001",
    manager_node_id="executive-node-001",
    feishu_open_id="ou_def456uvw",
)

# 生成所有配置
generator = ConfigTemplateGenerator()
results = generator.generate_all_configs(config, output_dir="configs/users")

# 查看生成的文件
for key, path in results.items():
    print(f"{key}: {path}")
```

## 📝 配置文件详解

### 1. 用户配置文件 (`user.{role}.toml`)

定义用户的基本信息、职责、权限等：

```toml
[user]
node_id = "staff-node-user-002"
user_id = "user-002"
role = "staff"
level = "l1_staff"
department_id = "dept-sales"
manager_node_id = "manager-node-001"
display_name = "李四"
job_title = "销售专员"
responsibilities = [
  "完成日常工作任务",
  "记录每日工作进展",
  "提交需要上级支持的问题"
]
input_sources = [
  "Manager Agent 下发的任务",
  "飞书日报卡片",
  "工作记录"
]
output_requirements = [
  "每日工作进度",
  "遇到的问题",
  "已尝试解决方案",
  "是否需要上级支持",
  "明日计划"
]
permission_notes = [
  "只能访问自己的任务与日报",
  "不能读取其他员工数据",
  "不能做部门级决策"
]
personalized_context = "李四 的个性化上下文，请根据实际情况填写。"

[user.metadata]
feishu_open_id = "ou_abc123xyz"
created_at = "2026-05-17T10:30:00"
created_by = "config_template_generator"
```

### 2. Hermes 配置文件 (`hermes.toml`)

定义 Hermes Runtime 的行为：

```toml
[hermes]
enabled = true
runtime_name = "automage-hermes-user-002"
mode = "local"
settings_path = "configs/automage.example.toml"
use_mock_api = false
skill_registry = "automage_agents.skills.registry.SKILL_REGISTRY"

[hermes.context]
org_id = "org-001"
run_date = ""
workflow_name = "automage_mvp_dag"
source_channel = "openclaw"

[hermes.agents.staff]
enabled = true
profile_path = "configs/users/user-002/user.staff.toml"
workflow_stage = "staff_daily_report"

[hermes.agents.manager]
enabled = false
profile_path = "examples/user.manager.example.toml"
workflow_stage = "manager_summary"

[hermes.agents.executive]
enabled = false
profile_path = "examples/user.executive.example.toml"
workflow_stage = "executive_decision"
```

### 3. OpenClaw 配置文件 (`openclaw.toml`)

定义 OpenClaw 集成的渠道和路由：

```toml
[openclaw]
enabled = true
runtime_name = "automage-openclaw-user-002"
default_channel = "cli"
reply_enabled = true

[openclaw.channels.cli]
enabled = true

[openclaw.channels.feishu]
enabled = true
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

[openclaw.commands.knowledge_query]
keywords = ["查知识库", "查询知识库", "知识库", "项目资料", "项目文档"]
```

### 4. 知识库配置文件 (`knowledge.toml`)

定义用户可访问的知识库节点：

```toml
[knowledge]
name = "李四 的知识库"
version = "1.0.0"
description = "staff 角色相关的业务知识、流程规范、技术文档"
owner_user_id = "user-002"
org_id = "org-001"
department_id = "dept-sales"

[[knowledge.sections]]
id = "project_overview"
topic = "项目概览"
node_token = "YOUR_FEISHU_DOC_TOKEN_HERE"
labels = ["项目", "概览"]

[[knowledge.sections]]
id = "business_glossary"
topic = "业务术语表"
node_token = "YOUR_FEISHU_DOC_TOKEN_HERE"
labels = ["术语", "词汇表"]

[[knowledge.sections]]
id = "staff_report_template"
topic = "Staff 日报模板"
node_token = "YOUR_FEISHU_DOC_TOKEN_HERE"
labels = ["日报", "模板", "staff"]
```

### 5. 飞书用户映射文件 (`feishu_user_map.json`)

维护飞书 Open ID 到系统 User ID 的映射：

```json
{
  "ou_staff_001": "user-001",
  "ou_abc123xyz": "user-002",
  "ou_def456uvw": "user-003"
}
```

## 🔧 高级用法

### 批量导入用户

创建用户列表文件 `users.json`：

```json
[
  {
    "user_id": "user-004",
    "display_name": "赵六",
    "role": "staff",
    "department_id": "dept-sales",
    "job_title": "销售专员",
    "manager_node_id": "manager-node-001",
    "feishu_open_id": "ou_ghi789rst"
  },
  {
    "user_id": "user-005",
    "display_name": "孙七",
    "role": "staff",
    "department_id": "dept-engineering",
    "job_title": "软件工程师",
    "manager_node_id": "manager-node-002",
    "feishu_open_id": "ou_jkl012mno"
  }
]
```

批量导入脚本：

```python
import json
from pathlib import Path
from automage_agents.config.template_generator import (
    ConfigTemplateGenerator,
    UserOnboardingConfig,
)

# 读取用户列表
with open("users.json", "r", encoding="utf-8") as f:
    users = json.load(f)

# 批量生成配置
generator = ConfigTemplateGenerator()
for user_data in users:
    config = UserOnboardingConfig(**user_data)
    results = generator.generate_all_configs(config)
    print(f"✅ 已为 {config.display_name} 生成配置")
```

### 自定义知识库节点

```python
from automage_agents.config.template_generator import (
    ConfigTemplateGenerator,
    UserOnboardingConfig,
)

# 自定义知识库节点
custom_knowledge_sections = [
    {
        "id": "sales_playbook",
        "topic": "销售手册",
        "node_token": "doccnXXXXXXXXXXXXXXXXXXXX",
        "labels": ["销售", "手册"],
    },
    {
        "id": "customer_cases",
        "topic": "客户案例库",
        "node_token": "doccnYYYYYYYYYYYYYYYYYYYY",
        "labels": ["客户", "案例"],
    },
]

config = UserOnboardingConfig(
    user_id="user-006",
    display_name="周八",
    role="staff",
    department_id="dept-sales",
    job_title="销售专员",
    knowledge_sections=custom_knowledge_sections,
)

generator = ConfigTemplateGenerator()
results = generator.generate_all_configs(config)
```

## 📚 配置模板加载器

系统提供了配置加载器来读取生成的配置：

```python
from automage_agents.integrations.hermes.config import load_hermes_config
from automage_agents.integrations.openclaw.config import load_openclaw_config

# 加载 Hermes 配置
hermes_config = load_hermes_config("configs/users/user-002/hermes.toml")
print(f"Runtime Name: {hermes_config.runtime_name}")
print(f"Org ID: {hermes_config.context.org_id}")

# 加载 OpenClaw 配置
openclaw_config = load_openclaw_config("configs/users/user-002/openclaw.toml")
print(f"Default Channel: {openclaw_config.default_channel}")
print(f"Feishu Enabled: {openclaw_config.feishu.enabled}")
```

## ✅ 验证配置

生成配置后，建议进行以下验证：

### 1. 配置文件语法检查

```bash
# 检查 TOML 语法
python -c "import toml; toml.load('configs/users/user-002/hermes.toml')"
```

### 2. 配置加载测试

```bash
# 运行配置加载测试
python -c "
from automage_agents.integrations.hermes.config import load_hermes_config
config = load_hermes_config('configs/users/user-002/hermes.toml')
print(f'✅ Hermes 配置加载成功: {config.runtime_name}')
"
```

### 3. 端到端测试

```bash
# 使用生成的配置运行测试
python scripts/check_real_hermes_skill_server.py \
  --hermes-config configs/users/user-002/hermes.toml
```

## 🔐 安全注意事项

1. **敏感信息保护**
   - 不要将包含真实飞书凭证的配置文件提交到版本控制
   - 使用 `.gitignore` 排除 `configs/users/*/` 目录
   - 生产环境使用环境变量或密钥管理器

2. **权限隔离**
   - 确保用户只能访问自己的配置文件
   - 定期审计用户权限配置
   - 使用 RBAC 机制控制 API 访问

3. **配置验证**
   - 生成配置后进行语法和逻辑验证
   - 测试环境先验证再部署到生产
   - 保留配置变更历史记录

## 🐛 常见问题

### Q1: 如何获取飞书文档 token？

A: 打开飞书文档，查看 URL：
```
https://example.feishu.cn/docx/doccnXXXXXXXXXXXXXXXXXXXX
                              ^^^^^^^^^^^^^^^^^^^^^^^^
                              这部分就是 node_token
```

### Q2: 如何更新现有用户的配置？

A: 重新运行生成脚本，系统会覆盖现有配置文件。建议先备份：

```bash
# 备份现有配置
cp -r configs/users/user-002 configs/users/user-002.backup

# 重新生成
python scripts/onboard_new_user.py --user-id user-002 ...
```

### Q3: 如何为用户添加自定义知识库节点？

A: 编辑用户的 `knowledge.toml` 文件，添加新的 `[[knowledge.sections]]` 块：

```toml
[[knowledge.sections]]
id = "custom_doc"
topic = "自定义文档"
node_token = "doccnZZZZZZZZZZZZZZZZZZZZ"
labels = ["自定义", "文档"]
```

### Q4: 如何禁用飞书集成？

A: 编辑 `openclaw.toml`，设置：

```toml
[openclaw.channels.feishu]
enabled = false
```

## 📖 相关文档

- [Hermes 集成指南](./openclaw_integration_guide.md)
- [OpenClaw 集成指南](./openclaw_integration_guide.md)
- [知识库配置指南](../references/feishu_knowledge_base.md)
- [API 文档](./swagger_test_flow_zh.md)

## 🤝 贡献

如需扩展配置模板功能，请修改：
- `automage_agents/config/template_generator.py` - 模板生成器
- `scripts/onboard_new_user.py` - 命令行工具
- 相关配置加载器（`hermes/config.py`、`openclaw/config.py`）
