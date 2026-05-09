# AutoMage-2 MVP 里程碑二《Dream 简版归并规则文档》

文档版本：v1.0.0
适用阶段：M2 Mock 闭环验证
生成日期：2026-05-06
Owner：杨卓
适用对象：Executive Agent、Dream Mock、Manager Agent、后端、老板侧前端、测试

---

## 1. 文档目标

本文档定义 AutoMage-2 MVP 里程碑二中 Dream 的简版归并规则，用于在不实现完整 Dream Run、复杂模型调度、长期记忆和生产级权限系统的前提下，先验证以下链路是否成立：

```text
Manager 汇总 / 风险 / 上推事项
→ Dream 清洗、过滤、归并
→ 生成组织级摘要
→ 识别需要老板确认的决策项
→ 生成 A/B 方案和推荐理由
→ 生成任务草案
→ 老板确认后转正式任务
```

M2 阶段的 Dream 不是完整智能决策引擎，而是一个可复现、可测试、可替换真实 API 的规则层。它的核心价值是把多个部门、多个风险、多个待确认事项整理成少量老板能直接处理的结构化决策卡片。

---

## 2. Dream 在 M2 中的位置

| 位置 | 说明 |
|---|---|
| 上游 | Manager 汇总、Staff 高风险日报、未完成任务、异常、历史决策 |
| 中间处理 | 清洗无效数据、归并同类事项、识别组织级风险、生成决策项 |
| 下游 | Executive 决策卡片、任务草案、老板确认、正式任务生成 |
| Mock 文件 | `mock_executive_decision_card_ab_options.json` |
| 运行脚本 | `run_mock_workflow.py` |
| 主要接口 | `POST /internal/dream/run`, `POST /api/v1/decision/commit`, `POST /api/v1/tasks` |
| 主要表 | `manager_reports`, `summaries`, `summary_source_links`, `decision_records`, `decision_logs`, `agent_decision_logs`, `tasks`, `task_queue`, `audit_logs` |

M2 阶段 Dream 以本地 JSON 和规则输出为主，不直接调用大模型、不直接写真实数据库。真实联调时由后端接口和数据库 Skill 接管读写。

---

## 3. 输入数据范围

### 3.1 必读输入

| 输入 | 来源 | 说明 |
|---|---|---|
| Manager 汇总 | `mock_manager_summary_normal.json`, `mock_manager_summary_need_executive.json` | Dream 的主输入，包含部门摘要、风险、阻塞和待老板决策事项 |
| Staff 高风险日报 | `mock_staff_report_high_risk.json` | 用于追溯风险来源和任务回流原因 |
| 未完成任务 | `mock_generated_tasks.json` 或真实 `tasks` 查询 | 判断是否存在多日未解决 / 影响主链路的任务 |
| 历史决策 | `decision_records` / Mock 历史字段 | 避免重复生成老板决策 |
| 当前上下文 | `org_id`, `summary_date`, `dag_run_id`, `run_date` | 保证归并结果可追溯到同一组织、同一日期 |

### 3.2 可选输入

| 输入 | 用途 | M2 处理方式 |
|---|---|---|
| `incidents` | 补充风险等级和处理状态 | 只读取与 Staff / Manager 来源相关的数据 |
| `audit_logs` | 判断是否已确认 / 已处理 | M2 可只保留引用，不强制分析 |
| 外部业务目标 | 判断影响范围 | M2 不强依赖，缺失时不硬编造 |
| 老板历史偏好 | 推荐方案参考 | M2 暂不实现 |

---

## 4. 运行触发规则

M2 简版 Dream 支持三种触发方式。

| 触发方式 | 触发条件 | M2 优先级 | 输出 |
|---|---|---:|---|
| 定时触发 | 每天早间读取上一日 Manager 汇总 | 高 | 老板决策卡片 / 无需决策摘要 |
| Manager 上推触发 | `need_executive_decision` 非空或存在 `critical` / `high` 风险 | 高 | 局部老板决策卡片 |
| 手动触发 | 测试或老板主动查询 | 中 | 当前窗口组织级摘要 |

