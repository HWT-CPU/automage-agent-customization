# AutoMage-2 MVP 里程碑二《Mock 数据说明文档》

文档版本：v1.0.0  
适用阶段：M2 Mock 闭环验证  
生成日期：2026-05-06  
Owner：杨卓  
适用对象：后端、Agent 客制化、数据库 Skill、测试、老板侧产品/前端

---

## 1. 文档目标

本文档用于说明 AutoMage-2 MVP 里程碑二的本地 Mock 数据包。当前阶段不等待完整真实后端、不依赖完整 Agent、不强制写入真实数据库，先用标准 JSON 数据和本地脚本验证以下最小闭环：

```text
Staff 日报提交
→ Manager 汇总部门事实
→ Executive / Dream 生成老板决策卡片
→ 老板确认方案
→ 系统生成任务
→ Staff 查询任务
→ 任务结果进入下一轮日报样例
```

本 Mock 包服务于三类工作：

1. **Agent 编排验证**：验证 Staff / Manager / Executive 三类 Agent 的输入输出边界是否成立。
2. **后端接口对齐**：验证每一步 Mock 输出是否能对应到里程碑一接口和真实数据库表。
3. **里程碑三联调准备**：为后续替换真实 API、数据库 Skill、鉴权、审计和任务状态流转提供稳定样例。

---

## 2. 文件清单

| 文件名 | 类型 | 对应 Schema / 用途 | 是否 M2 必需 | 主要消费者 |
|---|---|---|---:|---|
| `mock_staff_report_normal.json` | Mock Staff 日报 | `schema_v1_staff` | 是 | Staff Agent、Manager Agent、后端 `/report/staff` |
| `mock_staff_report_high_risk.json` | Mock Staff 高风险日报 | `schema_v1_staff` + Incident 输入 | 是 | Manager Agent、Dream、后端 `/report/staff`、`/incidents` |
| `mock_manager_summary_normal.json` | Mock Manager 正常汇总 | `schema_v1_manager` | 是 | Executive Agent、后端 `/report/manager` |
| `mock_manager_summary_need_executive.json` | Mock Manager 上推汇总 | `schema_v1_manager` | 是 | Executive / Dream、老板决策卡片 |
| `mock_executive_decision_card_ab_options.json` | Mock 老板决策卡片 | `schema_v1_executive` | 是 | Executive Agent、老板侧前端、`/decision/commit` |
| `mock_generated_tasks.json` | Mock 任务生成结果 | `schema_v1_task[]` | 是 | Task API、Staff Agent、Manager Agent |
| `mock_full_workflow_run.json` | Mock 全链路运行记录 | `mock_v1_full_workflow_run` | 是 | 测试、验收、联调排查 |
| `run_mock_workflow.py` | 本地闭环验证脚本 | 读取上述 JSON 并校验流程 | 是 | 杨卓、胡文涛、熊锦文、测试 |

---

## 3. 统一上下文与测试 ID

本 Mock 包采用统一测试上下文，后续可直接替换为真实数据库 Seed 数据或联调测试账号。

| 字段 | Mock 值 | 说明 |
|---|---|---|
| `org_id` | `org_automage_mvp` | AutoMage-2 MVP 试点组织 |
| `department_id` / `dept_id` | `dept_mvp_core` | MVP 核心项目组 |
| `run_date` / `record_date` / `summary_date` | `2026-05-06` | 本轮 Mock 运行日期 |
| `dag_run_id` | `DAGRUN-20260506-AUTOMAGE-M2-001` | 全链路 Mock 运行 ID |
| Staff 正常样例用户 | `user_agent_001` | Agent 客制化负责人样例 |
| Staff 高风险样例用户 | `user_backend_001` | 后端 / 数据库负责人样例 |
| Manager 用户 | `user_manager_001` | 项目 Manager / 汇总节点样例 |
| Executive 用户 | `user_executive_001` | 老板 / 高管决策节点样例 |
| Staff 正常节点 | `staff_agent_huwentao_001` | Staff Agent 样例节点 |
| Staff 高风险节点 | `staff_agent_xiongjinwen_001` | Staff Agent 样例节点 |
| Manager 节点 | `manager_agent_mvp_001` | Manager Agent 样例节点 |
| Executive 节点 | `executive_agent_boss_001` | Executive Agent 样例节点 |

