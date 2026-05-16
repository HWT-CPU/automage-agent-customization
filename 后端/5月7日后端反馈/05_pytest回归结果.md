# pytest 回归结果
日期：2026-05-07

## 本次执行说明

本轮已在当前本地 Python 环境中补装 `pytest`，并对项目现有测试文件进行了实际执行。

补装内容：

- `pytest 9.0.3`

说明：

- 之前“本机缺少 pytest 环境”的问题已解决
- 本轮结论不再只是基于真实接口手工回归，也已经有自动化测试回归支撑

## 实际执行结果

### 1. API 相关回归

执行：

- `python -m pytest tests\test_daily_report_api.py -q`

结果：

- `15 passed`

覆盖重点：

- `POST /api/v1/report/staff/import-markdown`
- `GET /api/v1/report/staff/{work_record_id}`
- `GET /api/v1/report/staff`
- `GET /api/v1/report/manager`
- `POST /api/v1/tasks`
- `PATCH /api/v1/tasks/{task_id}`
- 审计接口
- 基础鉴权与角色边界

### 2. Manager / Decision / Task 闭环回归

执行：

- `python -m pytest tests\test_manager_decision_task_flow.py -q`

结果：

- `8 passed`

覆盖重点：

- Manager 汇总提交
- Dream / Decision / Task 闭环
- Task 可见性与更新权限
- Manager 跨部门提交/建任务拦截
- Staff 越权查询与越权更新拦截
- Manager 汇总读取范围隔离

### 3. 幂等规则回归

执行：

- `python -m pytest tests\test_idempotency_flow.py -q`

结果：

- `7 passed`

覆盖重点：

- Staff 日报重复提交
- Staff 日报冲突提交
- Task 创建与更新幂等
- 统一 `409 Conflict` 返回体
- 中间件 `Idempotency-Key` 重放行为
- `request_id` 持久化可观测性

### 4. 日报解析回归

执行：

- `python -m pytest tests\test_staff_daily_report_parser.py -q`

结果：

- `3 passed`

### 5. 日报持久化回归

执行：

- `python -m pytest tests\test_staff_daily_report_persistence.py -q`

结果：

- `3 passed`

### 6. 日报渲染回归

执行：

- `python -m pytest tests\test_staff_daily_report_rendering.py -q`

结果：

- `1 passed`

## 汇总结果

本轮共执行：

1. `tests\test_daily_report_api.py`
2. `tests\test_manager_decision_task_flow.py`
3. `tests\test_idempotency_flow.py`
4. `tests\test_staff_daily_report_parser.py`
5. `tests\test_staff_daily_report_persistence.py`
6. `tests\test_staff_daily_report_rendering.py`

总结果：

- `34 passed`
- `0 failed`

## 本次额外说明

执行过程中出现了同一类 warning：

- `PytestCacheWarning`

原因：

- 当前工作目录下 `.pytest_cache` 创建权限受限

影响：

- 只影响 pytest 缓存写入
- 不影响测试执行结果
- 不影响本轮通过结论

## 当前可以对外使用的结论

截至 2026-05-07，当前后端不仅已经完成真实接口回归，也已经补齐 pytest 自动化回归。

因此现在可以同时给出两层结论：

1. 真实接口联调主链路已跑通
2. 现有核心后端测试已自动化通过

这意味着当前后端提交物已经具备：

1. 真实接口闭环验证
2. 自动化回归验证
3. RBAC 边界验证
4. 幂等行为验证