M2 默认以 `summary_date = run_date` 作为窗口。后续版本可扩展为：昨日汇总、近 3 天风险、近 7 天未完成任务、近 7 天历史决策、当前外部目标。

---

## 5. 数据过滤规则

Dream 在归并前必须先过滤无效数据，避免把脏数据推给老板。

| 过滤对象 | 过滤规则 | 处理方式 |
|---|---|---|
| 草稿汇总 | `signature.confirm_status != confirmed` 且非高风险上推 | 不进入老板卡片 |
| 明显无效数据 | 缺少 `org_id`、`summary_date`、来源 ID | 写入校验问题，不参与归并 |
| 重复数据 | 同一 `source_record_id` / `source_summary_id` 重复出现 | 保留最新确认版本 |
| 权限不匹配数据 | 不属于当前 `org_id` 或超出 Executive 可读范围 | 丢弃并记录审计 |
| 已关闭低风险 | `severity = low` 且无复盘价值 | 不进入老板卡片 |
| 无来源风险 | 没有 Staff / Manager 来源证据 | 标记为“需补充信息”，不生成决策项 |
| 已处理决策 | 历史 `decision_records.status = confirmed/closed` 且无新增变化 | 不重复推送 |

如果某部门缺失汇总，Dream 不能默认该部门没有问题，应在 `business_summary` 或 `key_risks` 中标记“数据缺失”。

---

## 6. 归并对象定义

Dream 主要归并五类对象。

| 类型 | 来源字段 | 归并目标 |
|---|---|---|
| 风险 | `top_3_risks`, `issues_faced`, `incidents` | `key_risks` |
| 阻塞 | `blocked_items`, `task_progress.current_status = blocked` | 风险或任务调整建议 |
| 需老板决策事项 | `need_executive_decision` | `decision_items` |
| 任务草案 | Manager 调整建议、Executive 推荐方案 | `generated_tasks` |
| 数据缺口 / 接口缺口 | Staff / Manager / 后端日报中的阻塞说明 | 组织级风险或决策项 |

M2 不归并个人绩效排名、复杂组织诊断、长期趋势预测、行业化经营指标。

---

## 7. 同类事项归并规则

### 7.1 归并 Key

一个事项是否同类，优先按以下顺序判断：

1. `source_id` / `source_record_ids` / `source_summary_ids` 是否相同。
2. `related_task_ids` 是否相同。
3. `risk_title` / `issue_title` / `decision_title` 是否高度相似。
4. 是否影响同一个主链路节点：Staff 写入、Manager 汇总、Executive 决策、Task 下发、任务回流。
5. 是否指向同一个系统对象：API、数据库 Skill、Schema、决策表、任务表、审计日志。
6. 是否需要同一个责任人处理。

### 7.2 关键词归并

M2 可使用简单关键词规则，不引入复杂向量检索。

| 关键词组 | 归并类别 | 示例 |
|---|---|---|
| `API`, `接口`, `CRUD`, `调用样例`, `响应格式` | API 联调缺口 | Staff 写入接口未验证、Task 查询接口未验证 |
| `数据库 Skill`, `Skill`, `读写`, `落库` | 数据库 Skill 缺口 | Agent 不能通过 Skill 写 Staff 日报 |
| `staff_reports`, `work_records`, `字段映射` | Staff 落库口径缺口 | Staff 日报主表未冻结 |
| `manager_reports`, `summaries` | Manager 汇总落库缺口 | Manager 汇总主表未冻结 |
| `decision_records`, `decision_logs`, `summaries.meta` | 决策落库缺口 | 老板确认记录落表不清晰 |
| `task_queue`, `tasks`, `task_assignments` | 任务生成 / 分配缺口 | 任务草案和正式任务边界不清晰 |
| `审计`, `payload_hash`, `签名`, `确认` | 审计 / 签名缺口 | 老板确认未记录 payload_hash |
| `跨部门`, `资源`, `优先级`, `老板确认` | 需 Executive 决策 | 多团队优先级冲突 |

### 7.3 归并输出字段

归并后的事项至少包含：

