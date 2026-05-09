# HWT Milestone 2 5.6-5.9 Completion Matrix

## Verdict

Hu Wentao-side engineering work for the 5.6-5.9 Milestone 2 schedule is closed for repository-level acceptance.

The current project can enter Milestone 3 integration with these boundaries:

- Staff -> Manager -> Executive -> Task main chain is covered by local regression and Real API smoke.
- Schema, Context, Prompt/Skill, API request identity, idempotency, RBAC, and task update behavior have repository evidence.
- Landing Page P0 is closed as data contract and field plan, not frontend implementation.
- New employee onboarding / information completion is closed as a minimal half-manual flow contract; production user-profile API remains a Milestone 3 dependency under M3/deployment/frontend/profile API scope.
- Raw external acceptance materials and Redis connection details are not committed.

## Main-chain status

| Main-chain item | Required by schedule | HWT status | Evidence | Remaining owner / note |
| --------------- | -------------------- | ---------- | -------- | ---------------------- |
| Postgres database + CRUD API | Database online and core API callable before Skill/Agent validation | Done for HWT acceptance through merged backend code plus real API smoke evidence | `scripts/smoke_real_api.py`, `references/hwt_m2_real_backend_integration_plan.md` | Runtime ownership stays with backend/deployment owner |
| Database Skill | Agent can read/write through formal API path | Done at Agent/API contract level | `references/database_skill_alignment.md`, `delivery/database-api-skill/SKILL.md`, `references/hwt_m2_real_backend_integration_plan.md` | Production deployment credentials are out of repo |
| Mock data + unified IDs | Stable org/user/role/Agent IDs for tests | Done | `scripts/test_database_skill_mock.py`, `scripts/test_yang_mock_workflow.py`, `scripts/smoke_real_api.py` | Keep IDs stable for M3 |
| Agent orchestration | Staff report -> Manager summary -> Executive decision -> task dispatch | Done | `tests/test_manager_decision_task_flow.py`, `tests/test_feishu_im_flow.py`, `scripts/verify_im_decision_task_flow.py` | Production Feishu roster/open_id mapping remains external |
| Unit/regression validation | Main chain and edge behavior covered | Done | `tests/test_idempotency_flow.py`, `tests/test_redis_abuse_store.py`, `tests/test_smoke_real_api_plan.py` | Continue running before M3 merges |
| Landing Page P0 planning | P0 fields and data sources frozen | Done for planning | `references/landing_page_p0_p1_p2.md` | Frontend implementation is not HWT code-side blocker |
| New employee onboarding / information completion | Minimal flow defined | Done as half-manual contract | `references/onboarding_information_completion_min_flow.md` | Formal user-profile API is M3/backend dependency |

## 5.6 schedule check

| Line | HWT task | Status | Evidence / result |
| ---- | -------- | ------ | ----------------- |
| Backend / Skill | Install and test database Skill | Done | Database Skill path documented and mock/real request paths validated through regression and smoke plan |
| Agent orchestration | Staff daily report template into Staff Agent parser | Done | `automage_agents/schemas/staff_daily_report_parser.py`, `tests/test_staff_daily_report_parser.py` |
| Agent orchestration | Manager reads Staff report and generates summary | Done | `scripts/test_database_skill_mock.py`, `tests/test_manager_decision_task_flow.py` |
| Checkpoint | Issue log exists | Done | `references/milestone2_issue_log.md` |
| Checkpoint | Database/API/trace not ready at 5.6 | Converted to later acceptance evidence | `references/hwt_m2_real_backend_integration_plan.md`, real smoke run evidence |

## 5.7 schedule check

| Line | HWT task | Status | Evidence / result |
| ---- | -------- | ------ | ----------------- |
| Agent orchestration | Replace local mock demo with real API path | Done at smoke/API validation level | `scripts/smoke_real_api.py` covers Staff, Manager, Decision, direct Task create/query/update |
| Agent orchestration | Staff report writes to backend | Done | Real smoke step `post_staff_report`; local API tests cover write/idempotency |
| Agent orchestration | Manager reads Staff report and generates summary | Done | `tests/test_manager_decision_task_flow.py`; real smoke step `post_manager_report` |
| Checkpoint | Landing Page P0 has data sources | Done | `references/landing_page_p0_p1_p2.md` |

## 5.8 schedule check

| Line | HWT task | Status | Evidence / result |
| ---- | -------- | ------ | ----------------- |
| Main-chain joint debug | Decision confirmation, task generation, Staff task query loop | Done | `tests/test_manager_decision_task_flow.py`; real smoke steps `commit_decision`, `post_tasks`, `fetch_tasks`, `patch_task` |
| Backend feedback loop | Report API/Skill issues with request identity and idempotency | Done | `references/hwt_m2_real_backend_integration_plan.md`, `tests/test_smoke_real_api_plan.py` |
| New employee onboarding | Minimum half-manual onboarding/info completion flow | Done as M2 contract | `references/onboarding_information_completion_min_flow.md` |
| Acceptance prep | 5.9 checklist from HWT side | Done | This completion matrix |

## 5.9 schedule check

| Line | HWT task | Status | Evidence / result |
| ---- | -------- | ------ | ----------------- |
| Blocker triage | Close HWT code-side blockers | Done | Yang strict alignment reports no known drift; targeted regression passes |
| Agent final version | Fix workflow, prompt, context, Skill blockers | Done | Feishu runtime context refs, Executive/Task adapters, IM role guard, parser updates |
| Full-chain rerun | Staff -> Manager -> Executive -> Task -> Staff query | Done | Real smoke summary evidence and `tests/test_manager_decision_task_flow.py` |
| Freeze scope | Do not add new M2 features | Done | Remaining items are explicitly M3/deployment/frontend dependencies |

## Current acceptance wording

```text
Hu Wentao-side Milestone 2 work for 5.6-5.9 is closed at repository level. The Staff daily report parser, Manager summary path, Executive decision card/task adapters, IM authorization guard, real API smoke plan, idempotency/request-id strategy, RBAC/idempotency regression, and Landing Page P0 data contract are in place. A real API smoke run has validated the Staff -> Manager -> Executive -> Task create/query/update chain against localhost runtime. The only remaining items are not HWT code-side blockers: production Feishu open_id roster, deployment supervision, frontend Landing Page implementation/data binding, staff report revision UX, and formal onboarding/profile API implementation.
```

## Recommended next commands

```powershell
python scripts\smoke_real_api.py --base-url http://localhost:8000 --summary-only --output-json _cache\smoke_real_api_latest.json
python -m pytest tests\test_smoke_real_api_plan.py tests\test_feishu_im_flow.py tests\test_scheduler_jobs.py tests\test_manager_decision_task_flow.py tests\test_idempotency_flow.py tests\test_redis_abuse_store.py tests\test_staff_daily_report_parser.py tests\test_skill_result.py -q
python scripts\check_yang_skill_field_alignment.py --strict
```
