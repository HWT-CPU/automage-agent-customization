# Staff 日报模板落库方案

## 目标
这份文档把 `AutoMage_2_Staff日报模板_v1.0.0` 整理成一套可落库、可检索、可兼容现有接口的字段方案。

推荐目标不是只把整份 Markdown 塞进一个 JSON 字段，而是采用下面的混合存储：

1. `form_templates`
   保存模板定义和 schema 版本。
2. `work_records`
   保存一条日报主记录。
3. `work_record_items`
   保存日报的分区内容和结构化字段。
4. `staff_reports`
   可选保留一份兼容当前接口的轻量快照。

## 相关文件
- Schema 文件：[staff_daily_report_v1.schema.json](/D:/Code/A实习项目/automage-agent-customization-main/automage_agents/schemas/staff_daily_report_v1.schema.json)

## 推荐主表映射

| 来源字段 | 目标表 | 目标列 | 说明 |
| --- | --- | --- | --- |
| `basic_info.org_id` | `work_records` | `org_id` | 所属组织 |
| `basic_info.department_or_project_group` | `work_records` | `department_id` | 建议解析成真实部门 ID；如果暂时没有映射关系，可先写 `meta.department_or_project_group` |
| 模板 ID | `work_records` | `template_id` | 对应 `form_templates.id` |
| `basic_info.user_id` | `work_records` | `user_id` | 填报人 |
| `basic_info.report_date` | `work_records` | `record_date` | 日报日期 |
| 生成值 | `work_records` | `title` | 建议格式：`[日报] {submitted_by} {report_date}` |
| `basic_info.report_status` | `work_records` | `status` | 建议做状态码映射 |
| `basic_info.submitted_at` | `work_records` | `submitted_at` | 提交时间 |
| `basic_info.submission_channel` | `work_records` | `source_type` | 建议做来源码映射 |
| 聚合检索字段 | `work_records` | `meta` | 存放风险、是否需支持、条目计数、原始路径等 |

## 推荐模板表映射

`form_templates` 建议保存以下内容：

| 列 | 建议值 |
| --- | --- |
| `name` | `Staff Daily Report Template` |
| `scope` | 员工日报模板范围值 |
| `status` | 启用 |
| `schema_json` | `staff_daily_report_v1.schema.json` 的完整内容 |
| `version` | `1` |
| `meta.schema_id` | `schema_v1_staff_daily` |
| `meta.schema_version` | `v1.0.0` |

## 推荐明细表映射

`work_record_items` 建议以“一个分区一个主字段”的方式保存，复杂分区使用 `value_json`，简单摘要使用 `value_text`。这样后续读整份日报最方便，解析器也简单。

### 一级字段设计

| field_key | field_label | field_type | 建议存储 |
| --- | --- | --- | --- |
| `basic_info` | 基础信息 | `object` | `value_json` |
| `today_task_progress` | 今日任务进展 | `array` | `value_json` |
| `today_completed_items` | 今日完成事项 | `array` | `value_json` |
| `today_artifacts` | 今日产出物清单 | `array` | `value_json` |
| `today_blockers` | 今日问题与阻塞 | `array` | `value_json` |
| `support_requests` | 需要支持的事项 | `array` | `value_json` |
| `decision_requests` | 需要确认或决策的事项 | `array` | `value_json` |
| `tomorrow_plans` | 明日计划 | `array` | `value_json` |
| `cross_module_requests` | 与其他模块的对接需求 | `array` | `value_json` |
| `risk_assessment` | 风险判断 | `object` | `value_json` |
| `workflow_notes` | Context / Prompt / Workflow 补充 | `array` | `value_json` |
| `daily_summary` | 今日总结 | `object` | `value_json` |
| `sign_off` | 签名确认 | `object` | `value_json` |
| `source_markdown` | 原始 Markdown 快照 | `markdown` | `value_text` |

### 检索增强字段

为了后面更容易筛选，建议额外增加一批“可直接过滤”的投影字段：

| field_key | field_label | field_type | 建议值 |
| --- | --- | --- | --- |
| `search.need_support` | 是否需要支持 | `boolean` | 任一 `support_requests.need_support = true` 则为 `true` |
| `search.blocker_count` | 阻塞数量 | `integer` | `today_blockers` 条数 |
| `search.decision_count` | 待决策数量 | `integer` | `decision_requests` 条数 |
| `search.risk_level` | 总体风险等级 | `enum` | `risk_assessment.overall_risk_level` |
| `search.follow_up_task_count` | 需继续跟进任务数 | `integer` | `today_task_progress` 中 `needs_follow_up = true` 的数量 |
| `search.artifact_count` | 产出物数量 | `integer` | `today_artifacts` 条数 |