统一 ID 的目的不是模拟真实生产 ID，而是保证本地脚本、数据库字段映射、API 对齐表和 Agent 编排在同一套上下文里验证。

---

## 4. Mock 数据与 DAG 节点关系

| 阶段 | DAG 含义 | 输入文件 | 输出文件 | 对应接口 | 主要读表 | 主要写表 |
|---|---|---|---|---|---|---|
| Staff 正常日报 | 员工提交日报，记录正常进展 | 员工日报模板 / 自然语言日报 | `mock_staff_report_normal.json` | `POST /api/v1/report/staff` | `tasks` | `staff_reports`, `work_records`, `work_record_items`, `artifacts`, `audit_logs` |
| Staff 高风险日报 | 员工提交日报并暴露阻塞 / 风险 | 员工日报模板 / 自然语言日报 | `mock_staff_report_high_risk.json` | `POST /api/v1/report/staff`, `POST /api/v1/incidents` | `tasks` | `staff_reports`, `work_records`, `work_record_items`, `incidents`, `artifacts`, `audit_logs` |
| Manager 正常汇总 | 汇总正常 Staff 日报 | `mock_staff_report_normal.json` | `mock_manager_summary_normal.json` | `POST /api/v1/report/manager` | `staff_reports`, `work_records`, `work_record_items`, `tasks`, `incidents` | `manager_reports`, `summaries`, `summary_source_links`, `audit_logs` |
| Manager 上推汇总 | 汇总高风险日报并生成上推事项 | `mock_staff_report_high_risk.json` | `mock_manager_summary_need_executive.json` | `POST /api/v1/report/manager` | `staff_reports`, `work_records`, `incidents`, `tasks` | `manager_reports`, `summaries`, `summary_source_links`, `incidents`, `audit_logs` |
| Executive / Dream 决策 | 读取部门汇总，生成 A/B 方案 | `mock_manager_summary_need_executive.json` | `mock_executive_decision_card_ab_options.json` | `POST /internal/dream/run`, `POST /api/v1/decision/commit` | `manager_reports`, `summaries`, `incidents`, `tasks`, `decision_records` | `decision_records`, `decision_logs`, `agent_decision_logs`, `summaries`, `audit_logs` |
| 任务生成 | 老板确认后生成正式任务 | `mock_executive_decision_card_ab_options.json` | `mock_generated_tasks.json` | `POST /api/v1/tasks` | `decision_records`, `decision_logs`, `summaries` | `tasks`, `task_queue`, `task_assignments`, `task_updates`, `audit_logs` |
| 下一轮回流 | 任务进入下一轮 Staff 日报 | `mock_generated_tasks.json` | `mock_full_workflow_run.json` 中 `next_round_staff_report_seed` | `GET /api/v1/tasks`, `PATCH /api/v1/tasks/{task_id}` | `tasks`, `task_assignments`, `task_updates` | `work_records`, `work_record_items`, `staff_reports`, `audit_logs` |

---

## 5. 文件说明

### 5.1 `mock_staff_report_normal.json`

用途：模拟 Staff Agent 在正常工作日结束后生成的标准日报结构。

核心内容：

- 已完成 Agent prompt 第一版落地。
- 已完成 `context_v0` 接入本地 Mock Demo。
- 已跑通本地 Mock Demo 主链路。
- 当前无高风险阻塞，但需要继续替换真实 API / 数据库 Skill。

关键字段：

| 字段 | 说明 | 后续落库建议 |
|---|---|---|
| `schema_id` | 固定为 `schema_v1_staff` | `staff_reports.schema_id` / `work_records.meta` |
| `task_progress` | 今日任务进展 | `task_updates` 或 `work_record_items` |
| `work_progress` | 今日完成事项 | `work_record_items` |
| `issues_faced` | 问题与阻塞 | `work_record_items`，高风险可转 `incidents` |
| `need_support` / `support_detail` | 是否需要支持及支持内容 | `work_record_items` / `incidents` |
| `next_day_plan` | 明日计划 | `work_record_items`，后续可转任务 |
| `artifacts` | 产出物 | `artifacts` / `artifact_links` |
| `related_task_ids` | 关联任务 | `tasks` / `task_updates` 反查 |
| `signature` | 员工确认 | `audit_logs` / 后续签名表 |

