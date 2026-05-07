# Yang Mock Skill Field Alignment

## Summary

- **ok**: `true`
- **strict_ok**: `false`
- **scope**: `yang-mock-to-current-skill-field-alignment`
- **yang_mock_dir**: `D:\Auto-mage2\里程碑二_杨卓_交付推进与联调v1.0.0`

## Comparison results

| Area | Required | Expected fields | Actual fields | Missing in current output | Extra in current output |
| ---- | -------- | --------------- | ------------- | ------------------------- | ----------------------- |
| staff_normal | true | 24 | 24 | - | - |
| staff_high_risk | true | 24 | 24 | - | - |
| manager_normal | true | 26 | 26 | - | - |
| manager_need_executive | true | 26 | 26 | - | - |
| staff_skill_output_vs_yang_normal | false | 24 | 24 | - | - |
| manager_skill_output_vs_yang_need_executive | false | 26 | 26 | - | - |
| executive_dream_output_vs_yang_card | false | 26 | 6 | `business_summary`<br>`confirmed_at`<br>`confirmed_by`<br>`confirmed_option`<br>`decision_items`<br>`decision_required`<br>`executive_node_id`<br>`executive_user_id`<br>`expected_impact`<br>`generated_tasks`<br>`human_confirm_status`<br>`key_risks`<br>`meta`<br>`option_a`<br>`option_b`<br>`org_id`<br>`reasoning_summary`<br>`recommended_option`<br>`schema_version`<br>`signature`<br>`source_decision_ids`<br>`source_incident_ids`<br>`source_summary_ids`<br>`summary_date`<br>`timestamp` | `contract_status`<br>`decision_options`<br>`input`<br>`knowledge_refs`<br>`runtime_context` |
| generated_task_vs_yang_task | false | 22 | 10 | `artifacts`<br>`assignee_role`<br>`assignment_type`<br>`confirm_required`<br>`created_by_node_id`<br>`creator_user_id`<br>`department_id`<br>`org_id`<br>`schema_id`<br>`schema_version`<br>`source_decision_id`<br>`source_id`<br>`source_summary_id`<br>`source_type`<br>`task_description`<br>`task_title` | `description`<br>`storage_table`<br>`task_queue_id`<br>`title` |

## Known drifts

### executive_dream_output_vs_yang_card

- **type**: `placeholder_contract`
- **fields**: `business_summary`<br>`confirmed_at`<br>`confirmed_by`<br>`confirmed_option`<br>`decision_items`<br>`decision_required`<br>`executive_node_id`<br>`executive_user_id`<br>`expected_impact`<br>`generated_tasks`<br>`human_confirm_status`<br>`key_risks`<br>`meta`<br>`option_a`<br>`option_b`<br>`org_id`<br>`reasoning_summary`<br>`recommended_option`<br>`schema_version`<br>`signature`<br>`source_decision_ids`<br>`source_incident_ids`<br>`source_summary_ids`<br>`summary_date`<br>`timestamp`
- **reason**: Current `dream_decision_engine` returns `schema_v1_dream_decision` placeholder output, while Yang Zhuo mock uses `schema_v1_executive` decision card.

### generated_task_vs_yang_task

- **type**: `task_payload_adapter_gap`
- **fields**: `artifacts`<br>`assignee_role`<br>`assignment_type`<br>`confirm_required`<br>`created_by_node_id`<br>`creator_user_id`<br>`department_id`<br>`org_id`<br>`schema_id`<br>`schema_version`<br>`source_decision_id`<br>`source_id`<br>`source_summary_id`<br>`source_type`<br>`task_description`<br>`task_title`
- **reason**: Current `commit_decision` task candidates are lightweight task queue items, while Yang Zhuo task mock models formal task fields.


## Recommendations

- **Action**: Keep Staff and Manager adapter compatibility checks in regression because they should preserve Yang Zhuo top-level contract fields.
- **Action**: Treat Executive and Task differences as known placeholder gaps until formal `schema_v1_executive` and `schema_v1_task` adapters are implemented.
- **Action**: After the database alignment report is added, map each drift field to its real database table and API endpoint.
- **Action**: Add a formal Executive decision card adapter or update `dream_decision_engine` to emit Yang Zhuo `schema_v1_executive` fields.
- **Action**: Add a task candidate adapter that maps Yang Zhuo `schema_v1_task` fields into `task_queue` and later formal `tasks` payloads.

## Commands

```powershell
python scripts/check_yang_skill_field_alignment.py
python scripts/check_yang_skill_field_alignment.py --strict
```
