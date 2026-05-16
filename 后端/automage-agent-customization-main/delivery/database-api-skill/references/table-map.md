# 接口与数据表映射

这份说明用于回答“哪个 Agent 能力通过哪个 API 写了哪张表”。

## 1. Agent 初始化

- 接口或方法：
  `POST /api/v1/agent/init`
  `AutoMageApiClient.agent_init()`
- service 层：
  `create_agent_session()`
- 主写表：
  `agent_sessions`
  `audit_logs`
- 作用：
  记录 Agent 身份、角色、层级和会话元数据

## 2. Staff 正式日报提交

- 接口或方法：
  `POST /api/v1/report/staff`
  `AutoMageApiClient.post_staff_report()`
- service 层：
  `create_staff_report()`
- 主写表：
  `work_records`
  `work_record_items`
  `audit_logs`
- 兼容镜像：
  `staff_reports`
- 高风险自动分支：
  `incidents`
  `incident_updates`
- 作用：
  保存正式日报数据，并在高风险场景自动生成异常记录

## 3. Staff 日报列表与详情读取

- 接口或方法：
  `GET /api/v1/report/staff`
  `GET /api/v1/report/staff/{work_record_id}`
- service 层：
  `list_staff_reports()`
  `read_staff_daily_report()`
- 主读表：
  `work_records`
  `work_record_items`
- 作用：
  从正式业务表中查询日报列表和日报详情

## 4. Manager 正式汇总提交

- 接口或方法：
  `POST /api/v1/report/manager`
  `AutoMageApiClient.post_manager_report()`
- service 层：
  `create_manager_report()`
- 主写表：
  `summaries`
  `summary_source_links`
  `audit_logs`
- 兼容镜像：
  `manager_reports`
- 作用：
  保存正式经理汇总，并保留来源关联

## 5. Manager 汇总读取

- 接口或方法：
  `GET /api/v1/report/manager`
- service 层：
  `list_manager_reports()`
- 主读表：
  `summaries`
  兼容展示时可参考 `manager_reports`
- 作用：
  查询经理汇总列表

## 6. Dream 草案

- 接口或方法：
  `POST /internal/dream/run`
  `AutoMageApiClient.run_dream()`
- service 层：
  `run_dream_from_summary()`
- 主读表：
  `summaries`
- 可审计：
  `audit_logs`
- 作用：
  基于汇总生成决策草案，不直接生成正式任务

## 7. Executive 正式决策提交

- 接口或方法：
  `POST /api/v1/decision/commit`
  `AutoMageApiClient.commit_decision()`
- service 层：
  `commit_decision()`
- 主写表：
  `decision_records`
  `decision_logs`
  `audit_logs`
- 兼容镜像：
  `agent_decision_logs`
- 若确认并带任务候选，则额外写：
  `tasks`
  `task_assignments`
  `task_updates`
  `task_queue`
- 作用：
  沉淀正式决策，并在需要时生成正式任务

## 8. 正式任务创建

- 接口或方法：
  `POST /api/v1/tasks`
- service 层：
  `create_tasks()`
- 主写表：
  `tasks`
  `task_assignments`
  `task_updates`
  `audit_logs`
- 兼容镜像：
  `task_queue`
- 作用：
  创建正式任务，并同步保留兼容镜像

## 9. 正式任务读取

- 接口或方法：
  `GET /api/v1/tasks`
  `AutoMageApiClient.fetch_tasks()`
- service 层：
  `list_tasks()`
- 主读表：
  `tasks`
  `task_assignments`
- 兼容镜像：
  `task_queue`
- 作用：
  查询正式任务视图，并按登录人或执行人过滤

## 10. 正式任务更新

- 接口或方法：
  `PATCH /api/v1/tasks/{task_id}`
- service 层：
  `update_task()`
- 主写表：
  `tasks`
  `task_updates`
  `audit_logs`
- 兼容镜像：
  `task_queue`
- 作用：
  更新任务当前状态，同时追加任务事件记录

## 11. 审计日志查询

- 接口或方法：
  `GET /api/v1/audit-logs`
- service 层：
  `list_audit_logs()`
- 读取表：
  `audit_logs`
- 作用：
  按对象类型、操作人和时间范围查询关键动作

## 12. 通用 CRUD

支持的资源表定义在 [crud.py](D:/Code/A实习项目/automage-agent-customization-main/automage_agents/server/crud.py)。

读接口：

- `GET /api/v1/crud/{resource}`
- `GET /api/v1/crud/{resource}/{record_id}`

写接口：

- `POST /api/v1/crud/{resource}`
- `PUT /api/v1/crud/{resource}/{record_id}`
- `PATCH /api/v1/crud/{resource}/{record_id}`
- `DELETE /api/v1/crud/{resource}/{record_id}`

写库说明：

- 直接写所选 `resource`
- 同时补写 `audit_logs`

## 13. 当前 Skill 覆盖的主要物理表

主模型文件：

- [models.py](D:/Code/A实习项目/automage-agent-customization-main/automage_agents/db/models.py)

当前最重要的正式业务表：

- `agent_sessions`
- `work_records`
- `work_record_items`
- `incidents`
- `incident_updates`
- `summaries`
- `summary_source_links`
- `decision_records`
- `decision_logs`
- `tasks`
- `task_assignments`
- `task_updates`
- `audit_logs`

当前仍保留的兼容镜像表：

- `staff_reports`
- `manager_reports`
- `agent_decision_logs`
- `task_queue`
