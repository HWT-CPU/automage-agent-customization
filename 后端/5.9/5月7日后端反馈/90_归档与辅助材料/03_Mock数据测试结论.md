# Mock 数据测试结论

测试时间：2026-05-07  
测试范围：

- `mock_staff_report_normal.json`
- `mock_staff_report_high_risk.json`
- `mock_manager_summary_normal.json`
- `mock_manager_summary_need_executive.json`
- `mock_executive_decision_card_ab_options.json`
- `mock_generated_tasks.json`
- `mock_full_workflow_run.json`

## 一、结论概览

这批 Mock 数据**内部业务结构基本自洽**，但**并不是都能直接作为当前后端接口请求体使用**。

可以分成两层结论：

1. 按自带 `run_mock_workflow.py` 校验：
   - 结果：通过
   - 说明：说明这批 Mock 在“本地 Mock 闭环验证脚本”的规则下是成立的

2. 按当前后端接口请求模型校验：
   - 结果：只有 `mock_generated_tasks.json` 可以直接通过
   - 其余 Staff / Manager / Executive Mock 都**不能直接 POST 到当前后端接口**

## 二、自带脚本测试结果

执行命令：

```powershell
python "D:\Code\A实习项目\里程碑二_杨卓_交付推进与联调v1.0.0\run_mock_workflow.py" --no-write
```

结果摘要：

```json
{
  "overall_status": "passed",
  "dag_run_id": "DAGRUN-20260506-AUTOMAGE-M2-001",
  "checks": {
    "staff_reports_count": 2,
    "has_high_risk_report": true,
    "manager_needs_executive": true,
    "executive_decision_required": true,
    "generated_tasks_count": 3,
    "next_round_seed_present": true
  }
}
```

### 但要注意

这个“通过”只代表：

- 最小必填字段检查通过
- 脚本定义的业务链路推演通过

**不代表严格 schema 校验一定通过**。  
原因是当前目录里没有看到以下 schema 文件：

- `schema_v1_staff.json`
- `schema_v1_manager.json`
- `schema_v1_executive.json`
- `schema_v1_task.json`

所以脚本大概率只执行了“最小字段校验”，严格 `jsonschema` 校验被跳过了。

## 三、按当前后端接口模型测试结果

### 1. 可直接通过的 Mock

- `mock_generated_tasks.json`

原因：

- 当前后端 `TaskCreateRequest` 只要求最外层有 `tasks` 数组
- 该 Mock 的顶层结构和 `POST /api/v1/tasks` 兼容

### 2. 不能直接通过的 Mock

- `mock_staff_report_normal.json`
- `mock_staff_report_high_risk.json`
- `mock_manager_summary_normal.json`
- `mock_manager_summary_need_executive.json`
- `mock_executive_decision_card_ab_options.json`

### 3. 失败原因

这些 Mock 的数据结构是“原始业务对象”，例如：

- Staff Mock 顶层就是日报内容本身
- Manager Mock 顶层就是汇总内容本身
- Executive Mock 顶层就是决策卡内容本身

但当前后端接口定义要求的是包装后的请求体：

- `POST /api/v1/report/staff` 需要：
  - `identity`
  - `report`

- `POST /api/v1/report/manager` 需要：
  - `identity`
  - `report`

- `POST /api/v1/decision/commit` 需要：
  - `identity`
  - `decision`

所以这些 Mock 不能直接发给接口，否则会报：

- `identity` 缺失
- `report` 缺失
- `decision` 缺失

## 四、这说明了什么

当前这批 Mock 数据**本身不是错数据**，而是：

- 更适合做“业务样例 / 中间层样例 / Agent 输出样例”
- 不适合直接当“最终 HTTP 请求体”

换句话说，问题不在于内容错，而在于**接口包装层没对齐**。

## 五、当前真实风险点

### 风险 1：全栈可能误以为 Mock 可以直接调接口

实际上不行。  
除了 `mock_generated_tasks.json`，其余几个都需要先包装。

### 风险 2：本地脚本通过，不等于接口联调通过

因为本地脚本验证的是“Mock 闭环逻辑”，不是“HTTP 契约完全一致”。

### 风险 3：严格 schema 文件缺失

如果后续要做真正严格验证，需要补齐：

- `schema_v1_staff.json`
- `schema_v1_manager.json`
- `schema_v1_executive.json`
- `schema_v1_task.json`

## 六、建议处理方式

建议后续按下面方式推进：

1. 把当前 Mock 定义成“业务内容样例”，不要定义成“可直接请求后端的最终报文”
2. 由前端或后端适配层增加包装：
   - Staff：`{ identity, report }`
   - Manager：`{ identity, report }`
   - Executive：`{ identity, decision }`
3. 继续保留 `mock_generated_tasks.json` 作为 `POST /api/v1/tasks` 的直接样例
4. 如果要做严格校验，补充 schema 文件，再跑一次 `jsonschema`

## 七、最终判断

### 可以说“没问题”的部分

- Mock 业务逻辑基本自洽
- 本地闭环验证脚本能跑通
- 任务 Mock 可以直接对接当前任务创建接口

### 不能说“完全没问题”的部分

- Staff / Manager / Executive 这几类 Mock 目前**不能直接作为当前后端接口请求体**
- 严格 schema 校验目前并未真正完成

## 八、一句话对外口径

这批 Mock 作为业务样例基本没问题，但除了任务数据外，其他几类 Mock 当前还不能直接拿来调用后端接口，需要补一层 `identity/report/decision` 的请求包装。
