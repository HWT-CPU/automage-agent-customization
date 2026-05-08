# SQLAlchemy 直连链路

当 Agent 不经过 HTTP，而是直接通过 ORM 访问数据库时，使用这份说明。

## 端到端链路

完整路径如下：

1. Agent 调用 `SqlAlchemyAutoMageApiClient` 的方法
2. 客户端通过 `session_factory` 打开 SQLAlchemy session
3. 代码直接创建或查询 ORM 模型
4. 事务在本地提交
5. 返回 `ApiResponse`，其结构尽量和 HTTP 模式保持一致

## 入口文件

- [sqlalchemy_client.py](D:/Code/A实习项目/automage-agent-customization-main/automage_agents/api/sqlalchemy_client.py)

当前核心方法包括：

- `agent_init(identity)`：插入 `AgentSessionModel`
- `post_staff_report(identity, report_payload)`：插入 `StaffReportModel`
- `fetch_tasks(identity, status=None)`：查询 `TaskQueueModel`
- `post_manager_report(identity, report_payload)`：插入 `ManagerReportModel`
- `commit_decision(identity, decision_payload)`：插入 `DecisionLogModel`，必要时插入 `TaskQueueModel`

## 当前边界

这条路径当前仍保留，但必须明确：

- 它主要对应旧快照表链路
- 它没有完整覆盖当前正式主链路
- 它不经过 FastAPI
- 它不经过 `get_db_session()`
- 它不经过请求中间件
- 它默认不经过完整权限、RBAC、Redis 版限流 / 幂等
- 当前实现下不会自动补写和 HTTP 一样完整的审计链

## 与 HTTP 模式的区别

SQLAlchemy 直连模式：

- 更适合本地调试
- 更适合嵌入式调用
- 更偏历史兼容
- 当前主写快照表：`staff_reports / manager_reports / agent_decision_logs / task_queue`

HTTP API 模式：

- 有标准请求/响应契约
- 当前对齐正式后端主链路
- 有权限、RBAC、审计、限流、幂等保护
- 当前主写正式表：`work_records / summaries / decision_records / tasks`

## 推荐一句话说明

对外可以这样概括：

`Agent -> SqlAlchemyAutoMageApiClient -> ORM Model -> PostgreSQL`

但要补一句：

这条路径当前主要用于本地调试和历史兼容，不应替代当前正式 HTTP API 主链路。
