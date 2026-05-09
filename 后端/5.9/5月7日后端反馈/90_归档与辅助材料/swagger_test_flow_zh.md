# Swagger 中文联调顺序

本文对应当前本地 Swagger 页面：
- `http://localhost:8000/docs`
- `http://localhost:8000/openapi.json`

适用前提：
- 已启动 API：`python scripts/run_api.py`
- 如需正式任务域表结构已建好：`python scripts/init_db.py`
- 如需演示数据：`python scripts/reset_and_seed_demo_data.py`

## 重要提醒：Mock 口径与真实本地口径不要混用

当前仓库里同时存在两套身份示例：

1. Mock / 测试文档口径：
   - `user_agent_001`
   - `user_backend_001`
   - `user_manager_001`
   - `user_executive_001`
2. 当前本地真实种子库口径：
   - `zhangsan`
   - `wangxiaomei`
   - `lijingli`
   - `chenzong`

如果你当前联调的是本地真实环境 `http://localhost:8000`，请优先使用下面这套真实本地口径：

- `org_id=org_automage_mvp`
- `department_id=dept_mvp_core`
- `staff user_id=zhangsan`
- `manager user_id=lijingli`
- `executive user_id=chenzong`
- `backend assignee_user_id=zhangsan`
- `staff node_id=staff_agent_mvp_001`
- `manager node_id=manager_agent_mvp_001`
- `executive node_id=executive_agent_boss_001`

如果你看到旧文档里的 `user_manager_001`、`node-manager-001` 一类示例，请把它们理解为 Mock 身份示例，不要原样用于当前真实本地库。

节点上下级关系统一为：
- `staff_agent_mvp_001 -> manager_agent_mvp_001 -> executive_agent_boss_001`

说明：
- 像 `work_record_id`、`record_id` 这类数据库主键仍然保留数字形态。
- 当前真实本地联调时，业务身份、组织、部门、任务归属统一使用上面的真实本地口径。
- Mock 示例仅用于静态演示、页面占位、结构说明，不作为当前本地真实库联调参数。
- 当前任务正式落表已经是 `tasks / task_assignments / task_updates`，`task_queue` 只保留兼容镜像用途。

---

## 一、认证与权限

当 `auth_enabled=true` 时，除 `GET /healthz` 外，其余接口都需要：

必传请求头：
- `Authorization: Bearer <AUTOMAGE_AUTH_TOKEN>`
- `X-User-Id: <当前调用用户>`
- `X-Role: staff | manager | executive`
- `X-Node-Id: <当前节点 ID>`
- `X-Level: l1_staff | l2_manager | l3_executive`

推荐补充请求头：
- `X-Department-Id: dept_mvp_core`
- `X-Manager-Node-Id: manager_agent_mvp_001`
- `X-Request-Id: swagger-xxx-001`

当前权限口径：
- `staff`：
  - 只能提交自己的员工日报
  - 只能查询自己的员工日报
  - 只能查询分配给自己且节点匹配的任务
- `manager`：
  - 只能提交自己的经理汇总
  - 只能查询自己部门、且属于自己管理链的经理汇总
  - 只能查询自己部门、且属于自己管理链的任务
- `executive`：
  - 保留全局视角
  - 可提交决策并创建正式任务
  - 可使用通用 CRUD 查看全量表数据

---

## 二、当前接口范围

本地最小闭环目前支持这些核心接口：
- `GET /healthz`
- `POST /api/v1/agent/init`
- `POST /api/v1/report/staff`
- `GET /api/v1/report/staff`
- `GET /api/v1/report/staff/{work_record_id}`
- `POST /api/v1/report/staff/import-markdown`
- `POST /api/v1/report/manager`
- `GET /api/v1/report/manager`
- `POST /internal/dream/run`
- `POST /api/v1/decision/commit`
- `POST /api/v1/tasks`
- `GET /api/v1/tasks`
- `PATCH /api/v1/tasks/{task_id}`

---

## 三、固定回归前置条件

