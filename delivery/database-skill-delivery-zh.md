# 数据库 Skill 交付稿

## 一、交付目标

本次交付的目标，是完成 AutoMage 场景下数据库 Skill 的设计与落地，明确 Agent 如何通过 API 接口完成数据库读写，并形成可复用、可说明、可演示的标准链路。

本次交付重点解决以下问题：

1. Agent 不是直接拼接 SQL 操作数据库，而是通过统一 API 或统一服务层访问数据库。
2. 不同业务动作对应清晰的数据表落点，便于后续排查、扩展和审计。
3. 日报类数据同时支持“Agent 快照存储”与“正式业务入库”两类模式。
4. 数据写入过程支持审计留痕，便于问题追踪和链路复盘。

## 二、整体设计说明

当前数据库 Skill 采用“两层访问模式”：

### 1. 标准 API 模式

这是推荐的正式链路，整体流程如下：

`Agent -> AutoMageApiClient -> FastAPI 路由 -> service 层 -> SQLAlchemy ORM -> PostgreSQL`

在这条链路中：

- Agent 通过客户端方法发起请求
- FastAPI 负责暴露统一接口
- service 层负责业务封装
- ORM 负责模型落库
- PostgreSQL 负责最终存储
- 审计日志会同步写入 `audit_logs`

### 2. 本地直连模式

在本地运行、调试或特定集成模式下，也支持如下路径：

`Agent -> SqlAlchemyAutoMageApiClient -> SQLAlchemy ORM -> PostgreSQL`

该模式不经过 HTTP 层，适合本地开发或嵌入式调用，但默认不具备完整的请求追踪与审计能力，因此正式环境更推荐标准 API 模式。

## 三、Agent 如何通过 API 读写数据库

### 1. Agent 初始化

当 Agent 启动并登记自身身份时，会调用：

- 接口：`POST /api/v1/agent/init`
- 客户端方法：`agent_init(identity)`

写入数据表：

- `agent_sessions`
- `audit_logs`

作用：

- 记录 Agent 的 `node_id`、`user_id`、`role`、`level`、`department_id` 等身份信息
- 为后续日报、决策、任务等动作建立上下文身份基础

### 2. 员工日报快照写入

当一线员工 Agent 提交日报快照时，会调用：

- 接口：`POST /api/v1/report/staff`
- 客户端方法：`post_staff_report(identity, report_payload)`

写入数据表：

- `staff_reports`
- `audit_logs`

作用：

- 保存一份 Agent 视角的员工日报 JSON 快照
- 适合流程联调、快速留档和上游汇总使用

### 3. 经理汇总快照写入

当经理 Agent 汇总团队日报后，会调用：

- 接口：`POST /api/v1/report/manager`
- 客户端方法：`post_manager_report(identity, report_payload)`

写入数据表：

- `manager_reports`
- `audit_logs`

作用：

- 保存一份经理视角的汇总结果
- 作为进一步决策或管理视角展示的数据来源

### 4. 决策写入与任务生成

当高层 Agent 提交最终决策时，会调用：

- 接口：`POST /api/v1/decision/commit`
- 客户端方法：`commit_decision(identity, decision_payload)`

写入数据表：

- `agent_decision_logs`
- `task_queue`（当请求中包含 `task_candidates` 时）
- `audit_logs`

作用：

- 保存最终决策结果
- 如果决策中包含待分发任务，则自动生成任务队列记录

### 5. 任务读取

当 Agent 需要读取待办任务时，会调用：

- 接口：`GET /api/v1/tasks`
- 客户端方法：`fetch_tasks(identity, status=None)`

读取数据表：

- `task_queue`

作用：

- 按 `user_id` 或 `status` 查询任务
- 支撑任务执行闭环

## 四、日报正式入库能力

本次交付中，日报能力不只停留在快照层，还补齐了正式业务入库链路。

### 1. Markdown 日报导入

接口：

- `POST /api/v1/report/staff/import-markdown`

作用：

- 将 Markdown 日报解析为结构化 JSON
- 将日报正式写入业务表

写入数据表：

- `form_templates`
- `work_records`
- `work_record_items`
- 可选 `staff_reports`
- `audit_logs`

这条链路的意义在于：

- `form_templates` 保存模板定义
- `work_records` 保存日报主记录
- `work_record_items` 保存日报字段明细
- `staff_reports` 可选保存旧格式快照，兼容原有链路