| 字段 | 说明 |
|---|---|
| `merged_item_id` | 归并事项 ID |
| `title` | 归并后标题 |
| `description` | 归并后说明 |
| `severity` | 归并后风险等级 |
| `source_items` | 被归并的原始事项 |
| `source_record_ids` | Staff 来源 |
| `source_summary_ids` | Manager 来源 |
| `owner_user_id` | 建议负责人 |
| `need_executive_decision` | 是否需要老板确认 |
| `suggested_action` | 建议动作 |
| `dedup_reason` | 归并理由 |

---

## 8. 风险识别规则

### 8.1 风险等级

| 等级 | 判断条件 | 是否进入老板决策卡片 |
|---|---|---:|
| `low` | 不影响主链路、不跨部门、可由 Staff 自行处理 | 否 |
| `medium` | 影响局部联调或需要 Manager 协调，但不影响里程碑验收 | 一般否，进入 Manager 汇总即可 |
| `high` | 影响 Staff → Manager → Executive → Task 主链路，或影响 5.8 / 5.9 验收 | 是，若跨角色需上推 |
| `critical` | 阻断主链路，且当天不处理会导致里程碑失败或客户/交付风险 | 是，立即触发 |

### 8.2 风险评分

M2 可使用 0-100 简版评分。

| 维度 | 分值 | 说明 |
|---|---:|---|
| 是否阻塞主链路 | 30 | Staff 写入、Manager 读取、Executive 决策、Task 下发、任务回流任一阻塞 |
| 是否跨角色 / 跨模块 | 20 | 涉及后端、Agent、产品、前端两个以上角色 |
| 是否影响里程碑时间 | 20 | 影响 5.8 联调或 5.9 冻结 |
| 是否已有明确 owner | 10 | 无 owner 时风险更高 |
| 是否多日未解决 | 10 | 连续出现或历史任务未关闭 |
| 是否影响老板决策 | 10 | 老板无法确认或确认后无法生成任务 |

评分映射：

- `0-29`：low
- `30-59`：medium
- `60-84`：high
- `85-100`：critical

### 8.3 当前 Mock 中的典型风险

| 风险 | 等级 | 来源 | Dream 处理 |
|---|---|---|---|
| API / 数据库 Skill 未通过端到端验证 | high | Staff 高风险日报、Manager 上推汇总 | 生成老板决策项 |
| 真实库新增表与里程碑一契约存在差异 | medium | Staff 高风险日报、Manager 汇总 | 生成关键风险，但不一定需要老板决策 |
| Mock 与真实 API 字段映射未冻结 | medium | Manager 正常汇总 | 进入任务或调整建议，不打扰老板 |

---

## 9. 决策项生成规则

### 9.1 生成条件

满足任一条件即可生成 `decision_items`：

1. `Manager.need_executive_decision` 非空。
2. 存在 `high` 或 `critical` 风险，且需要跨角色协调。
3. 问题影响老板确认、任务生成或里程碑验收。
4. 存在资源优先级冲突，需要老板选择方案。
5. Manager 权限内无法处理。

不得生成决策项的情况：

1. 信息不足以形成 A/B 方案。
2. 只是普通工作进度同步。
3. 已有历史决策且无新增事实。
4. 低风险事项可由 Staff / Manager 自行处理。

### 9.2 决策项字段

每个决策项必须包含：

| 字段 | 必填 | 说明 |
|---|---:|---|
| `decision_id` | 是 | 决策项 ID |
| `decision_title` | 是 | 老板看到的决策标题 |
| `background` | 是 | 背景事实，不写空泛判断 |
| `decision_level` | 是 | M2 里通常为 `L3` |
| `risk_level` | 是 | 风险等级 |
| `options` | 是 | 至少 A / B 两个方案 |
| `recommended_option` | 是 | 推荐方案 |
| `reasoning_summary` | 是 | 推荐理由摘要 |
| `expected_impact` | 是 | 预期影响 |
| `source_summary_ids` | 是 | 来源 Manager 汇总 |
| `generated_task_drafts` | 是 | 确认后可生成的任务草案 |

### 9.3 A/B 方案要求

| 要求 | 说明 |
|---|---|
| 互斥 | A / B 应代表不同取舍，不能只是文字变体 |
| 可执行 | 方案确认后必须能生成任务 |
| 有代价 | 每个方案必须说明成本或缺点 |
| 可追踪 | 方案必须关联来源风险和负责人 |
| 推荐明确 | 必须给出推荐方案，不能只列选项 |

