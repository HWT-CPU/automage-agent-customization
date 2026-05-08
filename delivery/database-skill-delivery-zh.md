# 数据库 Skill 交付说明

## 一、交付目标

本次交付的目标，是把 AutoMage 当前“数据库 Skill 如何接后端”这件事说明清楚，并且和现在已经落地的正式后端主链路保持一致。

当前数据库 Skill 的推荐口径已经不是“只写快照表”，而是：

- Agent 优先通过 HTTP API 调后端
- 后端优先写正式业务表
- 快照表仅保留兼容镜像或调试用途
- 关键动作可通过 `audit_logs` 追踪

---

## 二、当前推荐链路

### 1. 正式推荐链路

当前推荐使用：

`Agent -> AutoMageApiClient -> FastAPI 路由 -> service 层 -> SQLAlchemy ORM -> PostgreSQL`

这条链路的特点：

- 走统一 API 契约
- 走当前正式主链路
- 走权限校验与 RBAC
- 走审计日志
- 走限流 / 幂等保护

### 2. 本地直连链路

项目中仍保留一条本地 SQLAlchemy 直连路径：

`Agent -> SqlAlchemyAutoMageApiClient -> SQLAlchemy ORM -> PostgreSQL`

这条路径当前仍存在，但需要明确边界：

- 主要用于本地调试、嵌入式调用、历史兼容
- 当前仍偏旧快照口径
- 不代表当前正式验收链路
- 不经过 HTTP 中间件、权限、RBAC、Redis 版防滥用和完整审计链

如果要验证“当前正式后端是否跑通”，优先应使用 HTTP API 路径。

---

## 三、当前正式主数据口径

当前正式主数据链路如下：

### 1. Staff 日报

主数据表：

- `work_records`
- `work_record_items`

兼容镜像：

- `staff_reports`

补充分支：

- 高风险时自动写 `incidents`
- 同步写 `incident_updates`

### 2. Manager 汇总

主数据表：

- `summaries`
- `summary_source_links`

兼容镜像：

- `manager_reports`

### 3. Executive 决策

主数据表：

- `decision_records`
- `decision_logs`

兼容镜像：

- `agent_decision_logs`

### 4. 正式任务

主数据表：

- `tasks`
- `task_assignments`
- `task_updates`

兼容镜像：

- `task_queue`

### 5. 审计

关键动作统一写：

- `audit_logs`

---

## 四、当前数据库 Skill 对应的正式接口

### 1. Agent 初始化

- 接口：`POST /api/v1/agent/init`
- 主写：`agent_sessions`
- 审计：`audit_logs`

### 2. Staff 提交日报

- 接口：`POST /api/v1/report/staff`
- 主写：`work_records / work_record_items`
- 兼容镜像：`staff_reports`
- 高风险自动分支：`incidents / incident_updates`
- 审计：`audit_logs`

### 3. Staff 查询日报

- 接口：`GET /api/v1/report/staff`
- 接口：`GET /api/v1/report/staff/{work_record_id}`
- 主读：`work_records / work_record_items`

### 4. Manager 提交汇总

- 接口：`POST /api/v1/report/manager`
- 主写：`summaries / summary_source_links`
- 兼容镜像：`manager_reports`
- 审计：`audit_logs`

### 5. Manager 查询汇总

- 接口：`GET /api/v1/report/manager`
- 主读：`summaries`

### 6. Dream 草案

- 接口：`POST /internal/dream/run`
- 主读：`summaries`
- 说明：只返回草案，不写正式决策表

### 7. Executive 提交正式决策

- 接口：`POST /api/v1/decision/commit`
- 主写：`decision_records / decision_logs`
- 确认后生成：`tasks / task_assignments / task_updates`
- 兼容镜像：`agent_decision_logs / task_queue`
- 审计：`audit_logs`

### 8. 任务查询与更新

- 接口：`GET /api/v1/tasks`
- 接口：`POST /api/v1/tasks`
- 接口：`PATCH /api/v1/tasks/{task_id}`
- 主读主写：`tasks / task_assignments / task_updates`
- 兼容镜像：`task_queue`
- 审计：`audit_logs`

### 9. 审计日志查询

- 接口：`GET /api/v1/audit-logs`
- 主读：`audit_logs`

---

## 五、当前与旧数据库 Skill 口径的差异

为了避免误解，这里明确说明当前和旧版口径的差异：

### 1. `POST /api/v1/report/staff`

旧口径：

- 认为它只写 `staff_reports`

当前口径：

- 它已经是正式写入入口
- 主写 `work_records / work_record_items`
- `staff_reports` 只是镜像

### 2. `POST /api/v1/report/manager`

旧口径：

- 认为它只写 `manager_reports`

当前口径：

- 主写 `summaries / summary_source_links`
- `manager_reports` 只是镜像

### 3. `POST /api/v1/decision/commit`

旧口径：

- 认为它主写 `agent_decision_logs / task_queue`

当前口径：

- 主写 `decision_records / decision_logs`
- 正式任务主写 `tasks / task_assignments / task_updates`
- `agent_decision_logs / task_queue` 只是镜像

### 4. `GET /api/v1/tasks`

旧口径：

- 认为它主读 `task_queue`

当前口径：

- 它已经主读 `tasks + task_assignments`
- `task_queue` 不再是正式默认任务源

---

## 六、权限、审计与防滥用

当前数据库 Skill 如走 HTTP API 路径，会自动进入以下保护链：

### 1. 权限与 RBAC

- 角色限制：`staff / manager / executive`
- 资源归属校验
- 部门范围校验
- 任务更新权限校验
- 审计日志查询范围校验

### 2. 审计

关键动作会写：

- `audit_logs`

并保留：

- `request_id`
- `target_type`
- `target_id`
- `action`
- `payload`

### 3. 防滥用

当前已支持：

- 基础限流
- 幂等保护
- `Idempotency-Key`

当前后端已支持：

- `memory` 版
- `redis` 版

如果走 SQLAlchemy 直连路径，上述保护链默认不完整。

---

## 七、当前推荐给 Agent 的数据库 Skill 结论

如果现在要对外讲“数据库 Skill 是否匹配当前项目”，推荐统一结论如下：

1. 当前数据库 Skill 已经可以匹配现有正式后端，但必须以 HTTP API 路径为主口径。
2. 原先只围绕 `staff_reports / manager_reports / task_queue` 的说法已经过时，需要切换到正式表主链路。
3. SQLAlchemy 直连路径仍保留，但更适合作为本地调试或历史兼容说明，不建议作为当前正式联调验收主路径。
4. 当前正式链路已经覆盖权限、RBAC、审计、Redis 版防滥用等能力，这些都是数据库 Skill 对齐当前项目时必须说明的部分。

---

## 八、本次同步后的交付产物

本次已经对齐并保留以下交付内容：

1. `delivery/database-skill-delivery-zh.md`
2. `delivery/database-api-skill/SKILL.md`
3. `delivery/database-api-skill/references/http-flow.md`
4. `delivery/database-api-skill/references/sqlalchemy-flow.md`
5. `delivery/database-api-skill/references/table-map.md`

这些内容现在统一对齐当前正式后端主链路。
