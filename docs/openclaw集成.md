# Hermes / OpenClaw 完整深度集成方案

## 目标

本文档用于说明 AutoMage-2 后续如何从“初版 Agent 工程骨架”逐步升级到完整的 Hermes / OpenClaw 深度集成。

核心目标是：

```text
OpenClaw 负责员工入口、飞书渠道、事件接收和消息发送。
Hermes 负责 Agent Runtime、岗位 prompt、Skill 调用和 Schema 修正。
AutoMage-2 后端负责权限校验、数据写入、任务队列和事实存储。
```

最终链路应达到：

```text
员工在飞书 / IM 中操作
 ↓
OpenClaw 接收消息或卡片回调
 ↓
转换成 AutoMage-2 内部事件
 ↓
调用 Hermes 中对应的 Staff / Manager / Executive Agent
 ↓
Hermes 调用 Skill
 ↓
Skill 调 AutoMage-2 后端 API
 ↓
后端完成权限校验、Schema 校验、数据库写入
 ↓
结果再通过 OpenClaw / 飞书返回给用户
```

---

## 前提说明

完整 Hermes / OpenClaw 深度集成不建议一开始直接硬接。

更稳妥的方式是：

```text
先做可替换、可联调、可扩展的初版工程骨架，
再把其中的 Agent Runtime、Skill 注册、IM 入口、事件回调逐步替换成真实 Hermes / OpenClaw 实现。
```

这样做不会影响后续深度集成，前提是初版开发时遵守以下原则：

- 不自己写死 Agent Runtime。
- 不把飞书逻辑写进业务 Skill。
- 不把 API 地址、Token、用户信息硬编码。
- 不把 Schema 散落在各个函数中。
- 不只依赖 prompt 做权限控制。
- 不让 Hermes 和 OpenClaw 同时控制同一个 Cron。
- 所有未确认的 API、Schema、鉴权、Dream 输入输出，都要加清晰 TODO 注释。

---

## 1. 阶段一：确认 Hermes 真实运行规范

### 1.1 需要确认的内容

在真正深度集成 Hermes 之前，需要先确认 Hermes 官方运行规范。

需要确认：

- Hermes 官方项目版本。
- Agent 配置文件格式。
- `agents.md` 是否为官方识别格式，或是否需要转换成 Hermes 的其他配置格式。
- Skill 目录结构。
- Skill 注册方式。
- Skill 参数定义方式。
- Skill 返回格式。
- Skill 是否支持异步调用。
- Skill 是否支持配置注入。
- Skill 是否支持按用户 / 按 Agent 隔离。
- Hermes 的运行命令。
- Hermes 的环境变量配置方式。
- Hermes 是否支持多 Agent 实例。
- Hermes 是否支持每个员工一份 `user.md`。
- Hermes 如何加载长期记忆或上下文。

### 1.2 要完成的映射关系

需要把 AutoMage-2 初版中的结构：

```text
agents/
skills/
config/
schemas/
user.md
```

映射到 Hermes 官方要求。

例如：

```text
AutoMage-2 agents/staff/agents.md
 ↓
Hermes 官方 Agent 配置格式

AutoMage-2 skills/post_daily_report.py
 ↓
Hermes 官方 Skill / Tool 格式

AutoMage-2 user.md
 ↓
Hermes 用户上下文 / 配置注入方式
```

### 1.3 阶段一产出

- Hermes 版本确认。
- Hermes Agent 配置格式确认。
- Hermes Skill 注册方式确认。
- AutoMage-2 目录结构与 Hermes 目录结构映射表。
- 需要改造的文件列表。

---

## 2. 阶段二：把初版 Skill 改造成 Hermes Skill

### 2.1 改造原则

初版 Skill 应保持纯业务能力，不直接绑定 Hermes。

推荐结构是：

```text
业务函数：post_daily_report(data)
Hermes 包装器：hermes_post_daily_report_tool(args)
```

也就是说：

- 业务逻辑保持独立。
- Hermes 只负责调用包装器。
- 包装器负责参数转换和结果格式转换。
- 后端 API 调用仍然走统一 API Client。

这样后续如果 Hermes 的 Skill 格式变化，只需要改包装层，不需要重写业务逻辑。

### 2.2 需要改造成 Hermes Skill 的能力

Staff Agent 相关：

