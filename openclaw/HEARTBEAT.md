# Heartbeat 任务

## 每轮必做

### 1. 检查调度器待办任务

```python
# 查询待办任务
curl -s "http://localhost:8080/internal/scheduler/pending" \
  -H "Authorization: Bearer cA3dLkXdDinzl-5Q1w5zGQTPoxPthN9FkDdqOCFNizQ" \
  -H "X-Role: manager" \
  -H "X-User-Id: lijingli"

# 如果有任务：
# 1. POST /internal/scheduler/claim/{task_id} 认领
# 2. 按 instruction 执行
# 3. POST /internal/scheduler/complete/{task_id} 标记完成
# 4. 重复直到没有待办任务
```

### 2. 任务类型对照

| 类型 | 我的操作 |
|------|---------|
| `generate_manager_summary` | GET 日报 → LLM 分析 → POST manager 汇总 |
| `generate_dream_decision` | 我 LLM 生成 A/B → 推 cron → 转发微信 |
| `remind_missing_staff` | 标记完成（飞书提醒由 Auto01 通道处理） |

### 3. A/B 推送方式

用 cron job（isolated + deleteAfterRun）推送到 boss 微信：
- delivery: `{ mode: "announce", channel: "openclaw-weixin", to: "o9cq80-4ZTet7x8h6pGOsyDexBik@im.wechat" }`
- prompt 必须约束：只转发，不分析
- timeoutSeconds: 180

---

## 节流规则

- 如果 5 分钟内已经轮询过调度器且没有新任务 → 跳过本轮
- 轮询间隔不应少于 2 分钟
- 如果不在主会话中（如 WeChat/Feishu 会话）→ 不执行调度器轮询
