# Milestone 2 5.6 Acceptance

## Acceptance context

Date: 2026-05-06

Goal: close the 5.6 checkpoint for Milestone 2 with a clear distinction between completed Agent/mock work and blocked real backend work.

Current 5.9 status is tracked in `references/hwt_m2_0506_0509_completion_matrix.md`.

Backend status confirmed by project owner:

| Item | Status |
| ---- | ------ |
| API base URL | Not available yet |
| Backend API service | Not ready / not started |
| Authentication | Not required for the first smoke test |

PR3 merge update on 2026-05-07:

| Item | Status |
| ---- | ------ |
| RBAC / auth headers | Code merged locally |
| Write idempotency | Code merged locally |
| Manager decision -> task closed loop | Code merged locally |
| Local PR regression | Passed |
| External real API runtime | Still needs service start and smoke validation |

## Overall conclusion

5.6 was not fully closed as a real backend milestone because the backend CRUD API was not ready and the API service was not running.

After merging PR3 locally, the project now has a runnable FastAPI/DB/RBAC/idempotency/task closed-loop implementation in code. External real API runtime validation is still pending service startup and environment configuration.

## Main chain status

| Chain item | Required status | Current status | Acceptance result | Evidence |
| ---------- | --------------- | -------------- | ----------------- | -------- |
| PostgreSQL database | Online and reachable | Database connectivity was validated locally before, but no API write path is available yet | Partially done | `scripts/check_database_connection.py` |
| CRUD API | Core endpoints callable | PR3 FastAPI code merged locally; external service still needs startup validation | Code merged / runtime pending | `automage_agents/server/app.py`, `scripts/run_api.py`, `python scripts/smoke_real_api.py --dry-run` |
| Database Skill | Agent can understand and call database access path | Agent-side Skill delivery and mock validation are ready | Mock done | `delivery/database-api-skill/SKILL.md`, `references/database_skill_alignment.md` |
| Mock data and unified test IDs | Stable demo IDs and mock tables | Ready; Yang Zhuo standard mock package also validates locally | Done | `scripts/test_database_skill_mock.py`, `scripts/test_yang_mock_workflow.py` |
| Agent orchestration | Staff -> Manager -> Executive -> task flow | Ready on mock path; Yang Zhuo Staff normal/high-risk, Manager normal/need-executive, Executive decision, generated tasks, and next-round seed all pass | Mock done | `scripts/test_database_skill_mock.py`, `scripts/knowledge_auto_skill_flow.py`, `scripts/test_yang_mock_workflow.py` |
| Yang mock field alignment | Staff/Manager top-level fields align with current adapters and Skills | Staff and Manager have no blocking field gaps; PR3 adds formal task API, but current strict checker still records Executive placeholder and mock task drift | Partially done | `scripts/check_yang_skill_field_alignment.py`, `references/yang_mock_skill_field_alignment.md` |
| RBAC / idempotency / task closed loop | Real API must protect role scope, avoid duplicate writes, and close manager decision to tasks | PR3 merged locally and regression passed | Done in code | `tests/test_rbac_policy.py`, `tests/test_idempotency_flow.py`, `tests/test_manager_decision_task_flow.py` |
| Unit / regression validation | Compile and mock flow pass | Ready | Done | `python -m compileall automage_agents scripts` |
| Landing Page planning | P0/P1/P2 fields identified | Planned in local reference doc | Done for planning | `references/landing_page_p0_p1_p2.md` |
| Local architecture KB | Agent-friendly architecture knowledge package | Ready as local structured reference | Done for reference | `references/local_architecture_kb.md`, `AutoMage_2_MVP_KB_v1.0.0/05_AGENT_SKILL/SKILL.md` |
| Yang Zhuo database alignment report | Real database structure and mock/API/DB alignment | Local directory exists but is empty | Blocked | `里程碑二_杨卓_数据库测试对齐报告v1.0.0/` |
| New employee onboarding / information completion flow | Needs API and identity fields | Not implemented in real flow | Blocked | Requires backend API and identity field contract |

