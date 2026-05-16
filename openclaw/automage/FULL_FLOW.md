# AutoMage 全链路工作流 v2（调度器升级版）

> 最后更新：2026-05-13
> 架构变更：墨智从 Orchestrator → Executor，调度器为 Orchestrator

---

## 🧩 新架构：Orchestrator + Executor

```
调度器（Orchestrator）
  │
  ├─ 每天检查日报
  ├─ 生成汇总任务  →  我（Executor）领取 → 执行 → 完成
  ├─ 生成决策任务  →  我（Executor）领取 → 执行 → 完成
  ├─ 生成催日报任务 →  我（Executor）领取 → 执行 → 完成
  │
  └─ 超时未领取 → 重试；全部完成 → 等待下一轮
```

**我的职责变成**：每 2 分钟轮询调度器，领取任务、执行、标记完成。

---

## 🔄 执行流程

```
循环：
  1. GET /internal/scheduler/pending
  2. 有任务？→ 认领 POST /internal/scheduler/claim/{task_id}
  3. 按 instruction 执行（调 API / LLM 分析 / 推微信）
  4. 标记完成 POST /internal/scheduler/complete/{task_id}
  5. 没有任务 → 等 2 分钟再查
```

---

## 🧩 角色定义

| 角色 | 真实身份 | 在系统中的映射 |
|------|---------|--------------|
| **Staff** | 人类员工（如张三） | 通过前端提交日报 |
| **Executor（我）** | 墨智 | 轮询领取并执行任务 |
| **Orchestrator** | 后端调度器 | 自动创建各类任务 |
| **Executive** | 人类老板（杨卓） | 在微信中回复 A/B |

---

## 📋 任务类型

| 类型 | 触发条件 | 我的操作 |
|------|---------|---------|
| `generate_manager_summary` | 有日报未汇总 | 读日报 → LLM 分析 → POST /api/v1/report/manager |
| `generate_dream_decision` | 汇总标记 escalation=true | 我 LLM 生成 A/B 方案 → 推老板微信 |
| `remind_missing_staff` | 有人没交日报 | 推送到飞书提醒对应员工 |

---

## 🛠 调度器 API

### 查询待办任务

```
GET /internal/scheduler/pending
```

返回任务列表，每项包含：
- `task_id`: 任务 ID
- `type`: `generate_manager_summary` / `generate_dream_decision` / `remind_missing_staff`
- `instruction`: 精确的执行指令
- `data`: 上下文数据（日期、部门、summary_id 等）
- `created_at`: 创建时间

### 认领任务

```
POST /internal/scheduler/claim/{task_id}
```

认领后任务进入执行状态，其他 Executor 不再看到。

### 标记完成

```
POST /internal/scheduler/complete/{task_id}
Content-Type: application/json
Body: { "result": { "status": "success", ... } }
```

`result` 必须是字典（dict 类型），传入执行结果详情。

---

## ⚠️ 会话隔离（重要！）

**每个聊天窗口是独立的 OpenClaw 会话。**
- 老板在微信里回复的「我」= WeChat 通道的另一个会话窗口
- 操作员在 WebChat 教的「我」= 当前这个我
- 但所有会话**共享文件系统**

**实际工作流：**
1. 主线执行器轮询调度器（当前 WebChat / cron 中的我）
2. 收到 `generate_dream_decision` → 生成 A/B → 通过 cron 推送微信
3. 老板在微信回复 A/B → WeChat 会话中的我处理 → 调 `POST /api/v1/decision/commit`
4. 所有会话共享同一套知识配置（文件写入立即可见）

---

## 🕳️ 踩坑记录

### Dream A/B 不调 API

`POST /internal/dream/run` 已废弃。A/B 方案由我（LLM）基于 Manager 汇总的 top_3_risks 直接生成。

### 推送微信用约束 Agent

推送 A/B 到微信时，cron job 的 prompt 必须强制约束 "只转发内容，不分析"。详见下方推送规范。

### 日期由调度器提供

调度器会确保 instruction 中包含完整日期。我不需要自己推断日期。

---

## 📬 WeChat 推送规范

### 推送方法

```typescript
cron.add({
  name: "push-ab-to-boss-wechat",
  schedule: { kind: "at", at: "<ISO 时间>" },
  payload: {
    kind: "agentTurn",
    message: "请将以下内容直接回复出来，不要做任何分析或额外操作：\n\n<格式化A/B内容>",
    timeoutSeconds: 180
  },
  delivery: { mode: "announce", channel: "openclaw-weixin", to: "<老板微信Bot ID>" },
  sessionTarget: "isolated",
  deleteAfterRun: true
})
```

老板微信 Bot ID: `o9cq80-4ZTet7x8h6pGOsyDexBik@im.wechat`
老板用户名：杨卓，微信号：YZ2315766973

### A/B 推送格式

```
📋 AutoMage <部门>日报 A/B 决策方案

━━━━━━━━━━━━━━━━━━━━━━━━
日期：<日期>
部门健康度：🟡 Yellow/🔴 Red

风险概况：
1. 🔴 <风险标题>
2. 🟡 <风险标题>

━━━━━━━━━━━━━━━━━━━━━━━━

🅰 方案 A（<标题>）
【策略】<策略说明>
【任务】<任务分解>
优先级：🔴 高

🅱 方案 B（<标题>）
【策略】<策略说明>
【任务】<任务分解>
优先级：🟡 中

━━━━━━━━━━━━━━━━━━━━━━━━
请回复 A 或 B 确认选择方案。
```

---

## 📋 完整 API 调用

（与前端 API 共用 Header 规范，详见 API.md）

### Manager 汇总提交

```
POST /api/v1/report/manager
X-User-Id: lijingli, X-Role: manager

{
  "identity": { "node_id": "manager_agent_mvp_001", "user_id": "lijingli", "role": "manager", ... },
  "report": {
    "schema_id": "schema_v1_manager",
    "dept_id": "dept_mvp_core",
    "summary_date": "<日期>",
    "overall_health": "green|yellow|red",
    "aggregated_summary": "...",
    "top_3_risks": [
      {"risk_title": "...", "description": "...", "severity": "medium|high", "suggested_action": "..."},
      ...
    ],
    "escalation_required": true|false,
    ...
  }
}
```

> **注意：** `top_3_risks` 支持两种格式：对象数组（含 title/description/severity）或字符串数组。

### 决策提交

```
POST /api/v1/decision/commit
X-User-Id: chenzong, X-Role: executive

{
  "identity": { "node_id": "executive_agent_boss_001", "user_id": "chenzong", "role": "executive" },
  "decision": {
    "selected_option_id": "A",
    "summary_public_id": "MSUM-...",
    "task_candidates": [...]
  }
}
```

---

## 🔐 身份切换

| 操作 | X-User-Id | X-Role |
|------|-----------|--------|
| 查日报 / 写汇总 / 查调度器 | lijingli | manager |
| 落库决策 | chenzong | executive |

我是统一执行者，API 身份根据操作类型切换。
