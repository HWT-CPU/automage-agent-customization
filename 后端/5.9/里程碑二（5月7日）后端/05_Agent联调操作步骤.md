# Agent 联调操作步骤

## 1. 目标

本文档用于跑通一条最小闭环：

`Staff 提交日报 -> Manager 汇总 -> Dream 草案 -> Executive 决策 -> 任务生成 -> Staff 查询任务 -> Staff 更新任务`

如果这条链路跑通，就可以说明后端已经具备 Agent 联调所需的正式接口和正式落库能力。

---

## 2. 联调前准备

### 2.1 基础信息

- 数据库地址：`182.92.93.16`
- 数据库名：`automage`
- 用户名：`automage`

### 2.2 推荐联调身份

- 组织：`org_automage_mvp`
- 部门：`dept_mvp_core`
- Staff：`user_agent_001 / staff_agent_mvp_001`
- Manager：`user_manager_001 / manager_agent_mvp_001`
- Executive：`user_executive_001 / executive_agent_boss_001`

### 2.3 推荐先看的文档

1. `04_Agent联调接口示例.md`
2. `06_数据库核查SQL.md`

---

## 3. 联调步骤

### 步骤 1：Staff 提交日报

接口：

- `POST /api/v1/report/staff`

预期结果：

- 写入 `work_records`
- 写入 `work_record_items`
- 镜像写入 `staff_reports`
- 高风险时写入 `incidents / incident_updates`
- 写入 `audit_logs`

本步产出：

- `work_record_id`
- 如高风险则产出 `incident_ids`

### 步骤 2：Manager 提交汇总

接口：

- `POST /api/v1/report/manager`

预期结果：

- 写入 `summaries`
- 写入 `summary_source_links`
- 镜像写入 `manager_reports`
- 写入 `audit_logs`

本步产出：

- `summary_id`

### 步骤 3：Executive 获取 Dream 草案

接口：

- `POST /internal/dream/run`

预期结果：

- 返回决策草案
- 不写正式决策表
- 不生成正式任务

本步产出：

- 可用于下一步决策提交的草案选项

### 步骤 4：Executive 提交正式决策

接口：

- `POST /api/v1/decision/commit`

预期结果：

- 写入 `decision_records`
- 写入 `decision_logs`
- 镜像写入 `agent_decision_logs`
- 若带 `task_candidates`，则生成正式任务：
  - `tasks`
  - `task_assignments`
  - `task_updates`
  - `task_queue`
- 写入 `audit_logs`

本步产出：

- `decision_record_id`
- `task_ids`

### 步骤 5：Staff 查询任务

接口：

- `GET /api/v1/tasks?assignee_user_id=user_agent_001&status=pending`

预期结果：

- 查到上一步生成的正式任务
- 数据来源为 `tasks + task_assignments`

### 步骤 6：Staff 更新任务

接口：

- `PATCH /api/v1/tasks/{task_id}`

预期结果：

- 更新 `tasks.status`
- 新增一条 `task_updates`
- 同步镜像 `task_queue`
- 写入 `audit_logs`

### 步骤 7：审计与数据库核查

接口：

- `GET /api/v1/audit-logs`

SQL：

- 参考 `06_数据库核查SQL.md`

预期结果：

- 能看到日报、汇总、决策、任务更新的关键动作
- 能在数据库中查到对应正式落库记录

---

## 4. 验收判断标准

满足以下条件即可判断联调闭环成立：

1. Staff 日报成功进入 `work_records / work_record_items`
2. 高风险日报能自动创建异常
3. Manager 汇总成功进入 `summaries / summary_source_links`
4. Dream 只返回草案，不污染正式决策表
5. Executive 决策成功进入 `decision_records / decision_logs`
6. 正式任务成功进入 `tasks / task_assignments / task_updates`
7. Staff 能查到自己的任务并更新状态
8. `audit_logs` 能完整反映关键动作

---

## 5. 当前边界说明

后端侧目前已经完成：

- 正式接口准备
- 正式表落库能力
- 联调样例准备
- SQL 核查准备

但以下事情仍不属于后端单独完成项：

- Agent 侧是否真正调用了数据库 Skill
- Agent 侧是否按约定身份头和请求体发起真实联调
- Agent 侧最终验收截图或录屏

因此可以明确说：

- 后端已经为 Agent 联调准备完毕
- 最终“Agent 通过数据库 Skill 的真实读写联调验证”仍需要 Agent 负责人实际执行