验收重点：正常日报必须能被 Manager 读取，并生成不需要老板决策的部门汇总。

### 5.2 `mock_staff_report_high_risk.json`

用途：模拟 Staff Agent 提交包含主链路阻塞的高风险日报。

核心内容：

- 数据库可连接，但 API / 数据库 Skill 端到端链路未验证。
- 真实库出现 `staff_reports`、`manager_reports`、`decision_records`、`task_queue` 等新增表，需要和里程碑一设计表对齐。
- 该日报会触发 Manager 汇总中的 `top_3_risks` 和 `need_executive_decision`。

关键规则：

1. `risk_level = high` 时，Manager 必须读取并判断是否上推。
2. `issues_faced[].is_blocking = true` 时，不能被当作普通备注处理。
3. 若问题影响 Staff → Manager → Executive → Task 主链路，应进入 Manager 汇总的 `top_3_risks`。
4. 若问题跨后端、Agent、产品优先级，应生成 `need_executive_decision`。

### 5.3 `mock_manager_summary_normal.json`

用途：模拟 Manager Agent 对正常 Staff 日报的部门汇总。

核心内容：

- 部门整体健康度为正常或良好。
- 有中等风险提醒，但不需要老板决策。
- Manager 可在 L2 权限内处理下一步调整。

关键字段：

| 字段 | 说明 |
|---|---|
| `staff_report_count` | 读取 Staff 日报数量 |
| `missing_report_count` | 缺失日报数量 |
| `overall_health` | 部门整体健康度 |
| `aggregated_summary` | 部门综合进展摘要 |
| `top_3_risks` | 部门三大风险 |
| `highlight_staff` | 表现突出员工 |
| `manager_decisions` | Manager 权限内已处理事项 |
| `need_executive_decision` | 需要老板确认的事项；本文件为空 |
| `source_record_ids` | 来源 Staff 日报 ID |

验收重点：该文件应证明“不是所有 Manager 汇总都必须上推老板”，避免 Executive 决策层过载。

### 5.4 `mock_manager_summary_need_executive.json`

用途：模拟 Manager Agent 对高风险 Staff 日报的汇总，并生成老板决策候选项。

核心内容：

- 部门存在影响里程碑三真实联调的主链路风险。
- 需要老板确认 5.7 是否优先处理 API / 数据库 Skill 最小链路。
- 生成结构化 `need_executive_decision`，包含 A/B 方案、推荐方案、影响说明和来源记录。

关键规则：

1. `need_executive_decision` 中的 `option_a`、`option_b` 必须是对象，不使用纯字符串。
2. `expected_impact` 必须结构化，便于 Executive / Dream 继续生成决策卡片。
3. `source_record_ids` 必须追溯到 Staff 日报。
4. Manager 只生成候选项，不代表老板自动确认。

### 5.5 `mock_executive_decision_card_ab_options.json`

用途：模拟 Executive / Dream 读取 Manager 上推事项后生成的老板决策卡片。

核心内容：

- 公司级摘要：里程碑二 Mock 闭环具备交付基础，但真实 API / Skill 最小链路尚未验证。
- 关键风险：真实 API / 数据库 Skill 未通过端到端验证；新增数据表与里程碑一契约需要对齐。
- 决策项：是否将 5.7 最高优先级调整为 API / 数据库 Skill 最小链路验证。
- A/B 方案：主链路优先 vs 继续多线并行。
- 推荐方案：A。
- 任务草案：老板确认 A 后生成后端、Agent、架构三类任务。

验收重点：决策卡片必须能直接给老板侧前端 / IM 呈现，且能在老板确认后转化为正式任务。

### 5.6 `mock_generated_tasks.json`

用途：模拟老板确认方案 A 后生成的正式任务对象。