当前 Mock 中的核心决策：

- A：5.7 主链路优先，先修通 Staff 写入、Manager 查询、Task 查询最小 API / Skill。
- B：继续多线并行，API、Landing Page、新员工注册同步推进。
- 推荐：A。

---

## 10. 任务草案生成规则

### 10.1 任务草案与正式任务边界

| 阶段 | 数据形态 | 是否正式下发 | 推荐落库 |
|---|---|---:|---|
| Dream 生成 | `generated_task_drafts` | 否 | `task_queue` / `decision_records.payload` |
| 老板确认前 | 任务草案 | 否 | `task_queue` |
| 老板确认后 | `schema_v1_task` | 是 | `tasks`, `task_assignments`, `task_updates` |
| Staff 执行后 | 任务进展 / 结果 | 是 | `task_updates`, 下一轮 `work_record_items` |

M2 里 `mock_executive_decision_card_ab_options.json` 中的任务属于草案；`mock_generated_tasks.json` 中的任务属于老板确认后的正式任务。

### 10.2 任务字段要求

正式任务至少包含：

| 字段 | 说明 |
|---|---|
| `task_id` | 任务 ID |
| `task_title` | 任务标题 |
| `task_description` | 任务说明 |
| `source_type` | 来源类型，如 `executive_decision` |
| `source_decision_id` | 来源决策 |
| `source_summary_id` | 来源汇总 |
| `creator_user_id` | 创建人 / 决策人 |
| `assignee_user_id` | 负责人 |
| `priority` | 优先级 |
| `status` | 状态 |
| `due_at` | 截止时间 |
| `artifacts` | 需要交付的产出物 |
| `meta` | 扩展信息 |

### 10.3 当前 Mock 任务拆解规则

老板确认方案 A 后生成 3 个正式任务：

1. 后端任务：提供三条最小 API 调用样例。
2. Agent 任务：将本地 Mock Demo 替换为真实 API / 数据库 Skill 调用。
3. 架构 / 字段任务：根据真实数据库对齐报告回修 Mock 字段映射。

这三个任务分别对应后端、Agent、架构三个关键责任边界，能够直接支撑 5.8 / 5.9 联调。

---

## 11. 输出结构

M2 简版 Dream 输出应符合 `schema_v1_executive`，核心结构如下：

```json
{
  "schema_id": "schema_v1_executive",
  "schema_version": "1.0.0",
  "timestamp": "2026-05-06T21:30:00+08:00",
  "org_id": "org_automage_mvp",
  "executive_user_id": "user_executive_001",
  "executive_node_id": "executive_agent_boss_001",
  "summary_date": "2026-05-06",
  "business_summary": "组织级摘要",
  "key_risks": [],
  "decision_required": true,
  "decision_items": [],
  "recommended_option": "A",
  "reasoning_summary": "推荐理由摘要",
  "expected_impact": {},
  "generated_tasks": [],
  "source_summary_ids": [],
  "human_confirm_status": "pending"
}
```

如果没有需要老板确认的事项：

- `decision_required = false`
- `decision_items = []`
- `human_confirm_status = not_required`
- 只输出组织级摘要和普通风险提醒，不生成正式任务。

---

## 12. 与数据库表的关系

| Dream 输出 | M2 推荐表 | 说明 |
|---|---|---|
| 组织级摘要 | `summaries` | 可作为 Executive / Dream 组织级摘要 |
| 老板决策卡片 | `decision_records` | 决策主记录 |
| 决策确认 / 驳回 / 补充 | `decision_logs` | 记录人工确认动作 |
| Agent 自动推理日志 | `agent_decision_logs` | 记录 Dream / Executive Agent 生成过程 |
| 任务草案 | `task_queue` | 未确认前不进入正式任务 |
| 正式任务 | `tasks` | 老板确认后写入 |
| 任务负责人 | `task_assignments` | 多人或角色分配时使用 |
| 任务状态变化 | `task_updates` | Staff 执行反馈 |
| 来源追溯 | `summary_source_links` | Summary 与 Staff / Manager 来源记录关系 |
| 审计 | `audit_logs` | 提交、确认、生成任务等关键动作 |

