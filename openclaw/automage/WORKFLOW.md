# 墨智工作流程手册

> 全链路闭环文档详见 [FULL_FLOW.md](./FULL_FLOW.md)
> 最新修正：2026-05-13

---

## 三个核心原则

1. **全流程在一个主会话串行执行** — 不拆到多个隔离会话
2. **推送 = 只转发，不分析** — 推送 Agent 无权启动自主流程
3. **日期由员工日报决定** — 后续所有步骤用同一日期

---

## ⚠️ 会话隔离

**每个聊天窗口（WebChat / 微信 / 飞书）是独立的 OpenClaw 会话。**
- 老板在微信回 A/B → 由微信会话中的我处理决策落库
- 操作员在 WebChat 配置 → 由当前会话中的我更新文件
- **共享文件**保证所有会话知识一致

---

## 日报分析流程

我收到部门日报数据后：

1. LLM 理解每份日报的进展、问题、风险
2. 提取结构化洞察
3. 综合生成 Manager 汇总字段（详见 FULL_FLOW.md Step 3）
4. 判断 `escalation_required`

---

## A/B 决策方案（纯 LLM，无 API）

基于 Manager 汇总的 `top_3_risks` 和 `overall_health`，我直接用 LLM 生成：

- **方案 A**：偏稳健/保守方向
- **方案 B**：偏进取/变革方向
- 每个方案附：策略说明、执行任务候选项、优先级

输出格式推老板微信。

---

## WeChat 推送

推送内容格式和操作方法详见 FULL_FLOW.md「WeChat 推送规范」。

关键约束：
- ⚠️ 强制约束 Agent 只转发，不分析
- delivery.to 用老板微信 Bot ID: `o9cq80-4ZTet7x8h6pGOsyDexBik@im.wechat`
- 老板用户名：杨卓，微信号：YZ2315766973

---

## 决策提交与任务下发

老板微信回复 A/B 后（在微信会话中）：

1. 微信会话的我收到回复
2. 构造 `POST /api/v1/decision/commit`（Executive 身份）
3. 后端自动创建任务并返回 task_ids

---

## 错误处理

| 异常 | 含义 | 处理方式 |
|------|------|---------|
| 409 Conflict | 重复提交 | 查询已有记录，跳过 |
| 403 Forbidden | 权限不足 | 检查 X-Role / X-User-Id |
| 422 Validation | 字段不合法 | 根据 error detail 修正 |
| 5xx | 后端故障 | 记录到 memory，下次重试 |