建议每次回归前都按下面顺序准备：
- 启动 API：`python scripts/run_api.py`
- 如需初始化表结构：`python scripts/init_db.py`
- 如需重置演示数据：`python scripts/reset_and_seed_demo_data.py`
- 打开 Swagger：`http://localhost:8000/docs`

建议本轮固定使用以下业务 ID：
- `summary_date=2026-05-06`
- `manager summary request_id=swagger-regression-manager-001`
- `decision request_id=swagger-regression-decision-001`
- `task create request_id=swagger-regression-task-create-001`
- `task update request_id=swagger-regression-task-update-001`
- `decision task_id=TASK-REAL-FLOW-001`
- `manual task_id=TASK-REGRESSION-MANUAL-001`
- `dream 选项标题=${OPTION_B_TITLE}`

说明：
- 写接口只有在“幂等重放验证”时才复用同一个 `X-Request-Id`。
- 非幂等重放场景，请不要共用 `X-Request-Id`。
- `POST /api/v1/tasks` 当前以 `task_id` 作为创建幂等锚点，不以 `X-Request-Id` 作为唯一判定依据。

### 固定鉴权头模板

经理身份：

```text
Authorization: Bearer <AUTOMAGE_AUTH_TOKEN>
X-User-Id: lijingli
X-Role: manager
X-Node-Id: manager_agent_mvp_001
X-Level: l2_manager
X-Department-Id: dept_mvp_core
X-Manager-Node-Id: executive_agent_boss_001
```

高层身份：

```text
Authorization: Bearer <AUTOMAGE_AUTH_TOKEN>
X-User-Id: chenzong
X-Role: executive
X-Node-Id: executive_agent_boss_001
X-Level: l3_executive
X-Department-Id: dept_mvp_core
```

执行人 Staff 身份：

```text
Authorization: Bearer <AUTOMAGE_AUTH_TOKEN>
X-User-Id: zhangsan
X-Role: staff
X-Node-Id: staff_agent_mvp_001
X-Level: l1_staff
X-Department-Id: dept_mvp_core
X-Manager-Node-Id: manager_agent_mvp_001
```

---

## 四、经理汇总 -> Dream -> 决策 -> 任务固定回归清单

### 1. 健康检查

接口：
- `GET /healthz`

预期：
- 返回 `{"status": "ok"}`

### 2. 提交经理汇总快照

接口：
- `POST /api/v1/report/manager`

请求头：
- 使用“经理身份”模板
- 追加 `X-Request-Id: swagger-regression-manager-001`

请求体示例：

```json
{
  "identity": {
    "node_id": "manager_agent_mvp_001",
    "user_id": "lijingli",
    "role": "manager",
    "level": "l2_manager",
    "department_id": "dept_mvp_core",
    "manager_node_id": "executive_agent_boss_001",
    "metadata": {
      "display_name": "李经理",
      "source": "swagger"
    }
  },
  "report": {
    "schema_id": "schema_v1_manager",
    "schema_version": "1.0.0",
    "timestamp": "2026-05-06T18:00:00+08:00",
    "org_id": "org_automage_mvp",
    "dept_id": "dept_mvp_core",
    "manager_user_id": "lijingli",
    "manager_node_id": "manager_agent_mvp_001",
    "summary_date": "2026-05-06",
    "staff_report_count": 1,
    "missing_report_count": 0,
    "overall_health": "yellow",
    "aggregated_summary": "Need executive confirmation for backend follow-up tasks.",
    "top_3_risks": [
      "Task handoff needs explicit owner",
      "Need tighter follow-up on summary actions"
    ],
    "pending_approvals": 1,
    "signature": {
      "confirm_status": "confirmed",
      "confirmed_by": "lijingli"
    }
  }
}
```

预期：
- 返回 `200`
- `data.record.summary_public_id` 非空，后面记为 `${SUMMARY_PUBLIC_ID}`
- `data.record.summary_id` 非空
- `data.record.source_count >= 1`

### 3. 查询经理汇总列表

接口：
- `GET /api/v1/report/manager`

请求头：
- 使用“经理身份”模板

查询参数：
- `org_id=org_automage_mvp`
- `summary_date=2026-05-06`
- `dept_id=dept_mvp_core`