### 2. 正式日报读取与还原

接口：

- `GET /api/v1/report/staff/{work_record_id}?format=json`
- `GET /api/v1/report/staff/{work_record_id}?format=markdown`

读取数据表：

- `work_records`
- `work_record_items`

作用：

- 将数据库中的正式日报恢复为完整 JSON
- 或恢复为可直接查看的 Markdown 文本

这保证了日报入库后不是“只写不读”，而是具备完整回放能力。

## 五、日报能力的两种模式

为了避免理解混乱，本次交付明确区分了两种日报模式：

### 1. 快照模式

对应接口：

- `POST /api/v1/report/staff`

特点：

- 直接写入 `staff_reports`
- 数据结构灵活
- 更适合 Agent 工作流快照

### 2. 正式业务模式

对应接口：

- `POST /api/v1/report/staff/import-markdown`
- `GET /api/v1/report/staff/{work_record_id}`

特点：

- 写入 `work_records` 和 `work_record_items`
- 结构更标准
- 更适合正式业务数据沉淀与后续查询分析

## 六、通用 CRUD 能力

除核心业务接口外，系统还提供了通用 CRUD 接口，用于对部分资源表进行标准化读写。

支持资源：

- `agent_sessions`
- `staff_reports`
- `manager_reports`
- `agent_decision_logs`
- `task_queue`

主要接口：

- `GET /api/v1/crud/{resource}`
- `GET /api/v1/crud/{resource}/{record_id}`
- `POST /api/v1/crud/{resource}`
- `PUT /api/v1/crud/{resource}/{record_id}`
- `PATCH /api/v1/crud/{resource}/{record_id}`
- `DELETE /api/v1/crud/{resource}/{record_id}`

作用：

- 在不重复开发专用接口的前提下，提供统一资源读写能力
- 满足调试、运维、演示和轻量扩展场景

## 七、审计与可追踪性

本次交付特别补充了审计能力，确保数据库 Skill 不只是“能写入”，而且“能追踪”。

主要机制包括：

1. 核心写接口写入 `audit_logs`
2. 通用 CRUD 写接口写入 `audit_logs`
3. 请求级别支持 `X-Request-Id`
4. 审计日志中保存 `request_id`、动作类型、目标表、目标记录、摘要和请求载荷

这样做的价值在于：

- 可以追踪一次 Agent 调用最终改动了哪张表、哪条记录
- 可以定位某次写库的来源
- 可以支持联调、审计和问题复盘

## 八、真实链路验证结果

本次交付不仅完成了代码实现，也完成了真实日报链路验证。

以真实员工日报文件为例，已验证如下流程可用：

1. 中文 Markdown 日报通过 `markdown_base64` 方式提交
2. 服务端正确解析中文内容
3. 日报成功写入正式业务表
4. 可通过读取接口还原 JSON 与 Markdown

实际验证结果包括：

- 导入成功
- `submitted_by` 正确识别
- `report_date` 正确识别
- `task_count` 正确统计
- `need_support` 正确识别
- `risk_level` 正确还原

这说明数据库 Skill 已具备从“文本导入”到“结构化入库”再到“完整读取”的闭环能力。

## 九、本次交付产出

本次交付产出主要包括以下内容：

1. 数据库 Skill 中文说明文档
2. Agent 通过 API 读写数据库的链路说明
3. 接口到数据表映射说明
4. Markdown 日报导入接口
5. 正式日报 JSON/Markdown 读取接口
6. 中文日报 HTTP 编码稳定性修复方案
7. 真实日报导入与读取验证结果

## 十、结论

本次数据库 Skill 交付，已经完成了从 Agent 调用入口、API 路由、service 业务层、ORM 模型到 PostgreSQL 表落点的完整打通，并补齐了审计、正式日报入库、日报还原读取等关键能力。

当前系统已经具备以下特点：

- Agent 访问数据库路径清晰
- 接口和表之间映射明确
- 正式业务数据与 Agent 快照数据分层清楚
- 支持中文日报稳定导入
- 支持正式日报结构化回读
- 支持审计追踪和问题复盘

后续如果继续扩展，可进一步增加：

- 更多正式业务对象的标准化入库接口
- 更细粒度的权限控制
- 更完善的查询检索能力
- 面向管理端的聚合视图与分析接口
