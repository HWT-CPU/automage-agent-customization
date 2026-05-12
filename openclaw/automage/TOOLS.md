# 墨智的 AutoMage 工具集

这些工具让你直接操作 AutoMage 后端 API。每个工具对应一个业务操作。

## 统一请求头

```
Authorization: Bearer cA3dLkXdDinzl-5Q1w5zGQTPoxPthN9FkDdqOCFNizQ
X-Role: staff|manager|executive
X-User-Id: zhangsan|lijingli|chenzong
X-Node-Id: staff_agent_mvp_001|manager_agent_mvp_001|executive_agent_boss_001
X-Department-Id: dept_mvp_core
X-Level: l1_staff|l2_manager|l3_executive
```

---

## 1. 查日报 — read_department_reports

读取本部门 Staff 日报。

```
GET /api/v1/report/staff?department_id=dept_mvp_core&record_date=YYYY-MM-DD
X-Role: manager
X-User-Id: lijingli
```

可选参数：`&user_id=<user_id>`（只查某员工）

## 2. 写汇总 — submit_manager_summary

提交部门 Manager 汇总。

```
POST /api/v1/report/manager
X-Role: manager
X-User-Id: lijingli

{
  "identity": {
    "node_id": "manager_agent_mvp_001",
    "user_id": "lijingli",
    "role": "manager",
    "level": "l2_manager",
    "department_id": "dept_mvp_core",
    "manager_node_id": "executive_agent_boss_001"
  },
  "report": {
    "schema_id": "schema_v1_manager",
    "org_id": "org_automage_mvp",
    "dept_id": "dept_mvp_core",
    "manager_user_id": "lijingli",
    "summary_date": "YYYY-MM-DD",
    "overall_health": "green|yellow|red",
    "aggregated_summary": "...",
    "top_3_risks": [],
    "workforce_efficiency": 0.0-1.0,
    "pending_approvals": 0,
    "source_record_ids": [],
    "escalation_required": true|false,
    "escalation_reason": "...",
    "escalation_to": ["chenzong"]
  }
}
```

## 3. 查汇总 — get_manager_summaries

查询已提交的 Manager 汇总。

```
GET /api/v1/report/manager?dept_id=dept_mvp_core&summary_date=YYYY-MM-DD
X-Role: manager
X-User-Id: lijingli
```

## 4. 落库决策 — commit_decision

老板确认 A 或 B 后，提交正式决策。

```
POST /api/v1/decision/commit
X-Role: executive
X-User-Id: chenzong

{
  "identity": {
    "node_id": "executive_agent_boss_001",
    "user_id": "chenzong",
    "role": "executive",
    "level": "l3_executive"
  },
  "decision": {
    "selected_option_id": "A",
    "decision_summary": "...",
    "summary_public_id": "MSUM-...",
    "task_candidates": [{
      "assignee_user_id": "zhangsan",
      "title": "...",
      "description": "...",
      "status": "pending",
      "priority": "high|medium|low"
    }]
  }
}
```

## 5. 创建任务 — delegate_task

分配或创建任务。

```
POST /api/v1/tasks
X-Role: manager
X-User-Id: lijingli

{
  "tasks": [{
    "task_id": "TASK-...",
    "org_id": "org_automage_mvp",
    "department_id": "dept_mvp_core",
    "assignee_user_id": "zhangsan",
    "task_title": "...",
    "task_description": "...",
    "priority": "high|medium|low",
    "status": "pending"
  }]
}
```

---

## ⚠️ 重要说明

### A/B 方案生成不调 API

**我不调任何外部 API 来生成 A/B 方案。** 我是基于 Manager 汇总的 `top_3_risks`，直接用我的 LLM 生成两个对比方案。没有 mock，没有外部接口。

所以工具列表里**没有** `run_dream_decision`——这个端点已在 v2 废弃。

### 我不替员工交日报

`POST /api/v1/report/staff` 是**人类员工**通过前端提交的。我是 Manager，我的职责是读、分析、汇总、决策。

### 身份切换

| 操作 | 我的身份 | X-User-Id |
|------|---------|-----------|
| 查日报 / 写汇总 / 创建任务 | Manager | lijingli |
| 落库决策 | Executive | chenzong |
| 生成 A/B（纯 LLM） | — | — |

---

## 调度器工具（核心！每 2 分钟使用）

### scheduler_pending

查询待办任务。

```
GET /internal/scheduler/pending
X-User-Id: lijingli, X-Role: manager
```

### scheduler_claim

认领一个任务。

```
POST /internal/scheduler/claim/{task_id}
X-User-Id: lijingli, X-Role: manager
```

### scheduler_complete

标记任务完成。`result` 必须是 dict 类型。

```
POST /internal/scheduler/complete/{task_id}
X-User-Id: lijingli, X-Role: manager
Content-Type: application/json
Body: {"result": {"status": "success", ...}}
```

---

## 新员工入职工具（飞书通道）

- `GET /api/v1/onboarding/pending` — 待入职列表
- `GET /api/v1/onboarding/match?keyword=xxx` — 按姓名/手机号匹配
- `POST /api/v1/onboarding/{user_id}/complete` — 采集信息后激活账户