预期：
- 返回 `200`
- 结果中能查到 `${SUMMARY_PUBLIC_ID}`
- `manager` 只能看到自己的部门、且 `manager_user_id / manager_node_id` 与自己匹配的记录

### 4. 运行 Dream 生成决策选项

接口：
- `POST /internal/dream/run`

请求头：
- 使用“高层身份”模板

请求体示例：

```json
{
  "summary_id": "${SUMMARY_PUBLIC_ID}"
}
```

预期：
- 返回 `200`
- `data.summary_public_id == ${SUMMARY_PUBLIC_ID}`
- `data.decision_options` 至少包含 `A`、`B`
- 把整个 `data.decision_options` 记录为 `${DREAM_OPTIONS}`
- 选一个后续要提交的选项，建议固定使用 `B`
- 把 `option_id=B` 对应的标题记录为 `${OPTION_B_TITLE}`

### 5. 验证非高层不能运行 Dream

接口：
- `POST /internal/dream/run`

请求头：
- 使用“经理身份”模板

请求体：

```json
{
  "summary_id": "${SUMMARY_PUBLIC_ID}"
}
```

预期：
- 返回 `403`

### 6. 提交高层决策并生成正式任务

接口：
- `POST /api/v1/decision/commit`

请求头：
- 使用“高层身份”模板
- 追加 `X-Request-Id: swagger-regression-decision-001`

请求体示例：

```json
{
  "identity": {
    "node_id": "executive_agent_boss_001",
    "user_id": "chenzong",
    "role": "executive",
    "level": "l3_executive",
    "department_id": "dept_mvp_core",
    "manager_node_id": null,
    "metadata": {
      "display_name": "陈总",
      "source": "swagger"
    }
  },
  "decision": {
    "org_id": "org_automage_mvp",
    "department_id": "dept_mvp_core",
    "summary_id": "${SUMMARY_PUBLIC_ID}",
    "title": "Promote manager summary actions",
    "selected_option_id": "B",
    "selected_option_label": "${OPTION_B_TITLE}",
    "decision_options": [],
    "decision_summary": "Convert the dream option into an executable backend task.",
    "priority": "critical",
    "task_candidates": [
      {
        "task_id": "TASK-REAL-FLOW-001",
        "org_id": "org_automage_mvp",
        "department_id": "dept_mvp_core",
        "source_summary_id": "${SUMMARY_PUBLIC_ID}",
        "manager_user_id": "lijingli",
        "manager_node_id": "manager_agent_mvp_001",
        "assignee_user_id": "zhangsan",
        "assignee_node_id": "staff_agent_mvp_001",
        "title": "Accelerate summary actions",
        "description": "Backend owner started execution from the executive decision.",
        "status": "pending"
      }
    ]
  }
}
```

执行时请把 `decision_options: []` 替换为步骤 4 返回的整段 `decision_options` 数组原文。

预期：
- 返回 `200`
- `data.task_ids` 至少包含 `TASK-REAL-FLOW-001`
- `data.decision.decision_record_public_id` 非空，后面记为 `${DECISION_PUBLIC_ID}`

### 7. 验证非高层不能提交决策

接口：
- `POST /api/v1/decision/commit`

请求头：
- 使用“经理身份”模板

最小请求体示例：

```json
{
  "identity": {
    "node_id": "manager_agent_mvp_001",
    "user_id": "lijingli",
    "role": "manager",
    "level": "l2_manager",
    "department_id": "dept_mvp_core",
    "manager_node_id": "executive_agent_boss_001"
  },
  "decision": {
    "org_id": "org_automage_mvp",
    "department_id": "dept_mvp_core",
    "summary_id": "${SUMMARY_PUBLIC_ID}",
    "selected_option_id": "A"
  }
}
```

预期：
- 返回 `403`

### 8. 直接创建一条手工正式任务

接口：
- `POST /api/v1/tasks`

说明：
- 当前主链路正式写入 `tasks / task_assignments / task_updates`
- 同时兼容镜像一份到 `task_queue`

建议请求头：
- 使用“经理身份”模板
- 追加 `X-Request-Id: swagger-regression-task-create-001`

