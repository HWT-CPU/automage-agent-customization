# AutoMage-2 Agent 初版工程

本目录当前提供面向后续 Hermes / OpenClaw 深度集成的 Agent 初版骨架。

## 当前已包含

- `automage_agents/core/`：Agent 枚举、共享数据模型、异常类型。
- `automage_agents/config/`：运行配置与 `user` 配置加载。
- `automage_agents/api/`：统一后端 API Client、响应模型、传输错误处理。
- `automage_agents/agents/`：三级 Agent 模板注册表与 `agents.md` 渲染器。
- `automage_agents/schemas/`：Staff / Manager / Dream Schema 草案。
- `automage_agents/integrations/`：OpenClaw / Feishu 适配层占位。
- `automage_agents/skills/`：Staff / Manager / Executive Skill 初版封装与本地 Skill registry。
- `automage_agents/templates/user.md`：岗位级 Agent 的 `user.md` 模板。
- `automage_agents/templates/*/agents.md`：base、line_worker、manager、executive 四类 Agent 模板草案。
- `configs/automage.example.toml`：本地运行配置示例。
- `examples/user.staff.example.toml`：可被加载器读取的员工配置示例。

## Docker 部署

本项目支持两种 Docker 启动方式：

### 1. 本地自部署

适合团队成员在自己电脑上直接测试和启动，默认会一起拉起 Postgres 容器。

```powershell
copy .env.example .env
docker compose up -d --build
```

启动后访问：

- Swagger：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/healthz`

### 2. 远程数据库 / 生产模式

适合连接公司已有远程数据库，不启用本地 Postgres 容器。

```powershell
copy .env.example .env
docker compose -f docker-compose.yml up -d --build
```

### 3. 配置切换规则

- 本地模式：使用 `docker-compose.override.yml`，自动切到 `configs/automage.docker.toml`
- 远程模式：只使用 `docker-compose.yml`，默认读取 `configs/automage.local.toml`
- 如果要手动覆盖配置文件路径，可以设置 `AUTOMAGE_CONFIG_PATH`

## 设计原则

- 不写死 Hermes Runtime。
- 不把飞书 / OpenClaw 逻辑写进业务 Skill。
- Skill、Schema、API Client、集成适配层保持独立。
- 数据库和后端 API 是事实源。
- 所有未确认契约保留 TODO 注释，等待对应同学确认。

## 当前 Skill 初版

- `agent_init`
- `check_auth_status`
- `load_user_profile`
- `post_daily_report`
- `fetch_my_tasks`
- `analyze_team_reports`
- `generate_manager_report`
- `generate_manager_schema`
- `delegate_task`
- `dream_decision_engine`
- `commit_decision`
- `broadcast_strategy`
- `schema_self_correct`

## 后端 API 初版封装

- `POST /api/v1/agent/init`
- `POST /api/v1/report/staff`
- `GET /api/v1/tasks`
- `POST /api/v1/report/manager`
- `POST /api/v1/decision/commit`

### Runtime Additions

```powershell
python scripts/run_api.py
python scripts/run_scheduler.py
```

New runtime config keys:

- `scheduler_enabled`
- `scheduler_timezone`
- `scheduler_jobs`
- `abuse_protection_enabled`
- `rate_limit_window_seconds`
- `rate_limit_max_requests`
- `idempotency_ttl_seconds`
- `write_protected_paths`

## 本地 Mock 端到端演示

可运行本地 mock 流程：

```powershell
python scripts/demo_mock_flow.py
```

该流程模拟：

- Staff Agent 收到飞书日报提交事件。
- OpenClaw Adapter 把事件交给内部路由。
- Staff Skill 写入 mock 后端日报。
- Manager Agent 生成部门汇总。
- Executive Agent 生成 Dream 决策草案。
- 飞书适配层发送老板 A/B 决策卡片 mock。
- 老板选择方案后写入 mock `decision_logs` 和 `task_queue`。
- Staff Agent 查询新任务。

TODO(OpenClaw): 后续替换为真实 OpenClaw Feishu/Lark Channel。
TODO(熊锦文): 后续替换为真实后端 API 和鉴权。

## Agent 模板渲染

可用示例用户配置渲染 Staff Agent 文档：

```powershell
python scripts/render_agents.py --user examples/user.staff.example.toml --output examples/rendered/staff.agents.md
```

TODO(Hermes): 当前渲染结果是 AutoMage-2 初版 `agents.md`，后续需要按 Hermes 官方格式调整。

## 待确认事项

- TODO(熊锦文): API 字段、错误码、鉴权方式、`user.md` 存储方式。
- TODO(杨卓): `schema_v1_staff` / `schema_v1_manager` 最终字段和校验规则。
- TODO(徐少洋): Dream 机制输入输出。
- TODO(Hermes): 真实 Agent 配置格式和 Skill 注册方式。
- TODO(OpenClaw): Feishu / Lark Channel、事件格式、用户身份映射。
