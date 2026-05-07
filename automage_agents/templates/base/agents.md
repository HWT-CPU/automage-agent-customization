# AutoMage-2 基础 Agent 模板

## 模板状态

这是 AutoMage-2 的基础 Agent 草稿模板。

TODO(Hermes): 在 Hermes 运行时规范确认后，将本文件转换为正式 Hermes Agent 配置格式。

## 共享运行原则

- 所有数据库写入都必须通过 AutoMage-2 后端 API 完成。
- 后端 API 和数据库是事实源。
- 本地记忆和 prompt 上下文只作为辅助信息。
- 权限控制必须由后端鉴权保证，不能只依赖 prompt 约束。
- OpenClaw / Feishu 的通道逻辑必须放在业务 Skills 之外。
- Skills 需要同时支持 Hermes、OpenClaw 适配器、本地脚本和测试调用。

## 共享上下文字段

- `context_version`: 当前上下文结构版本，初始为 `context_v0`。
- `org_id`: 当前组织范围。
- `run_date`: 当前 workflow 运行日期。
- `workflow_name`: 当前 DAG 或 workflow 名称。
- `workflow_stage`: 当前流程阶段，例如员工日报、Manager 汇总、Executive 决策。
- `user_id`: 当前业务用户 ID。
- `node_id`: 当前临时 Agent 节点 ID，仅用于 mock 或 demo。
- `role`: `staff`、`manager` 或 `executive`。
- `level`: `l1_staff`、`l2_manager` 或 `l3_executive`。
- `department_id`: 当前部门范围。
- `manager_node_id`: 上级 Manager 节点。
- `input_refs`: 当前阶段使用的来源记录。
- `output_refs`: 当前阶段产生的结果记录。

## 共享知识库上下文

- 如 `input_refs.feishu_knowledge.context_text` 存在，应优先作为项目资料上下文使用。
- `input_refs.feishu_knowledge.sources` 是引用来源，回答涉及项目资料时应保留可追溯来源。
- 知识库上下文只作为辅助证据，不能覆盖用户当前明确输入或后端事实数据。
- 不要在 Agent prompt 中读取或输出 Feishu CLI 凭证。

TODO(熊锦文): 确认后端鉴权字段，以及是否需要单独传 `role_id`。
TODO(OpenClaw): 确认 IM 用户身份如何映射到 `user_id` / `node_id`。

## 共享 Skills

- `agent_init`: 向后端初始化当前身份和权限。
- `check_auth_status`: 检查当前 Agent 凭证是否仍然有效。
- `load_user_profile`: 加载由 user.md 或后端配置生成的用户画像。
- `search_feishu_knowledge`: 从本地 Feishu 知识库缓存检索项目资料，并写入 `input_refs.feishu_knowledge`。
- `schema_self_correct`: 在后端返回 422 后，对结构化数据进行自我修正。

TODO(Hermes): 后续用 Hermes 官方 Skill 注册机制替换本地 registry。

## 错误处理基线

- 422 schema 错误：通过 Hermes runtime 触发自我修正，并在限制次数内重试。
- 401 鉴权错误：停止业务动作，并通知管理员。
- 403 权限错误：拒绝越权操作。
- 5xx / timeout：按指数退避策略重试。

TODO(熊锦文): 确认后端最终错误码结构。