请求体示例：

```json
{
  "tasks": [
    {
      "schema_id": "schema_v1_task",
      "schema_version": "1.0.0",
      "task_id": "TASK-REGRESSION-MANUAL-001",
      "org_id": "org_automage_mvp",
      "department_id": "dept_mvp_core",
      "task_title": "验证任务创建幂等",
      "task_description": "相同 task_id 重试应返回既有记录。",
      "source_type": "executive_decision",
      "source_id": "",
      "creator_user_id": "lijingli",
      "created_by_node_id": "manager_agent_mvp_001",
      "manager_user_id": "lijingli",
      "manager_node_id": "manager_agent_mvp_001",
      "assignee_user_id": "zhangsan",
      "assignee_node_id": "staff_agent_mvp_001",
      "priority": "critical",
      "status": "pending",
      "confirm_required": false
    }
  ]
}
```

预期：
- 返回 `200`
- `data.tasks[0].task_id == TASK-REGRESSION-MANUAL-001`

### 9. 查询正式任务列表并验证 Staff 收口

接口：
- `GET /api/v1/tasks`

请求头：
- 使用“执行人 Staff 身份”模板

第一轮建议查询参数：
- `user_id=user_someone_else`

预期：
- 返回 `200`
- 即使传了别人的 `user_id`，服务端也会按当前登录身份强制收口
- 列表中至少能看到 `TASK-REAL-FLOW-001`
- 该任务的 `assignee_user_id == zhangsan`
- 该任务初始 `status == pending`

第二轮建议查询参数：
- `user_id=zhangsan`

第三轮建议请求头：
- 把请求头切成“经理身份”模板

第三轮建议查询参数：
- `assignee_user_id=zhangsan`
- `status=pending`

预期：
- `manager` 只能看到“自己部门 + 自己管理链”范围内的任务

### 10. 验证无关 Staff 看不到任务

接口：
- `GET /api/v1/tasks`

请求头示例：

```text
Authorization: Bearer <AUTOMAGE_AUTH_TOKEN>
X-User-Id: user_other_001
X-Role: staff
X-Node-Id: staff_agent_other_001
X-Level: l1_staff
X-Department-Id: dept_mvp_core
X-Manager-Node-Id: manager_agent_mvp_001
```

查询参数：
- `user_id=zhangsan`

预期：
- 返回 `200`
- `data.tasks == []`

### 11. 更新决策生成的任务

接口：
- `PATCH /api/v1/tasks/{task_id}`

当前实现说明：
- 更新正式表 `tasks`
- 同时写入 `task_updates`
- 当前仍保留 `task_queue` 兼容镜像

请求头：
- 使用“执行人 Staff 身份”模板
- 追加 `X-Request-Id: swagger-regression-task-update-001`

请求体示例：

```json
{
  "status": "in_progress",
  "title": "Accelerate summary actions",
  "description": "Backend owner started execution from the executive decision.",
  "task_payload": {
    "execution_note": "picked_up"
  }
}
```

预期：
- 返回 `200`
- `data.task.task_id == TASK-REAL-FLOW-001`
- `data.task.status == in_progress`
- `data.task.task_payload.execution_note == picked_up`

### 12. 验证无关 Staff 不能更新任务

接口：
- `PATCH /api/v1/tasks/TASK-REAL-FLOW-001`

请求头：
- 使用步骤 10 的“无关 Staff”请求头

请求体示例：

```json
{
  "status": "done"
}
```

预期：
- 返回 `403`
- `detail` 中包含 `not allowed`

---

## 五、幂等重放验证

### 1. 经理汇总不做本轮幂等冻结项

说明：
- 本轮固定验收的幂等冻结项不包含 `POST /api/v1/report/manager`。
- 经理汇总本轮重点是“真实链路能跑通、能被 Dream 消费、权限正确”。

### 2. Staff 日报幂等口径

虽然本清单主链路不要求每次都回归 Staff 日报，但若要补跑，请按以下规则确认：
- 同一 `org_id + user_id + record_date` 且业务内容相同，再次提交应返回 `200`
- 返回的 `work_record_id / staff_report_id` 应与首次相同
- 同一业务键但内容不同，应返回 `409`