这些字段可以放在 `work_record_items`，也可以冗余放进 `work_records.meta`。

## 分区结构说明

### 1. basic_info
对应模板的“基础信息”。

关键字段：
- `report_date`
- `submitted_by`
- `project_name`
- `role_name`
- `responsibility_module`
- `work_types`
- `report_status`
- `submitted_at`
- `self_confirmed`
- `org_id`
- `department_or_project_group`
- `user_id`
- `agent_node_id`
- `submission_channel`

### 2. today_task_progress
对应模板的“今日任务进展”，一行一项。

每项建议字段：
- `line_no`
- `related_task_id`
- `task_name`
- `today_result`
- `previous_status`
- `current_status`
- `completion_percent`
- `needs_follow_up`
- `notes`

### 3. today_completed_items
对应模板的“今日完成事项”。

每项建议字段：
- `item_name`
- `item_type`
- `completion_detail`
- `current_status`
- `evidence`
- `artifact_title`
- `artifact_uri`
- `related_module`
- `reusable_for_followup`

### 4. today_artifacts
对应模板的“今日产出物清单”。

每项建议字段：
- `artifact_name`
- `artifact_type`
- `main_content`
- `usage_scope`
- `current_version`
- `synced`

### 5. today_blockers
对应模板的“今日遇到的问题与阻塞”。

每项建议字段：
- `issue_name`
- `issue_description`
- `impact_scope`
- `severity`
- `attempted_solution`
- `is_blocking`
- `support_owner`

### 6. support_requests
对应模板的“需要支持的事项”。

每项建议字段：
- `need_support`
- `support_item`
- `support_reason`
- `expected_support_target`
- `expected_completion_at`
- `impact_if_unresolved`

### 7. decision_requests
对应模板的“需要确认 / 决策的事项”。

每项建议字段：
- `decision_item`
- `background`
- `options`
- `recommended_option_key`
- `decision_level`
- `suggested_escalation_target`
- `impact_if_unconfirmed`
- `expected_confirmation_at`
- `confirmed_by`

### 8. tomorrow_plans
对应模板的“明日计划”。

每项建议字段：
- `plan`
- `expected_artifact`
- `priority`
- `expected_completion_at`
- `dependencies`
- `needs_collaboration`

### 9. cross_module_requests
对应模板的“与其他模块的对接需求”。

每项建议字段：
- `counterpart`
- `request_content`
- `need_from_other_side`
- `available_from_me`
- `expected_completion_at`
- `current_status`

### 10. risk_assessment
对应模板的“风险判断”。

关键字段：
- `overall_risk_level`
- `primary_risk_sources`
- `impacted_deliverables`
- `impacted_workflow_nodes`
- `suggested_mitigation`
- `needs_escalation`
- `escalation_targets`

### 11. workflow_notes
对应模板的 “Context / Prompt / Workflow 相关补充”。

建议统一成数组，每项结构：
- `note_type`
- `content`
- `target_roles`
- `recommend_persist`
- `validated`
- `notes`

### 12. daily_summary
对应模板的“今日总结”。

关键字段：
- `most_important_progress`
- `biggest_issue`
- `top_priority_tomorrow`
- `team_attention_items`

### 13. sign_off
对应模板的“签名确认”。

关键字段：
- `submitter_confirmation_text`
- `confirmation_status`
- `confirmed_by`
- `confirmed_at`

## 与当前 `schema_v1_staff` 的兼容方案

你现在的代码里，`post_daily_report` 仍然要求旧版轻量字段：
- `timestamp`
- `work_progress`
- `issues_faced`
- `solution_attempt`
- `need_support`
- `next_day_plan`
- `resource_usage`

定义位置：
- [placeholders.py](/D:/Code/A实习项目/automage-agent-customization-main/automage_agents/schemas/placeholders.py:8)

因此推荐从新版结构里派生一份 `legacy_projection`：