当前任务数量：`3` 个。

任务列表：

| 任务 ID | 负责人 | 优先级 | 截止时间 | 任务标题 |
|---|---|---|---|---|
| `TASK-20260507-BACKEND-001` | `user_backend_001` | `critical` | `2026-05-07T12:00:00+08:00` | 提供 Staff 写入 / Manager 查询 / Task 查询三条最小 API 调用样例 |
| `TASK-20260507-AGENT-001` | `user_agent_001` | `high` | `2026-05-07T20:00:00+08:00` | 将本地 Mock Demo 替换为真实 API / Skill 调用 |
| `TASK-20260507-ARCH-001` | `user_architect_001` | `high` | `2026-05-07T18:00:00+08:00` | 输出真实数据库与 Mock 字段映射差异清单 |


关键规则：

1. 正式任务必须有 `source_decision_id`，可追溯到老板确认。
2. 正式任务必须有 `source_summary_id`，可追溯到 Manager 汇总。
3. 正式任务必须有 `assignee_user_id` 或明确的承接角色。
4. 正式任务必须有 `priority`、`status`、`due_at`。
5. 正式任务进入 Staff 下一轮日报时，应作为 `task_progress` 的输入。

### 5.7 `mock_full_workflow_run.json`

用途：记录一次完整 Mock Workflow 的执行计划、步骤、状态和下一轮 Staff 回流种子数据。

验收字段：

| 字段 | 说明 |
|---|---|
| `dag_run_id` | 本次 Mock DAG 运行 ID |
| `input_files` | 本次运行涉及的所有 Mock 文件 |
| `steps` | Staff、Manager、Executive、Task 各阶段执行步骤 |
| `acceptance_checks` | 本地验收检查项 |
| `next_round_staff_report_seed` | 下一轮 Staff 日报回流样例 |
| `known_gaps_for_real_api` | 切换真实 API 前已知缺口 |

验收重点：该文件不是业务数据表，而是测试运行记录，用于证明本地 Mock 数据可以串成闭环。

### 5.8 `run_mock_workflow.py`

用途：本地读取 Mock JSON，进行结构校验、闭环检查，并输出运行结果。

执行方式：

```bash
cd <mock 文件所在目录>
python run_mock_workflow.py --output-dir ./mock_runtime_output
```

可选：只校验不写输出文件。

```bash
python run_mock_workflow.py --no-write
```

脚本输出：

- `overall_status`：整体是否通过。
- `dag_run_id`：本轮 DAG 运行 ID。
- `checks`：核心验收检查。
- `generated_task_ids`：老板确认后生成的任务 ID。
- `output_file`：运行结果文件路径。

当前本地验证结果：

```json
{validation}
```

---

## 6. 本地验收标准

里程碑二本地 Mock 包通过验收必须满足以下条件：

| 验收项 | 标准 |
|---|---|
| Staff 日报 | 至少包含正常样例和高风险样例，均符合 `schema_v1_staff` |
| Manager 汇总 | 至少包含正常汇总和需上推老板汇总，均符合 `schema_v1_manager` |
| Executive 决策 | 决策卡片包含 A/B 方案、推荐方案、理由、影响、任务草案 |
| Task 生成 | 老板确认后可生成正式任务数组，任务符合 `schema_v1_task` |
| 全链路记录 | `mock_full_workflow_run.json` 能串联 Staff → Manager → Executive → Task |
| 任务回流 | 下一轮 Staff 日报样例能引用已生成任务结果 |
| 接口映射 | 每一步都能对应到至少一个核心接口 |
| 表映射 | 每一步都能对应到真实数据库中的主表或兼容表 |
| 脚本验证 | `run_mock_workflow.py` 可本地通过 |

---

## 7. 与真实数据库的对应关系

当前真实数据库中已有与 Mock 闭环相关的表：

