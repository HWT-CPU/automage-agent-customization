# Yang Mock Skill Field Alignment

## Summary

- **ok**: `true`
- **strict_ok**: `true`
- **scope**: `yang-mock-to-current-skill-field-alignment`
- **yang_mock_dir**: `D:\AutoMage-manager-sync\客制化\里程碑二_杨卓_交付推进与联调v1.0.0`

## Comparison results

| Area | Required | Expected fields | Actual fields | Missing in current output | Extra in current output |
| ---- | -------- | --------------- | ------------- | ------------------------- | ----------------------- |
| staff_normal | true | 24 | 24 | - | - |
| staff_high_risk | true | 24 | 24 | - | - |
| manager_normal | true | 26 | 26 | - | - |
| manager_need_executive | true | 26 | 26 | - | - |
| staff_skill_output_vs_yang_normal | false | 24 | 24 | - | - |
| manager_skill_output_vs_yang_need_executive | false | 26 | 26 | - | - |
| executive_dream_output_vs_yang_card | false | 26 | 32 | - | `contract_status`<br>`decision_options`<br>`input`<br>`knowledge_refs`<br>`legacy_schema_id`<br>`runtime_context` |
| generated_task_vs_yang_task | false | 22 | 24 | - | `storage_table`<br>`task_queue_id` |

## Known drifts

No known drifts.

## Recommendations

- **Action**: Keep Staff and Manager adapter compatibility checks in regression because they should preserve Yang Zhuo top-level contract fields.
- **Action**: After the database alignment report is added, map each drift field to its real database table and API endpoint.
- **Action**: Keep `python scripts/check_yang_skill_field_alignment.py --strict` in regression; current Staff, Manager, Executive, and Task field alignment has no known drift.

## Commands

```powershell
python scripts/check_yang_skill_field_alignment.py
python scripts/check_yang_skill_field_alignment.py --strict
```
