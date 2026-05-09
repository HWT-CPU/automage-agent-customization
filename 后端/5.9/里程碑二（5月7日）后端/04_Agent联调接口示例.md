# Agent 联调接口示例

## 1. 说明

本文档面向后端与 Agent 联调，目标是给出一套可以直接拿去调用的接口样例。

当前正式主链路对应的正式表为：

- 日报：`work_records / work_record_items`
- 汇总：`summaries / summary_source_links`
- 决策：`decision_records / decision_logs`
- 任务：`tasks / task_assignments / task_updates`

兼容镜像表保留，但不再作为主数据源：

- `staff_reports`
- `manager_reports`
- `agent_decision_logs`
- `task_queue`

---

## 2. 统一请求头

当 `auth_enabled=true` 时，除健康检查外，建议统一带以下请求头：

```http
Authorization: Bearer <AUTOMAGE_AUTH_TOKEN>
X-User-Id: <当前用户ID>
X-Role: staff | manager | executive
X-Node-Id: <当前节点ID>
X-Level: l1_staff | l2_manager | l3_executive
X-Department-Id: <部门ID>
X-Manager-Node-Id: <上级节点ID>
X-Request-Id: <请求唯一ID>
Idempotency-Key: <关键写接口推荐携带>
```

推荐联调身份：

- 组织：`org_automage_mvp`
- 部门：`dept_mvp_core`
- Staff：`user_agent_001 / staff_agent_mvp_001`
- Manager：`user_manager_001 / manager_agent_mvp_001`
- Executive：`user_executive_001 / executive_agent_boss_001`

---

## 3. Staff 提交日报

接口：

- `POST /api/v1/report/staff`

作用：

- 提交正式日报
- 写入正式表
- 高风险时自动创建异常

请求体示例：

```json
{
  "identity": {
    "node_id": "staff_agent_mvp_001",
    "user_id": "user_agent_001",
    "role": "staff",
    "level": "l1_staff",
    "department_id": "dept_mvp_core",
    "manager_node_id": "manager_agent_mvp_001"
  },
  "report": {
    "schema_id": "schema_v1_staff",
    "schema_version": "1.0.0",
    "timestamp": "2026-05-07T10:00:00+08:00",
    "org_id": "org_automage_mvp",
    "department_id": "dept_mvp_core",
    "user_id": "user_agent_001",
    "node_id": "staff_agent_mvp_001",
    "record_date": "2026-05-07",
    "work_progress": "已完成后端主链路回归检查，并准备 Agent 联调材料。",
    "issues_faced": "仍需与 Agent 侧一起验证真实读写闭环。",
    "solution_attempt": "先固定正式表口径，再统一联调样例和核查 SQL。",
    "need_support": true,
    "next_day_plan": "配合 Agent 侧跑通真实数据库 Skill 联调。",
    "risk_level": "high",
    "signature": {
      "confirm_status": "confirmed",
      "confirmed_by": "user_agent_001"
    }
  }
}
```

响应关键字段：

```json
{
  "code": 200,
  "data": {
    "record": {
      "work_record_id": 101,
      "work_record_public_id": "WRK0000000000000000000101",
      "staff_report_id": 12,
      "incident_ids": [9]
    }
  },
  "msg": "Staff report saved"
}
```

落库表：

- `work_records`
- `work_record_items`
- `staff_reports`
- 高风险时额外写：
  - `incidents`
  - `incident_updates`
- `audit_logs`

---

## 4. Manager 提交汇总

接口：

- `POST /api/v1/report/manager`

请求体示例：

```json
{
  "identity": {
    "node_id": "manager_agent_mvp_001",
    "user_id": "user_manager_001",
    "role": "manager",
    "level": "l2_manager",
    "department_id": "dept_mvp_core",
    "manager_node_id": "executive_agent_boss_001"
  },
  "report": {
    "schema_id": "schema_v1_manager",
    "schema_version": "1.0.0",
    "timestamp": "2026-05-07T18:00:00+08:00",
    "org_id": "org_automage_mvp",
    "dept_id": "dept_mvp_core",
    "manager_user_id": "user_manager_001",
    "manager_node_id": "manager_agent_mvp_001",
    "summary_date": "2026-05-07",
    "staff_report_count": 2,
    "missing_report_count": 0,
    "overall_health": "yellow",
    "aggregated_summary": "正式主链路已切到正式表，当前重点是完成 Agent 真实读写联调。",
    "top_3_risks": [
      "Agent 真实读写验收尚未跑通",
      "Dream 当前仍是最小占位实现",
      "历史快照数据未迁移"
    ],
    "pending_approvals": 1,
    "source_record_ids": [
      "WRK0000000000000000000101",
      "WRK0000000000000000000102"
    ],
    "signature": {
      "confirm_status": "confirmed",
      "confirmed_by": "user_manager_001"
    }
  }
}
```