M2 若后端暂未实现上述全部表的写入，可先通过 `meta` / `payload` 兼容，但必须在联调问题记录中标记。

---

## 13. 与 API 的关系

| API | Dream 角色 |
|---|---|
| `GET /api/v1/report/manager` | 读取 Manager 汇总 |
| `GET /api/v1/tasks` | 读取未完成任务和历史任务状态 |
| `GET /api/v1/incidents` | 读取未关闭风险 / 异常 |
| `POST /internal/dream/run` | 触发 Dream 简版归并 |
| `POST /api/v1/decision/commit` | 老板确认或驳回决策 |
| `POST /api/v1/tasks` | 老板确认后创建正式任务 |
| `PATCH /api/v1/tasks/{task_id}` | Staff 更新任务状态，结果进入下一轮日报 |

M2 本地 Mock 阶段可以不实际调用上述 API，但 Mock 文件必须保持和这些接口的输入输出形式接近，避免 M3 大面积重写。

---

## 14. 降级策略

| 场景 | 降级方式 | 输出 |
|---|---|---|
| Manager 汇总缺失 | 不生成老板决策，输出数据缺失提示 | `key_risks` 中标记 `data_missing` |
| 风险来源不完整 | 不生成决策项，生成补充信息请求 | `decision_required = false` 或 `need_more_info` |
| A/B 方案无法成立 | 只输出组织摘要和风险，不强推方案 | `decision_items = []` |
| 老板未确认 | 保留任务草案，不生成正式任务 | `human_confirm_status = pending` |
| 老板驳回 | 记录驳回原因，不生成任务 | `decision_logs` / Mock 状态 |
| Mock 校验失败 | 脚本返回 failed，定位具体文件和字段 | `run_mock_workflow.py` 输出错误 |

---

## 15. 人工确认规则

M2 中 Executive / Dream 不能绕过老板自动执行重大决策。

| 动作 | 是否需要老板确认 | 说明 |
|---|---:|---|
| 生成组织级摘要 | 否 | 可自动生成 |
| 标记风险 | 否 | 可自动生成 |
| 生成 A/B 决策建议 | 否 | 可自动生成，但只是建议 |
| 推荐方案 | 否 | 可自动推荐 |
| 生成任务草案 | 否 | 可随卡片展示 |
| 下发正式任务 | 是 | 必须老板确认后执行 |
| 调整主链路优先级 | 是 | 属于 L3 决策 |
| 跨部门资源调配 | 是 | 属于 L3 或 L4 决策 |

老板确认后必须记录：

- `confirmed_by`
- `confirmed_at`
- `confirmed_option`
- `human_confirm_status`
- `payload_hash` 或等价审计字段
- 生成的 `task_ids`

---

## 16. 测试用例

| 用例 ID | 输入 | 预期输出 | 是否 M2 必测 |
|---|---|---|---:|
| DREAM-001 | 正常 Manager 汇总 | `decision_required = false`，不生成老板决策 | 是 |
| DREAM-002 | 高风险 Manager 汇总 | 生成 Executive 决策卡片 | 是 |
| DREAM-003 | 同类 API / Skill 风险多次出现 | 归并为一个组织级风险 | 是 |
| DREAM-004 | 缺少来源 ID 的风险 | 不生成决策项，标记需补充信息 | 是 |
| DREAM-005 | 老板确认方案 A | 生成正式任务 | 是 |
| DREAM-006 | 老板未确认 | 只保留任务草案 | 是 |
| DREAM-007 | 已关闭低风险事项 | 不进入老板卡片 | 否 |
| DREAM-008 | 多部门上报同类决策表问题 | 合并成一个决策落库口径问题 | 后续 |

---

## 17. 当前 Mock 示例的归并过程

### 17.1 输入事实

Manager 上推事项：

- 数据库本体已可连接。
- API / 数据库 Skill 端到端链路未验证。
- 真实库表结构与里程碑一落库口径存在新增表差异。
- 若不优先处理，会影响 5.8 真实联调和 5.9 里程碑二冻结。

### 17.2 归并判断

上述问题被归并为两个组织级风险：