| 业务对象 | 里程碑一主落点 | 真实库新增 / 可用表 | M2 使用建议 |
|---|---|---|---|
| Staff 日报 | `work_records`, `work_record_items` | `staff_reports` | M2 可将 `staff_reports` 作为聚合表，`work_records` / `work_record_items` 保留字段级事实源 |
| Manager 汇总 | `summaries`, `summary_source_links` | `manager_reports` | M2 可将 `manager_reports` 作为 Manager 汇总主表，`summaries` 作为统一汇总视图或兼容表 |
| Executive 决策 | `summaries.meta` | `decision_records`, `decision_logs`, `agent_decision_logs` | M2 建议使用 `decision_records` 存决策主记录，`decision_logs` 存确认和变更日志 |
| 任务 | `tasks`, `task_assignments`, `task_updates` | `task_queue` | M2 建议 `task_queue` 存任务草案 / 队列，`tasks` 存正式任务 |
| 异常 | `incidents`, `incident_updates` | 同名表 | 高风险 Staff 日报可转异常 |
| 审计 | `audit_logs` | 同名表 | 关键提交、确认、生成任务动作均写审计 |
| Agent 初始化 | 暂缓拆分 | `agent_profiles`, `agent_sessions`, `external_identities` | 支撑 `/api/v1/agent/init`、新员工节点注册和飞书 Gateway 路由 |

---

## 8. API 对齐口径

| 接口 | Mock 输入 | Mock 输出 | 说明 |
|---|---|---|---|
| `POST /api/v1/agent/init` | 统一 context / 用户身份 | Agent 初始化上下文 | M2 可用 mock context 代替，真实联调时写 `agent_profiles` / `agent_sessions` |
| `POST /api/v1/report/staff` | `mock_staff_report_normal.json`, `mock_staff_report_high_risk.json` | Staff 记录 ID | 写 Staff 日报和字段明细 |
| `GET /api/v1/report/staff` | `org_id`, `department_id`, `record_date` | Staff 报告集合 | Manager 汇总读取入口 |
| `POST /api/v1/report/manager` | `mock_manager_summary_normal.json`, `mock_manager_summary_need_executive.json` | Manager Summary ID | 写部门汇总和来源追溯 |
| `GET /api/v1/report/manager` | `org_id`, `summary_date` | Manager 汇总集合 | Executive / Dream 读取入口 |
| `POST /internal/dream/run` | Manager 汇总、任务、风险、历史决策 | Executive 决策卡片 | M2 本地用 `mock_executive_decision_card_ab_options.json` 代替 |
| `POST /api/v1/decision/commit` | 决策卡片确认结果 | 决策记录 / 任务草案确认结果 | 老板确认后触发任务生成 |
| `POST /api/v1/tasks` | `mock_generated_tasks.json` | 任务 ID 集合 | 写正式任务和分配关系 |
| `GET /api/v1/tasks` | `assignee_user_id`, `status` | Staff 本人任务列表 | Staff 下一轮日报读取入口 |
| `PATCH /api/v1/tasks/{{task_id}}` | 任务状态更新 | 更新后的任务状态 | 任务结果回流入口 |

---

## 9. Agent 使用方式

### 9.1 Staff Agent

输入：员工自然语言日报、Staff 日报模板、本人任务列表、`context_v0`。  
输出：`schema_v1_staff`，对应本包中的 `mock_staff_report_normal.json` 或 `mock_staff_report_high_risk.json`。

必须遵守：

1. 只能读写本人日报、本人任务、本人产出物。
2. 不得读取其他 Staff 原始日报。
3. 发现阻塞时必须写入结构化 `issues_faced` 和 `need_support`。
4. 任务执行结果必须进入 `task_progress`。
5. 提交前必须有人类确认或签名字段。

### 9.2 Manager Agent

输入：本部门 Staff 日报集合、任务状态、异常、部门上下文。  
输出：`schema_v1_manager`，对应 `mock_manager_summary_normal.json` 或 `mock_manager_summary_need_executive.json`。

必须遵守：

1. 只能读取本部门 Staff 数据。
2. 不复制 Staff 原文，要提炼事实、风险、阻塞和待确认事项。
3. 权限内事项形成 `manager_decisions`。
4. 超权限事项形成 `need_executive_decision`。
5. 所有风险必须保留来源记录 ID。

### 9.3 Executive / Dream