- `agent_init`
- `post_daily_report`
- `fetch_my_tasks`
- `check_auth_status`
- `schema_self_correct`

Manager Agent 相关：

- `analyze_team_reports`
- `generate_manager_schema`
- `delegate_task`
- `post_manager_report`

Executive Agent 相关：

- `dream_decision_engine`
- `broadcast_strategy`
- `commit_decision`

通用能力：

- `retry_with_backoff`
- `validate_schema`
- `load_user_profile`
- `load_agent_config`

### 2.3 需要保留的 TODO 注释

在 Skill 改造时，需要保留以下 TODO：

```text
TODO(熊锦文): 确认后端 API 请求字段、响应字段、错误码和鉴权方式。
TODO(杨卓): 确认 schema_v1_staff / schema_v1_manager 最终字段。
TODO(徐少洋): 确认 Dream 机制输入输出格式。
TODO(Hermes): 根据 Hermes 官方 Skill 注册方式调整 wrapper。
```

### 2.4 阶段二产出

- Hermes Skill wrapper。
- Skill 参数转换层。
- Skill 返回结果标准化。
- 统一错误处理。
- 统一重试逻辑。
- Schema 422 Self-correction 占位或初版实现。

---

## 3. 阶段三：确认 OpenClaw 真实插件 / Channel 机制

### 3.1 需要确认的内容

OpenClaw 是 AutoMage-2 中推荐承担“员工入口”和“IM 渠道”的部分。

在深度集成前，需要确认：

- OpenClaw 如何安装插件。
- OpenClaw 的 Channel 机制是什么。
- Feishu / Lark Channel 如何配置。
- 飞书消息事件格式是什么。
- 飞书卡片回调格式是什么。
- OpenClaw 如何区分私聊和群聊。
- OpenClaw 如何识别用户身份。
- OpenClaw 如何配置企业机器人凭证。
- OpenClaw 如何把消息转给外部 Agent。
- OpenClaw 是否能直接调用 Hermes。
- OpenClaw 是否需要通过中间服务调用 Hermes。
- 飞书互动卡片由 OpenClaw 发，还是由 AutoMage-2 自己通过飞书 API 发。

### 3.2 建议的适配层设计

OpenClaw 不应该直接写业务逻辑。

建议设计为：

```text
OpenClaw Feishu Channel
 ↓
OpenClaw Event Adapter
 ↓
AutoMage-2 Internal Event
 ↓
Hermes Agent Router
 ↓
Hermes Agent / Skill
```

内部事件可以先统一为：

```text
DAILY_REPORT_SUBMITTED
TASK_QUERY_REQUESTED
REMINDER_ACKED
TASK_COMPLETED
MANAGER_FEEDBACK_SUBMITTED
EXECUTIVE_DECISION_SELECTED
AUTH_FAILED
```

### 3.3 阶段三产出

- OpenClaw Feishu Channel 配置说明。
- OpenClaw 事件格式确认。
- AutoMage-2 内部事件格式。
- OpenClaw Event Adapter。
- 飞书用户身份与 AutoMage-2 `user_id` 映射方案。

---

## 4. 阶段四：打通 OpenClaw → Hermes → 后端 API

### 4.1 核心链路

完整集成的核心链路是：

```text
员工在飞书提交日报
 ↓
OpenClaw Feishu Channel 收到事件
 ↓
转换成内部事件 DAILY_REPORT_SUBMITTED
 ↓
调用 Hermes Staff Agent
 ↓
Hermes 根据 user.md 和 Staff 模板理解输入
 ↓
Hermes 调 post_daily_report Skill
 ↓
Skill 调 AutoMage-2 后端 API
 ↓
后端校验身份、权限和 Schema
 ↓
数据库写入日报
 ↓
结果返回 Hermes
 ↓
OpenClaw 发送确认消息给员工
```

### 4.2 Staff Agent 链路

Staff Agent 主要处理：

- 员工日报提交。
- 员工任务查询。
- 员工任务完成确认。
- 员工问题补充。
- 员工日报格式修正。

对应接口：

```text
POST /api/v1/agent/init
POST /api/v1/report/staff
GET  /api/v1/tasks
```

需要注释：

```text
TODO(熊锦文): 确认 Staff Agent 相关 API 字段和鉴权方式。
TODO(杨卓): 确认 Staff 日报 Schema 字段。
```