### 3. 正式任务创建幂等

复用步骤 8 的请求头和请求体，直接再发一次同样的 `POST /api/v1/tasks`。

预期：
- 返回 `200`
- 返回的 `task_id` 仍是 `TASK-REGRESSION-MANUAL-001`
- 不应新增第二条同 `task_id` 任务

再做冲突验证：
- 仅修改 `task_description`，保持 `task_id=TASK-REGRESSION-MANUAL-001` 不变，再发一次

预期：
- 返回 `409`

### 4. 正式任务更新幂等

复用步骤 11 的请求头和请求体，保持 `X-Request-Id: swagger-regression-task-update-001` 不变，再发一次同样的 `PATCH /api/v1/tasks/TASK-REAL-FLOW-001`。

预期：
- 返回 `200`
- 返回任务仍是同一条
- 不应因为重放而重复产生业务更新

再做冲突验证：
- 保持同一个 `X-Request-Id: swagger-regression-task-update-001`
- 把请求体改成：

```json
{
  "status": "done"
}
```

预期：
- 返回 `409`

### 5. 审计追踪核对

建议再补查一次：
- `GET /api/v1/audit-logs?limit=50`

请求头：
- 使用“高层身份”模板

预期：
- 返回 `200`
- `action` 至少包含：
  - `create_manager_report`
  - `dream_run`
  - `commit_decision`
  - `create_task`
  - `update_task`

---

## 六、通用 CRUD 调试

如需直接查看正式任务域底层表数据，可使用：
- `GET /api/v1/crud/tasks`
- `POST /api/v1/crud/tasks`
- `GET /api/v1/crud/tasks/{record_id}`
- `PATCH /api/v1/crud/tasks/{record_id}`
- `DELETE /api/v1/crud/tasks/{record_id}`

- `GET /api/v1/crud/task_assignments`
- `GET /api/v1/crud/task_updates`

兼容镜像表仍可查看：
- `GET /api/v1/crud/task_queue`

说明：
- 通用 CRUD 当前仅建议 `executive` 使用
- 便于核对正式表与兼容镜像表是否同步

---

## 七、审计与追踪

建议重点观察：
- 响应头里的 `X-Request-Id`
- 响应头里的 `X-Process-Time-Ms`
- `GET /api/v1/audit-logs`
- `items[].payload.request_id`

理想情况是：
- 请求头传入的 `X-Request-Id`
- 响应头返回的 `X-Request-Id`
- 审计日志里的 `payload.request_id`

三者一致。

---

## 八、给同事直接照着点的 12 步极简版

1. 打开 `http://localhost:8000/docs`
2. 先调 `GET /healthz`
3. 用 manager 身份调 `POST /api/v1/report/manager`
4. 用 manager 身份调 `GET /api/v1/report/manager`
5. 用 executive 身份调 `POST /internal/dream/run`
6. 用 manager 身份重试一次 `POST /internal/dream/run`，确认返回 `403`
7. 用 executive 身份调 `POST /api/v1/decision/commit`
8. 用 manager 身份重试一次 `POST /api/v1/decision/commit`，确认返回 `403`
9. 用 manager 身份调 `POST /api/v1/tasks`
10. 用 assignee staff 身份调 `GET /api/v1/tasks`
11. 用 assignee staff 身份调 `PATCH /api/v1/tasks/TASK-REAL-FLOW-001`
12. 按本文“幂等重放验证”再补跑任务创建重放、任务更新重放、无关 Staff 越权验证

---

## 九、当前后端口径总结

当前已经收口的点：
- Auth 已接入
- RBAC 已接入
- `GET /tasks` 已按角色、节点、部门隔离
- manager 部门权限已收口
- 任务正式落表已切换到 `tasks / task_assignments / task_updates`

当前仍保留的兼容层：
- `task_queue`

推荐后续动作：
- 如果前后端都已切到正式任务域，可逐步降低 `task_queue` 的主流程权重
- 再视情况补充 `task_updates` 的独立查询接口文档或业务接口