输入：Manager 汇总、组织级风险、未完成任务、历史决策。  
输出：`schema_v1_executive`，对应 `mock_executive_decision_card_ab_options.json`。

必须遵守：

1. 默认读取汇总，不默认展开全部个人明细。
2. 只向老板推送需要 L3 确认的问题。
3. 每个决策项必须有 A/B 方案、推荐方案、理由和影响。
4. 老板确认前只能生成任务草案，不能直接下发正式任务。
5. 老板确认后再生成 `schema_v1_task` 正式任务。

---

## 10. 已知差异与处理策略

| 差异 | 当前处理 | 是否阻塞 M2 | 是否需要后续回修 |
|---|---|---:|---:|
| 真实库存在 `staff_reports`，而里程碑一主设计为 `work_records` | Mock 同时标注两类表，后续由数据库对齐报告确定主表 | 否 | 是 |
| 真实库存在 `manager_reports`，而里程碑一主设计为 `summaries` | Mock 同时标注 `manager_reports` 和 `summaries` | 否 | 是 |
| 真实库存在 `decision_records` / `decision_logs` | Mock 建议 Executive 决策主落点迁移到决策表 | 否 | 是 |
| 真实库存在 `task_queue` | Mock 建议任务草案进入 `task_queue`，正式任务进入 `tasks` | 否 | 是 |
| 数字签名未完整实现 | Mock 保留 `signature` / `payload_hash` 字段 | 否 | 是 |
| 完整 RBAC 未实现 | Mock 只验证角色边界，不做真实鉴权 | 否 | 是 |
| 完整 Dream Run 表未实现 | M2 使用 `mock_executive_decision_card_ab_options.json` 代表 Dream 输出 | 否 | 是 |

---

## 11. 交付边界

### M2 必做

1. 本地 JSON 闭环跑通。
2. 每一步输入输出都是标准 JSON。
3. 每一步能对应到后端接口和数据库表。
4. 任务结果能进入下一轮日报样例。
5. Mock 文件字段尽量采用正式 Schema 字段名。
6. Mock 脚本能生成可复查运行结果。

### M2 不做

1. 不强制接入真实 IM。
2. 不强制完成真实登录鉴权。
3. 不强制完成完整数据库写入。
4. 不实现完整数字签名服务。
5. 不实现复杂权限矩阵。
6. 不实现完整 Dream Run 表、成本统计、Prompt 调度和模型调用。
7. 不接屏幕记忆、OA / ERP、飞书多租户 Gateway 的完整生产能力。

---

## 12. 下一步使用建议

1. 将本 Mock 包交给数据库对齐 Agent，生成真实数据库字段映射和差异报告。
2. 根据真实数据库报告回修 `Mock 字段 → 表字段` 映射。
3. 胡文涛用本 Mock 包替换当前 demo 中的散装样例数据。
4. 熊锦文按本 Mock 包优先实现三条真实 API / Skill 最小链路：
   - `POST /api/v1/report/staff`
   - `GET /api/v1/report/staff`
   - `GET /api/v1/tasks`
5. 5.8 前将 Manager 汇总、Executive 决策、任务生成接入真实 API。
6. 5.9 冻结 M2 Mock 包、脚本、问题记录和进入 M3 的字段差异清单。

---

## 13. 最终验收命令

```bash
cd <mock 文件目录>
python run_mock_workflow.py --output-dir ./mock_runtime_output
cat ./mock_runtime_output/mock_workflow_runtime_result.json
```

通过条件：

```json
{
  "overall_status": "passed"
}
```

若未通过，优先检查：

1. 是否缺少 Mock 文件。
2. JSON 是否语法错误。
3. `schema_id` 是否匹配。
4. Manager 上推项中的 `option_a` / `option_b` 是否为对象。
5. Executive 决策卡片是否包含 `decision_items` 和 `generated_tasks`。
6. `mock_generated_tasks.json` 中每个任务是否包含 `task_id`、`source_decision_id`、`assignee_user_id`、`priority`、`status`、`due_at`。
7. `mock_full_workflow_run.json` 是否包含下一轮 Staff 回流种子数据。