| 旧字段 | 派生规则 |
| --- | --- |
| `timestamp` | 取 `basic_info.submitted_at`，没有则用 `basic_info.report_date + 默认时间` |
| `work_progress` | 汇总 `today_task_progress.today_result` + `today_completed_items.completion_detail` |
| `issues_faced` | 汇总 `today_blockers.issue_description` |
| `solution_attempt` | 汇总 `today_blockers.attempted_solution` |
| `need_support` | 任一 `support_requests.need_support = true` 或任一 `today_blockers.is_blocking = true` |
| `next_day_plan` | 汇总 `tomorrow_plans.plan` |
| `resource_usage` | 放计数信息，如 `task_count`、`artifact_count`、`blocker_count` |

推荐兼容写法：
- `staff_reports.report` 中保存 `legacy_projection`
- 完整结构化内容落到 `work_records + work_record_items`

## 推荐读取方式

### 读整份日报
1. 从 `work_records` 读取主记录。
2. 按 `work_record_id` 查询 `work_record_items`。
3. 以 `field_key` 组装回完整 JSON。

### 做筛选或列表页
优先使用这些字段：
- `work_records.record_date`
- `work_records.user_id`
- `work_records.status`
- `work_records.meta.need_support`
- `work_records.meta.risk_level`

如果没有把聚合字段冗余进 `meta`，就从 `work_record_items` 的 `search.*` 投影字段读。

## 推荐的最小样例

```json
{
  "schema_id": "schema_v1_staff_daily",
  "schema_version": "v1.0.0",
  "basic_info": {
    "report_date": "2026-05-06",
    "submitted_by": "张三",
    "project_name": "AutoMage-2 MVP",
    "role_name": "后端开发",
    "responsibility_module": "数据库",
    "work_types": ["database", "backend"],
    "report_status": "confirmed",
    "submitted_at": "2026-05-06T18:30:00+08:00",
    "self_confirmed": true,
    "schema_id_ref": "schema_v1_staff",
    "schema_version_ref": "v1.0.0",
    "org_id": "org-001",
    "department_or_project_group": "backend",
    "user_id": "user-001",
    "agent_node_id": "staff-node-001",
    "submission_channel": "web",
    "related_template_name": "Staff Daily Report Template"
  },
  "today_task_progress": [],
  "today_completed_items": [],
  "today_artifacts": [],
  "today_blockers": [],
  "support_requests": [],
  "decision_requests": [],
  "tomorrow_plans": [],
  "cross_module_requests": [],
  "risk_assessment": {
    "overall_risk_level": "low",
    "primary_risk_sources": [],
    "impacted_deliverables": [],
    "impacted_workflow_nodes": [],
    "suggested_mitigation": null,
    "needs_escalation": false,
    "escalation_targets": []
  },
  "workflow_notes": [],
  "daily_summary": {
    "most_important_progress": "完成日报结构设计",
    "biggest_issue": "暂无",
    "top_priority_tomorrow": "实现 Markdown 解析器",
    "team_attention_items": "后续统一字段编码"
  },
  "sign_off": {
    "submitter_confirmation_text": "我确认以上内容为今日真实工作记录",
    "confirmation_status": "confirmed",
    "confirmed_by": "张三",
    "confirmed_at": "2026-05-06T18:30:00+08:00"
  }
}
```

## 后续实现建议

真正开始做解析时，推荐按这个顺序：

1. 先把 Markdown 解析成 `staff_daily_report_v1.schema.json` 对应的标准 JSON。
2. 再把标准 JSON 落到 `work_records` 和 `work_record_items`。
3. 最后生成 `legacy_projection`，用于兼容当前 `staff_reports` 接口。

这样后续即使模板升级到 `v1.1.0`，也只需要调整解析器和模板 schema，不需要推翻数据库设计。

## 当前解析器用法

项目里已经提供了 Markdown 解析脚本：
- [parse_staff_daily_report.py](/D:/Code/A实习项目/automage-agent-customization-main/scripts/parse_staff_daily_report.py)

直接解析文件并输出到终端：

```powershell
python scripts\parse_staff_daily_report.py "你的日报.md"
```

解析后保存为 JSON 文件：

```powershell
python scripts\parse_staff_daily_report.py "你的日报.md" -o "output.json"
```

如果不想把原始 Markdown 一起放进 JSON：

```powershell
python scripts\parse_staff_daily_report.py "你的日报.md" --omit-source-markdown
```

对应解析实现：
- [staff_daily_report_parser.py](/D:/Code/A实习项目/automage-agent-customization-main/automage_agents/schemas/staff_daily_report_parser.py)

对应最小测试：
- [test_staff_daily_report_parser.py](/D:/Code/A实习项目/automage-agent-customization-main/tests/test_staff_daily_report_parser.py)
