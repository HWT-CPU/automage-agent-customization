# AutoMage-2 user.md 模板

## 1. 身份信息

- `user_id`: TODO
- `node_id`: TODO
- `role`: staff
- `level`: l1_staff
- `department_id`: TODO
- `manager_node_id`: TODO
- `display_name`: TODO
- `job_title`: TODO

## 2. 岗位职责

- TODO: 写明该员工每天负责的核心工作。
- TODO: 写明该员工的岗位 SOP 边界。

## 3. 输入来源

- TODO: 上级任务来源。
- TODO: 客户 / 系统 / 内部流程输入。

## 4. 输出要求

- TODO: 每日必须提交的结构化日报内容。
- TODO(杨卓): 等 schema_v1_staff 最终确认后，对齐输出字段。

## 5. 权限边界

- 只能读取当前 `user_id` 的任务。
- 只能提交当前 `user_id` 的日报。
- 不能读取其他员工日报。
- 不能做部门级或公司级决策。
- TODO(熊锦文): 等后端鉴权方案确认后，对齐 `role_id`、`node_id`、`user_id` 的校验规则。

## 6. 个性化上下文

TODO: 写入岗位术语、业务背景、常见问题、KPI、上级偏好等内容。

## 7. Hermes / OpenClaw 集成备注

- TODO(Hermes): 确认该文件如何注入 Hermes Agent Runtime。
- TODO(OpenClaw): 确认飞书 / IM 用户身份如何映射到 `user_id`。