### 4.3 Manager Agent 链路

Manager Agent 主要处理：

- 读取下属 Staff 日报。
- 生成部门汇总。
- 识别风险。
- 下发权限内任务。
- 超权限问题上推。

对应接口：

```text
POST /api/v1/report/manager
GET  /api/v1/tasks
```

需要注释：

```text
TODO(熊锦文): 确认 Manager Agent 是否需要独立读取部门日报接口。
TODO(杨卓): 确认 Manager 汇总 Schema 字段。
```

### 4.4 Executive Agent 链路

Executive Agent 主要处理：

- 读取 Manager 汇总。
- 调用 Dream 机制。
- 生成 A/B 决策方案。
- 推送老板决策卡片。
- 老板确认后下发战略任务。

对应接口：

```text
POST /api/v1/decision/commit
GET  /api/v1/tasks
```

需要注释：

```text
TODO(徐少洋): 确认 Dream 机制输入输出格式。
TODO(熊锦文): 确认 decision/commit 请求体与 task_queue 写入规则。
```

### 4.5 阶段四产出

- OpenClaw → Hermes 调用通路。
- Hermes → Skill 调用通路。
- Skill → AutoMage-2 后端 API 通路。
- Staff 日报端到端链路。
- Manager 汇总端到端链路。
- Executive 决策端到端链路。

---

## 5. 阶段五：接入 Cron / 调度策略

### 5.1 Cron 主控原则

Cron 只能有一个主控，避免重复推送。

推荐原则：

```text
OpenClaw / 外部调度器负责触发。
Hermes 负责生成内容和调用 Skill。
后端负责记录状态和事实。
```

不建议：

```text
OpenClaw 发一次提醒，Hermes 又发一次提醒，后端 Cron 再发一次提醒。
```

这样会导致员工收到重复消息。

### 5.2 推荐调度表

```text
18:00 Staff Agent 日报提醒
20:00 Staff Agent 二次催填
21:00 Manager Agent 部门汇总
22:00 Manager Agent 信息不全预警（待确认）
Dream 触发 Executive Agent 决策方案
```

### 5.3 Cron 触发链路

18:00 日报提醒：

```text
Scheduler / OpenClaw
 ↓
send_daily_report_card
 ↓
飞书日报卡片
```

20:00 二次催填：

```text
Scheduler / OpenClaw
 ↓
后端查询未提交员工
 ↓
send_reminder_card
```

21:00 部门汇总：

```text
Scheduler / OpenClaw
 ↓
Manager Agent
 ↓
analyze_team_reports
 ↓
generate_manager_schema
 ↓
POST /api/v1/report/manager
```

Executive 决策：

```text
Dream Trigger
 ↓
Executive Agent
 ↓
dream_decision_engine
 ↓
send_decision_card
 ↓
老板点击
 ↓
POST /api/v1/decision/commit
```

### 5.4 阶段五产出

- Cron 主控方案。
- 定时任务配置。
- 重复推送防抖机制。
- 任务执行日志。
- 调度失败重试机制。

---

## 6. 阶段六：真实联调与替换 Mock

### 6.1 需要替换的 Mock

当其他同学的模块完成后，需要逐步替换初版中的 mock 和 TODO。

需要替换：

- 真实 API 地址。
- 真实 API 请求字段。
- 真实 API 响应字段。
- 真实鉴权 Token。
- 真实 `role_id` / `user_id` / `node_id` 权限规则。
- 真实 `schema_v1_staff`。
- 真实 `schema_v1_manager`。
- 真实 Dream 输入输出。
- 真实飞书 App ID / App Secret。
- 真实飞书事件订阅。
- 真实 OpenClaw Channel 配置。
- 真实 Hermes Skill 注册。

### 6.2 端到端测试场景

至少需要验证以下场景：

#### Staff Agent 场景

- 员工收到 18:00 日报卡片。
- 员工提交日报。
- 后端 Schema 校验通过。
- 数据写入员工日报表。
- 员工收到提交成功消息。
- 员工查询自己的任务。

#### Manager Agent 场景

- Manager Agent 21:00 自动读取部门日报。
- 生成部门汇总。
- 标记 top risks。
- 写入 Manager 汇总表。
- 推送部门汇总给中层。