1. **真实 API / 数据库 Skill 未通过端到端验证**：高风险，需要老板确认优先级。
2. **数据库新增表与契约主落点需要冻结**：中风险，需要杨卓和数据库对齐 Agent 回修字段映射。

### 17.3 决策生成

Dream 生成老板决策项：

```text
5.7 是否优先冻结 API / 数据库 Skill 最小链路
```

方案：

- A：主链路优先。
- B：继续多线并行。

推荐：A。

理由：里程碑二验收核心是 Staff → Manager → Executive → Task 闭环，主链路 API / Skill 未通过会直接影响 5.8 和 5.9。

### 17.4 任务草案

确认方案 A 后生成：

1. 后端提供三条最小 API 调用样例。
2. Agent 替换真实 API / 数据库 Skill 调用。
3. 架构侧根据真实数据库对齐报告回修 Mock 字段映射。

---

## 18. MVP 暂不实现能力

M2 Dream 简版不实现以下能力：

1. 不做长期记忆检索。
2. 不做复杂向量聚类。
3. 不做跨周 / 跨月组织诊断。
4. 不做完整绩效排名。
5. 不直接读取未经授权的 Staff 原始明细。
6. 不接屏幕记忆。
7. 不调用生产 LLM 自动改写决策卡片。
8. 不实现复杂审批流。
9. 不做成本统计和多模型路由。
10. 不直接自动下发 L3 / L4 决策任务。

这些能力后续可通过 `dream_runs`、`decision_records`、`agent_decision_logs`、Policy Engine、行业 Schema、长期记忆和多通道消息 Adapter 扩展。

---

## 19. 后续扩展口

| 扩展方向 | M2 保留口 | 后续实现 |
|---|---|---|
| Dream Run 表 | `POST /internal/dream/run` 输出和 `mock_full_workflow_run.json` | 增加 `dream_runs` 表记录输入、输出、状态、耗时、成本 |
| 决策对象独立化 | `decision_records`, `decision_logs` | 替代 `summaries.meta` 中的临时决策存储 |
| 任务草案队列 | `task_queue` | 支持老板确认前的任务预览和编辑 |
| 审计增强 | `payload_hash`, `audit_logs` | 增加签名服务和不可抵赖记录 |
| 权限策略 | 当前硬编码角色边界 | 后续接 Policy Engine |
| 数据采集 | Staff 日报模板 | 后续接 IM 表单、文档上传、屏幕记忆、OA / ERP |
| 老板侧展示 | 决策卡片 JSON | 后续接 IM / Web / App Landing Page |

---

## 20. 验收标准

Dream 简版归并规则在 M2 中通过验收必须满足：

1. 能读取 Manager 正常汇总并判断无需老板决策。
2. 能读取 Manager 高风险汇总并生成老板决策卡片。
3. 能把多个同类风险归并为少量组织级风险。
4. 能生成 A/B 方案、推荐方案、理由和预期影响。
5. 能生成任务草案，但老板确认前不生成正式任务。
6. 老板确认后能转为 `schema_v1_task` 正式任务。
7. 任务能关联 `source_decision_id`、`source_summary_id` 和负责人。
8. 任务能进入下一轮 Staff 日报样例。
9. 所有结果能通过 `run_mock_workflow.py` 本地校验。
10. 所有字段能被后端、Agent 和数据库对齐 Agent 继续映射。

---

## 21. 推荐执行顺序

1. 读取 `mock_manager_summary_normal.json`，验证无需老板决策分支。
2. 读取 `mock_manager_summary_need_executive.json`，验证上推老板决策分支。
3. 生成或检查 `mock_executive_decision_card_ab_options.json`。
4. 模拟老板确认推荐方案 A。
5. 生成或检查 `mock_generated_tasks.json`。
6. 将任务写入 `mock_full_workflow_run.json` 的下一轮 Staff 回流样例。
7. 执行：

```bash
python run_mock_workflow.py --output-dir ./mock_runtime_output
```

8. 若通过，将 Mock 包交给数据库对齐 Agent 做真实库字段映射。
9. 若失败，优先修正 Manager 上推项、Executive 决策卡片和 Task Schema 三处字段。
