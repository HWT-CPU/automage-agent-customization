# HTTP API 链路

当 Agent 通过 FastAPI 服务访问数据库时，使用这份说明。

## 端到端链路

当前推荐正式路径如下：

1. Agent 调用 `AutoMageApiClient` 的某个方法，或按接口契约直接发 HTTP 请求
2. `AutoMageApiClient` 把请求序列化为 JSON，并发送 HTTP 请求
3. FastAPI 在 `app.py` 或 `daily_report_api.py` 中接收请求
4. 路由通过 `get_db_session()` 注入数据库会话
5. 路由调用 service 层函数
6. service 层通过 SQLAlchemy ORM 读写正式业务表
7. 核心写接口在提交事务时会写入 `audit_logs`
8. 请求还会经过身份校验、RBAC、限流、幂等保护
9. API 返回统一响应体

## Agent 侧入口

入口文件：

- [client.py](D:/Code/A实习项目/automage-agent-customization-main/automage_agents/api/client.py)

当前已提供的主要客户端方法：

- `agent_init(identity)`
- `post_staff_report(identity, report_payload)`
- `fetch_tasks(identity, status=None)`
- `post_manager_report(identity, report_payload)`
- `commit_decision(identity, decision_payload)`
- `run_dream(identity, summary_id)`

说明：

- 当前客户端封装的是最常用主链路
- `POST /api/v1/tasks`、`PATCH /api/v1/tasks/{task_id}`、`GET /api/v1/audit-logs` 这类接口当前更多通过 Swagger、HTTP 调试工具或后续扩展 client 使用

## 服务端入口

服务端文件：

- [app.py](D:/Code/A实习项目/automage-agent-customization-main/automage_agents/server/app.py)
- [daily_report_api.py](D:/Code/A实习项目/automage-agent-customization-main/automage_agents/server/daily_report_api.py)

当前核心接口包括：

- `POST /api/v1/agent/init`
- `POST /api/v1/report/staff`
- `GET /api/v1/report/staff`
- `GET /api/v1/report/staff/{work_record_id}`
- `POST /api/v1/report/manager`
- `GET /api/v1/report/manager`
- `POST /internal/dream/run`
- `POST /api/v1/decision/commit`
- `POST /api/v1/tasks`
- `GET /api/v1/tasks`
- `PATCH /api/v1/tasks/{task_id}`
- `GET /api/v1/audit-logs`
- `GET / POST / PUT / PATCH / DELETE /api/v1/crud/{resource}`

## 当前正式主表

HTTP 主链路下，当前正式主数据源为：

- Staff 日报：`work_records / work_record_items`
- Manager 汇总：`summaries / summary_source_links`
- Executive 决策：`decision_records / decision_logs`
- 正式任务：`tasks / task_assignments / task_updates`
- 审计：`audit_logs`

以下表仍保留，但仅作为兼容镜像或调试用途：

- `staff_reports`
- `manager_reports`
- `agent_decision_logs`
- `task_queue`

## 审计与请求追踪

HTTP 路径下，请求追踪和保护链是完整的：

- 中间件会生成或透传 `X-Request-Id`
- 核心写接口会写入 `audit_logs`
- 鉴权层会做身份一致性校验和 RBAC 范围校验
- 防滥用中间件会做限流与幂等保护
- 当前防滥用支持 `memory` 和 `redis` 两种后端

相关文件：

- [middleware.py](D:/Code/A实习项目/automage-agent-customization-main/automage_agents/server/middleware.py)
- [auth.py](D:/Code/A实习项目/automage-agent-customization-main/automage_agents/server/auth.py)
- [rbac.py](D:/Code/A实习项目/automage-agent-customization-main/automage_agents/server/rbac.py)
- [audit.py](D:/Code/A实习项目/automage-agent-customization-main/automage_agents/server/audit.py)

## 推荐一句话说明

对外可以这样概括：

`Agent -> AutoMageApiClient -> FastAPI 路由 -> service 层 -> SQLAlchemy Model -> PostgreSQL -> audit_logs`
