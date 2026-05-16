# HWT M2 Real Backend Integration Carry-over

## Summary

Date: 2026-05-08

This document converts Yang Zhuo's real backend integration acceptance package and Xiong Jinwen's backend feedback package into Hu Wentao-side project actions.

## External evidence consumed

| Source | Evidence | Result for HWT |
| ------ | -------- | -------------- |
| Yang Zhuo real backend acceptance | `automage_m2_real_api_integration_acceptance/00_真实后端联调验收总报告.md` | Real backend service, `/healthz`, main API chain, database persistence, and pytest regression are usable as acceptance evidence. |
| Yang Zhuo main-chain report | `automage_m2_real_api_integration_acceptance/03_真实API主链路联调报告.md` | Staff write/read, Manager write/read, Dream, Decision, direct tasks, task query, and task update have all been exercised against real API. |
| Yang Zhuo DB check | `automage_m2_real_api_integration_acceptance/04_数据库落库核查报告.md` | Real API writes landed in `work_records`, `work_record_items`, `incidents`, `summaries`, `decision_records`, `decision_logs`, `tasks`, `task_assignments`, `task_updates`, and `audit_logs`. |
| Yang Zhuo idempotency/RBAC report | `automage_m2_real_api_integration_acceptance/05_幂等_RBAC_409验证报告.md` | HWT must keep request identity, role restrictions, duplicate write handling, and task update conflict behavior in regression. |
| Yang Zhuo 5.9 advice | `automage_m2_real_api_integration_acceptance/08_5.9里程碑二验收建议.md` | HWT owner item is Agent field conversion convergence plus `request_id` and `Idempotency-Key` strategy. |
| Xiong Jinwen RBAC feedback | `5月8日后端反馈/01_权限控制与跨部门访问校验说明.md` | Agent requests must keep header identity and body identity consistent; non-executive Dream/decision calls must not be generated. |
| Xiong Jinwen error-code feedback | `5月8日后端反馈/02_接口错误码说明.md` | Agent/IM should treat `403` as permission, `404` as missing resource, and `409` as write conflict with `error_code`, `conflict_target`, and `request_id`. |
| Xiong Jinwen delivery alignment | `5月8日后端反馈/06_数据库接口交付材料对齐说明.md` | HWT should use HTTP API as the formal path and treat SQLAlchemy/direct snapshot paths as local compatibility only. |
| Xiong Jinwen field/API workbook | `08_后端数据表字段与API清单.xlsx` | Formal table and API mapping confirms the current main-chain table contract. |

## HWT-side status changes

| Area | Previous status | Updated status | Evidence |
| ---- | --------------- | -------------- | -------- |
| Real backend runtime | Runtime pending | Externally validated by Yang Zhuo package | `run_id=m2real-20260508040831` |
| Real DB write path | Blocked/pending | Externally validated by DB read-only checks | `04_数据库落库核查报告.md` |
| Agent mock/schema alignment | Done locally | Still valid; strict drift remains closed | `references/yang_mock_skill_field_alignment.md` |
| Abuse/idempotency API protection | Done in code | Strengthened by HWT follow-up endpoint-level tests | `tests/test_idempotency_flow.py` |
| Real smoke script | Minimal chain | Updated to carry `Idempotency-Key` for write APIs and include direct task create/update | `scripts/smoke_real_api.py` |

## HWT action decisions

| Decision | Rationale | Implementation |
| -------- | --------- | -------------- |
| Keep Agent field adapters as the authoritative conversion layer | Yang Zhuo and Xiong Jinwen both show naming differences such as `dept_id` vs `department_id`, `selected_option_id` vs `selected_option_key`, and `task_title` vs `tasks.title`. | Continue using `automage_agents/schemas/*_v1.py` adapters and `check_yang_skill_field_alignment.py --strict`. |
| Generate stable request IDs for all Agent-originated API calls | Backend feedback requires traceability and conflict handling through `request_id`. | `scripts/smoke_real_api.py` already sets `X-Request-Id`; IM/runtime paths should keep deterministic event-derived IDs. |
| Add `Idempotency-Key` to write API smoke requests | Xiong Jinwen's write rules recommend idempotency for Staff, Manager, Decision, and Task writes. | `scripts/smoke_real_api.py` now configures idempotency keys for `POST /api/v1/report/staff`, `POST /api/v1/report/manager`, `POST /api/v1/decision/commit`, `POST /api/v1/tasks`, and `PATCH /api/v1/tasks/{task_id}`. |
| Do not commit raw external acceptance packages or Redis connection material | These folders may contain generated logs, environment-specific paths, and sensitive connection hints. | Keep them local reference inputs; commit only HWT-derived summary and code changes. |

## Remaining HWT follow-ups

| Priority | Item | Owner | Next action |
| -------- | ---- | ----- | ----------- |
| P0 | Real API smoke against current merged `main` | Hu Wentao / backend runtime owner | Start API with real env, then run `python scripts/smoke_real_api.py --base-url http://localhost:8000 --summary-only --output-json _cache/smoke_real_api_latest.json`. |
| P0 | IM event to API request identity strategy | Hu Wentao | Map Feishu event/message IDs to stable `X-Request-Id` and `Idempotency-Key` before production bot use. |
| P1 | Error-code user-facing handling | Hu Wentao / frontend | Map `403`, `404`, and `409` to IM/Landing Page messages without blind retry. |
| P1 | Field workbook regression | Hu Wentao / Yang Zhuo | Keep `check_yang_skill_field_alignment.py --strict` and compare field workbook changes before M3. |
| P2 | Redis production validation | Hu Wentao / Xiong Jinwen | Validate Redis backend mode without exposing Redis credentials in repo or logs. |

## Recommended HWT acceptance wording

Hu Wentao-side Milestone 2 can now be stated as:

```text
Agent/IM/Skill schema conversion and mock orchestration are closed locally, and the external real backend package shows the Staff -> Manager -> Executive -> Task API chain can persist to the formal tables. HWT has updated the real API smoke script to follow backend idempotency guidance and direct task create/update coverage. Remaining work moves to runtime execution against the current merged main environment and production IM request-id/idempotency mapping.
```

## Verification commands

```powershell
python scripts/smoke_real_api.py --dry-run
python scripts/smoke_real_api.py --base-url http://localhost:8000 --summary-only --output-json _cache/smoke_real_api_latest.json
python -m pytest tests\test_smoke_real_api_plan.py tests\test_feishu_im_flow.py tests\test_scheduler_jobs.py tests\test_manager_decision_task_flow.py tests\test_idempotency_flow.py tests\test_redis_abuse_store.py tests\test_staff_daily_report_parser.py tests\test_skill_result.py -q
python scripts\check_yang_skill_field_alignment.py --strict
```