## 5.6 evening checkpoint

| Checkpoint | Result | Notes |
| ---------- | ------ | ----- |
| Database is online | Partially done | Database connectivity can be checked locally, but no real API write flow is available yet |
| Data table scope aligned with Yang Zhuo | Partially done | Agent-side schema and table mapping are documented; final backend field freeze still needs owner confirmation |
| Core CRUD API callable | Blocked | Backend API is not ready and not started |
| Audit and trace fields available | Mock done | Mock backend writes `audit_logs`; real API audit is not verified |
| Database Skill delivered | Done | Delivery docs and alignment notes exist |
| Database Skill tested by Hu Wentao | Mock done | Agent-side mock validation passes |
| Issue record document created | Done | `references/milestone2_issue_log.md` |
| Staff daily report template connected to Staff Agent input parsing | Partially done | Staff schema coercion and Markdown import exist; full formal template parser remains follow-up work |
| Manager reads Staff reports and generates summary | Mock done | Mock Manager flow passes |
| Manager / Executive output scope supports boss transparency | Partially done | Current schemas and decision flow exist; final product wording remains follow-up |
| Landing Page P0/P1/P2 fields planned | Done | `references/landing_page_p0_p1_p2.md` |

## Done list for 5.6

- Agent-side database Skill path is documented.
- Mock backend stores Staff reports, Manager summaries, Executive decisions, tasks, and audit logs.
- Staff -> Manager -> Executive -> task handoff can run on mock data.
- Yang Zhuo standard M2 mock workflow package passes local validation.
- Yang Zhuo Staff/Manager mock fields align with current adapters and Skill outputs.
- Local architecture KB is registered as a structured reference package.
- Feishu knowledge auto retrieval and payload enrichment are integrated into business Skills.
- 5.6 issue log and Landing Page field planning are created.
- Real API smoke test script is prepared for backend readiness.
- PR3 RBAC, write idempotency, scheduler jobs, formal task tables, and Manager decision -> Executive decision -> task closed loop are merged locally.

## Blocked list for 5.6

- External real CRUD API runtime still needs service startup and environment validation.
- Real audit and trace are covered by local tests, but still need validation against the external runtime and real PostgreSQL environment.
- Real database write path through FastAPI still needs smoke validation after API startup.
- Yang Zhuo database alignment report cannot be consumed yet because the local directory is empty.
- Executive Dream output still uses placeholder `schema_v1_dream_decision` instead of Yang Zhuo `schema_v1_executive`.
- Current mock generated task output still uses lightweight `task_queue` entries in the strict field checker; PR3 adds formal `tasks / task_assignments / task_updates` API path for real backend validation.
- New employee onboarding / information completion flow depends on identity and user profile API contracts.

## Recommended acceptance wording

Milestone 2 5.6 Agent-side and mock-side work is closed. PR3 brings the local real backend implementation into the repository, including RBAC, idempotency, scheduler jobs, and formal task closed loop. The remaining backend acceptance item is external runtime validation: start the API, initialize/seed the database, then run the real API smoke test.

## Commands

Mock and regression validation:

```powershell
python -m compileall automage_agents scripts
python scripts/test_database_skill_mock.py
python scripts/test_yang_mock_workflow.py
python scripts/check_yang_skill_field_alignment.py
python scripts/knowledge_auto_skill_flow.py "OpenAPI 契约"
```

PR3 backend regression:

```powershell
python -m pytest tests/test_rbac_policy.py tests/test_idempotency_flow.py tests/test_manager_decision_task_flow.py tests/test_scheduler_jobs.py tests/test_daily_report_api.py -q
```

Real API dry-run validation:

```powershell
python scripts/smoke_real_api.py --dry-run
```

Real API validation after backend starts:

```powershell
python scripts/smoke_real_api.py --base-url http://localhost:8000 --summary-only --output-json _cache/smoke_real_api_latest.json
```
