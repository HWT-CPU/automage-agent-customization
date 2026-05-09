---
name: database-api-skill
description: 用于说明或实现 AutoMage Agent 如何通过 API 接口、服务层和数据库表读写 PostgreSQL。适用于数据库 Skill 交付、团队 onboarding、接口到数据表映射说明，以及 Agent 到 API 到数据库链路排查等场景。
---

# 数据库 API Skill

使用本 Skill 时，优先讲清楚“当前正式主链路怎么走”，不要继续把快照表当成默认主数据源。

## 快速使用

当有人问“Agent 现在是怎么读写数据库的”时，按下面顺序回答：

1. 先判断走的是 HTTP API 正式链路，还是本地 SQLAlchemy 直连链路。
2. 再定位 Agent 调用了哪个客户端方法或哪个 API 接口。
3. 再往下追到 FastAPI 路由和 service 层函数。
4. 明确最终主读主写的是哪几张正式表。
5. 补充说明是否还会镜像写入旧快照表。
6. 补充说明是否会写 `audit_logs`，是否受权限、RBAC、限流、幂等保护。

## 先判断两条路径

### 1. HTTP API 路径

这是当前推荐的正式链路。

- 参考 [references/http-flow.md](references/http-flow.md)
- 入口文件是 [client.py](D:/Code/A实习项目/automage-agent-customization-main/automage_agents/api/client.py)

### 2. SQLAlchemy 直连路径

这是保留的本地直连链路，主要用于调试和历史兼容。

- 参考 [references/sqlalchemy-flow.md](references/sqlalchemy-flow.md)
- 入口文件是 [sqlalchemy_client.py](D:/Code/A实习项目/automage-agent-customization-main/automage_agents/api/sqlalchemy_client.py)

注意：

- 这条路径当前仍偏旧快照表口径
- 不代表当前正式验收主路径

## 当前正式主链路

当前最重要的正式写库能力包括：

- `agent_init`：写入 `agent_sessions`
- `post_staff_report` 或 `POST /api/v1/report/staff`：主写 `work_records / work_record_items`，镜像 `staff_reports`
- `post_manager_report` 或 `POST /api/v1/report/manager`：主写 `summaries / summary_source_links`，镜像 `manager_reports`
- `run_dream` 或 `POST /internal/dream/run`：主读 `summaries`，只返回草案
- `commit_decision` 或 `POST /api/v1/decision/commit`：主写 `decision_records / decision_logs`，确认后生成 `tasks / task_assignments / task_updates`
- `POST /api/v1/tasks`：主写正式任务链路
- `PATCH /api/v1/tasks/{task_id}`：更新 `tasks` 并追加 `task_updates`

## 当前正式读库链路

当前最重要的正式读库能力包括：

- `GET /api/v1/report/staff`：从正式日报表聚合读取
- `GET /api/v1/report/staff/{work_record_id}`：读取 `work_records / work_record_items`
- `GET /api/v1/report/manager`：从 `summaries` 读取
- `fetch_tasks` 或 `GET /api/v1/tasks`：主读 `tasks + task_assignments`
- `GET /api/v1/audit-logs`：读取 `audit_logs`

## 日报说明规则

日报相关能力必须区分两种口径：

### 1. 当前正式业务口径

接口：

- `POST /api/v1/report/staff`
- `GET /api/v1/report/staff`
- `GET /api/v1/report/staff/{work_record_id}`

作用：

- 主写正式日报表
- 正式读取正式日报表

### 2. 快照兼容口径

当前 `staff_reports` 仍保留，但只是：

- 镜像写入
- 历史兼容
- 调试排障

不要再把它描述成当前唯一主数据源。

## 审计与保护规则

如果交付内容涉及正式链路，必须补充说明：

- 关键写接口会写 `audit_logs`
- HTTP 路径会经过权限与 RBAC
- HTTP 路径会经过限流与幂等保护
- 当前防滥用已支持 `memory` 和 `redis` 两种后端

## 推荐输出格式

对外讲解时，统一按这个顺序组织：

1. Agent 调用入口
2. API 接口或客户端方法
3. service 层函数
4. 主读主写的正式表
5. 是否有兼容镜像写入
6. 是否写审计日志
7. 是否经过权限、RBAC、限流、幂等保护

## 参考资料

- [references/http-flow.md](references/http-flow.md)
- [references/sqlalchemy-flow.md](references/sqlalchemy-flow.md)
- [references/table-map.md](references/table-map.md)