响应关键字段：

```json
{
  "code": 200,
  "data": {
    "record": {
      "summary_id": 21,
      "summary_public_id": "SUM0000000000000000000021",
      "source_count": 2
    }
  },
  "msg": "Manager summary saved"
}
```

落库表：

- `summaries`
- `summary_source_links`
- `manager_reports`
- `audit_logs`

---

## 5. Dream 草案接口

接口：

- `POST /internal/dream/run`

请求体示例：

```json
{
  "summary_id": "SUM0000000000000000000021"
}
```

响应关键字段：

```json
{
  "code": 200,
  "data": {
    "summary_id": 21,
    "summary_public_id": "SUM0000000000000000000021",
    "contract_status": "pending_dream_confirmation",
    "decision_options": [
      {
        "option_id": "A",
        "title": "Conservative execution plan"
      },
      {
        "option_id": "B",
        "title": "Aggressive execution plan"
      }
    ]
  },
  "msg": "Dream decision draft generated"
}
```

说明：

- 当前只返回决策草案
- 不写 `decision_records`
- 不生成正式任务

---

## 6. Executive 提交正式决策

接口：

- `POST /api/v1/decision/commit`

请求体示例：

```json
{
  "identity": {
    "node_id": "executive_agent_boss_001",
    "user_id": "user_executive_001",
    "role": "executive",
    "level": "l3_executive",
    "department_id": "dept_mvp_core"
  },
  "decision": {
    "org_id": "org_automage_mvp",
    "department_id": "dept_mvp_core",
    "summary_id": "SUM0000000000000000000021",
    "title": "是否先完成 Agent 真实读写验证",
    "decision_summary": "优先完成 Agent 真实读写闭环，再推进后续扩展。",
    "selected_option_id": "A",
    "selected_option_label": "先完成联调验收",
    "comment": "先确保正式表链路和任务闭环稳定。",
    "task_candidates": [
      {
        "task_id": "TASK-20260507-AGENT-001",
        "org_id": "org_automage_mvp",
        "department_id": "dept_mvp_core",
        "task_title": "完成 Agent 真实读写联调",
        "task_description": "验证日报提交、任务查询、任务更新闭环。",
        "assignee_user_id": "user_agent_001",
        "priority": "high",
        "status": "pending"
      }
    ]
  }
}
```

响应关键字段：

```json
{
  "code": 200,
  "data": {
    "decision": {
      "decision_record_id": 8,
      "decision_record_public_id": "DEC0000000000000000000008"
    },
    "task_ids": [
      "TASK-20260507-AGENT-001"
    ]
  },
  "msg": "Decision committed"
}
```

落库表：

- `decision_records`
- `decision_logs`
- `agent_decision_logs`
- 若带任务候选：
  - `tasks`
  - `task_assignments`
  - `task_updates`
  - `task_queue`
- `audit_logs`

---

## 7. 任务查询与更新

### 7.1 查询任务

接口：

- `GET /api/v1/tasks?assignee_user_id=user_agent_001&status=pending`

说明：

- 默认读取正式任务视图
- 读取来源为 `tasks + task_assignments`

### 7.2 更新任务

接口：

- `PATCH /api/v1/tasks/TASK-20260507-AGENT-001`

请求体示例：

```json
{
  "status": "in_progress",
  "description": "已开始验证日报写入和任务查询闭环。",
  "task_payload": {
    "progress": "40%"
  }
}
```

更新效果：

- 更新 `tasks`
- 追加一条 `task_updates`
- 同步镜像 `task_queue`
- 写入 `audit_logs`

---

## 8. 审计日志查询

接口：

- `GET /api/v1/audit-logs?target_type=tasks&limit=20`

用途：

- 联调排障
- 验证关键动作是否真实落库
- 反查某一步是否真的经过后端处理

---

## 9. 联调提示

建议联调顺序：

1. Staff 提交日报
2. Manager 提交汇总
3. Executive 调用 Dream 草案
4. Executive 提交正式决策
5. Staff 查询任务
6. Staff 更新任务
7. 用审计日志和 SQL 核查结果

说明：

- 后端已经准备好联调接口、样例和核查材料
- “Agent 通过数据库 Skill 的真实读写联调验收”最终仍需要 Agent 负责人实际发起调用完成验证
