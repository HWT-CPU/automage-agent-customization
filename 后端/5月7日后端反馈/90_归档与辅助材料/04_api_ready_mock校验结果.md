# api_ready_mock 校验结果

以下文件已经按当前后端请求模型完成校验，并确认可作为当前接口请求体使用：

- `api_ready_staff_report_normal.json`：对应 `StaffReportRequest`
- `api_ready_staff_report_high_risk.json`：对应 `StaffReportRequest`
- `api_ready_manager_summary_normal.json`：对应 `ManagerReportRequest`
- `api_ready_manager_summary_need_executive.json`：对应 `ManagerReportRequest`
- `api_ready_executive_decision_card_ab_options.json`：对应 `DecisionCommitRequest`
- `api_ready_generated_tasks.json`：对应 `TaskCreateRequest`

## 说明

- Staff / Manager / Executive 原始 Mock 已补齐接口包装层
- Task Mock 原结构本身就可直接用于当前任务创建接口
- 这套 `api_ready_mock` 的目标是“可直接请求当前后端接口”，不是替代原始业务样例

## 当前目录建议用途

- 原始业务样例继续保留在里程碑目录中，用于业务讨论和 Mock 闭环验证
- `5月7日后端反馈/api_ready_mock` 中的文件用于接口联调、Swagger 调试、前端联调和后端自测