#### Executive Agent 场景

- Executive Agent 读取 Manager 汇总。
- Dream 机制生成 A/B 方案。
- 老板收到决策卡片。
- 老板点击确认。
- 系统写入 `decision_logs`。
- 系统写入 `task_queue`。
- Staff Agent 能获取新任务。

#### 异常场景

- Schema 错误返回 422。
- Hermes 触发 Self-correction。
- API 超时触发指数退避。
- 鉴权失败通知管理员。
- 飞书回调失败重试。
- 重复点击按钮不重复下发任务。

### 6.3 阶段六产出

- 真实联调报告。
- 端到端演示流程。
- 异常测试记录。
- 部署配置说明。
- 真实运行的 Hermes / OpenClaw 集成版本。

---

## 7. 初版开发与完整深度集成的关系

四部分初版开发与完整深度集成不是冲突关系，而是前后关系。

```text
四部分初版开发 = 业务层和适配层准备
完整深度集成 = 把适配层接到真实 Hermes / OpenClaw Runtime
```

初版重点是：

- 目录结构。
- `user.md` 模板。
- Agent 职责边界。
- Skill 业务逻辑。
- API Client。
- Schema 草案。
- OpenClaw / Feishu 适配层占位。
- Mock 演示流程。

深度集成重点是：

- Hermes 真实 Agent 加载。
- Hermes 真实 Skill 注册。
- OpenClaw 真实 Feishu Channel。
- 真实事件回调。
- 真实鉴权。
- 真实数据库。
- 真实 Cron。
- 真实端到端联调。

---

## 8. 后续开发必须遵守的原则

为了保证后续能顺利深度集成，初版开发必须遵守以下原则。

### 8.1 不硬编码框架

不要自己写死一个假 Hermes Runtime。

应该只做：

- Agent 模板。
- Skill 业务函数。
- API 客户端。
- 适配层接口。

真实 Runtime 后续接 Hermes。

### 8.2 不混合飞书和业务逻辑

飞书 / OpenClaw 逻辑应放在：

```text
integrations/openclaw/
integrations/feishu/
```

业务 Skill 应放在：

```text
skills/
```

### 8.3 Skill 可独立调用

Skill 不应该关心调用来源。

同一个 Skill 应该能被：

- Hermes 调用。
- OpenClaw 事件调用。
- 测试脚本调用。
- 后续调度器调用。

### 8.4 API 统一封装

所有后端 API 都应统一走 API Client。

这样等熊锦文确认接口后，只需要集中修改。

### 8.5 Schema 集中管理

Schema 应集中放在：

```text
schemas/
```

这样等杨卓确认字段后，只需要集中调整。

### 8.6 Dream 边界单独隔离

Dream 输入输出未确认前，不要写死。

应保留：

```text
TODO(徐少洋): 确认 Dream 机制输入输出格式。
```

### 8.7 OpenClaw 只做入口

OpenClaw 不做业务决策。

推荐分工是：

```text
OpenClaw = 员工入口、飞书渠道、事件接收、消息发送
Hermes = Agent 大脑、岗位 prompt、Skill 调用、Schema 修正
后端 = 权限校验、数据事实源、任务队列
数据库 = 契约数据中心
```

---

## 9. 建议的完整集成路线图

推荐路线：

```text
第一步：完成初版工程骨架
第二步：完成 Skill 层和 API Client
第三步：完成三级 Agent 模板
第四步：完成 OpenClaw / Feishu 适配层占位
第五步：确认 Hermes 官方格式
第六步：把 Skill 包装成 Hermes Skill
第七步：确认 OpenClaw Feishu Channel
第八步：打通 OpenClaw → Hermes → 后端 API
第九步：接入 Cron 和真实飞书卡片
第十步：替换 Mock，完成真实端到端联调
```

---

## 10. 一句话总结

完整 Hermes / OpenClaw 深度集成的核心不是一开始就把所有框架硬接进去，而是先把 AutoMage-2 的业务能力设计成可适配结构：

```text
业务逻辑独立，Skill 独立，API 独立，Schema 独立，OpenClaw 只做入口，Hermes 只做 Agent Runtime。
```

这样后续接真实 Hermes / OpenClaw 时，不需要推翻初版，只需要逐步替换适配层和 Runtime 包装层。
