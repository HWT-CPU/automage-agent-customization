# Milestone 2 Issue Log

## Current checkpoint

Date: 2026-05-06

5.9 closure update:

| Item | Status |
| ---- | ------ |
| HWT repository-level Milestone 2 work | Closed |
| Real API smoke chain | Passed against localhost runtime with summary output |
| Yang schema strict alignment | Passed with no known drift |
| Remaining blockers | Moved to M3/deployment/frontend/profile API scope |

Original 5.6 backend status confirmed:

| Item | Status |
| ---- | ------ |
| API base URL | Not available yet |
| Backend API service | Not ready / not started |
| Authentication | Not required for first smoke test |

## Issue table

| ID | Area | Issue | Impact | Owner | Status | Next action | Target date |
| -- | ---- | ----- | ------ | ----- | ------ | ----------- | ----------- |
| M2-0506-001 | Backend API | Core CRUD API is not ready and service is not started | Blocks real API smoke test, real database write validation, and real audit validation | Xiong Jinwen | Done for HWT acceptance | Real API smoke passed against localhost runtime; keep deployment monitoring in M3 | 2026-05-09 |
| M2-0506-002 | Database | Real API write path to PostgreSQL is not validated | Blocks formal database Skill acceptance | Xiong Jinwen / Hu Wentao | Done for HWT acceptance | Real smoke covers Staff/Manager/Decision/Task writes and query/update | 2026-05-09 |
| M2-0506-003 | Audit / trace | Real audit and request trace fields are not verified | Blocks production-grade traceability acceptance | Xiong Jinwen | Done for HWT acceptance | Request identity and idempotency are covered by smoke plan and regression | 2026-05-09 |
| M2-0506-004 | Schema alignment | Final backend field freeze is not fully confirmed in repo | May cause payload and table mapping rework | Yang Zhuo / Xiong Jinwen | Done | Strict Yang alignment reports no known drift | 2026-05-09 |
| M2-0506-005 | Staff report parsing | Full formal Staff daily report template parser is not fully automated | Limits real daily report import precision | Hu Wentao | Done | Parser supports numbered and unnumbered Chinese section titles with regression | 2026-05-09 |
| M2-0506-006 | Landing Page | Boss-side P0/P1/P2 display fields needed explicit planning | May delay WebUI implementation | Zhang Runcheng / Yang Zhuo | Done for planning | Use `references/landing_page_p0_p1_p2.md` for implementation alignment | 2026-05-06 |
| M2-0506-007 | New employee onboarding | Onboarding / information completion flow depends on identity API contract | Blocks real enterprise onboarding scenario | Xiong Jinwen / Zhang Runcheng | Done as M2 minimal flow | Use `references/onboarding_information_completion_min_flow.md`; profile API remains M3 scope | 2026-05-09 |
| M2-0506-008 | Agent orchestration | Agent orchestration is validated on mock but not real backend | Blocks milestone-three real integration | Hu Wentao / Xiong Jinwen | Done | Real API smoke and Manager decision task flow regression cover the chain | 2026-05-09 |
| M2-0506-009 | Feishu knowledge | Knowledge retrieval currently depends on local cached Feishu wiki data | May need resync before formal demo | Hu Wentao | Done for M2 | Runtime knowledge refs are injected into Staff/Manager/Executive payloads; resync is M3 operation | 2026-05-09 |
| M2-0507-010 | Yang Zhuo mock package | Standard M2 mock workflow package needs to be part of local regression | Prevents field drift between project code and Yang Zhuo contract examples | Hu Wentao | Done | Run `python scripts/test_yang_mock_workflow.py` in regression | 2026-05-07 |
| M2-0507-011 | Local architecture KB | Architecture KB should be registered as the local reference source | Prevents architecture Q&A from relying on memory or scattered docs | Hu Wentao | Done | Use `references/local_architecture_kb.md` and `AutoMage_2_MVP_KB_v1.0.0/05_AGENT_SKILL/SKILL.md` | 2026-05-07 |
| M2-0507-012 | Database alignment report | Yang Zhuo database test alignment report directory exists but is empty | Blocks real DB structure comparison and mock/API/DB field reconciliation | Yang Zhuo / Hu Wentao | Done for HWT acceptance | Use consumed external acceptance evidence summarized in `references/hwt_m2_real_backend_integration_plan.md`; do not commit raw report packages | 2026-05-09 |
| M2-0507-013 | Yang mock field alignment | Staff and Manager fields must not drift from Yang Zhuo standard mock examples | Prevents 5.7 mock-to-skill integration failures | Hu Wentao | Done | Run `python scripts/check_yang_skill_field_alignment.py`; report at `references/yang_mock_skill_field_alignment.md` | 2026-05-07 |
| M2-0507-014 | Executive contract | Current Dream output is still a placeholder and does not emit full Yang Zhuo `schema_v1_executive` decision card | Blocks strict Yang contract acceptance for Executive layer | Hu Wentao / Xu Shaoyang | Done | Executive decision card adapter emits `schema_v1_executive`; strict checker passes | 2026-05-09 |
| M2-0507-015 | Task contract | Current mock generated tasks are lightweight `task_queue` entries in strict field alignment, while PR3 adds formal task API and tables | Blocks strict task schema acceptance until mock checker and Agent task adapter point at the formal task path | Hu Wentao / Xiong Jinwen | Done | Task adapter emits `schema_v1_task`; strict checker passes | 2026-05-09 |
| M2-0507-016 | PR3 backend merge | RBAC, write idempotency, scheduler jobs, formal task tables, and Manager decision task closed loop need to be merged into current local project without overwriting knowledge/schema work | Unblocks local real backend implementation and reduces M3 integration risk | Hu Wentao / Xiong Jinwen | Done in code | Run PR3 backend regression and real API smoke after service startup | 2026-05-07 |
| M2-0507-017 | Real API runtime validation | PR3 backend code is merged locally, but external FastAPI runtime and real PostgreSQL write path still need smoke validation | Blocks final real-backend acceptance | Xiong Jinwen / Hu Wentao | Done | Run `python scripts/smoke_real_api.py --base-url http://localhost:8000 --summary-only --output-json _cache/smoke_real_api_latest.json` | 2026-05-09 |

## Main-chain blockers

The main chain is:

```text
Database online -> CRUD API -> Database Skill -> Mock data -> Agent integration -> Unit acceptance
```

Current main-chain blocker after 5.9 closure:

```text
No HWT repository-level blocker remains for Milestone 2. Production Feishu roster, deployment supervision, frontend Landing Page implementation, and formal profile API move to Milestone 3.
```

## Non-blocking completed items

- Agent-side mock flow is available.
- Database Skill delivery documentation exists.
- Mock data tables and unified IDs are usable for local validation.
- Yang Zhuo standard M2 mock workflow validates locally through `scripts/test_yang_mock_workflow.py`.
- Yang Zhuo Staff/Manager field alignment validates locally through `scripts/check_yang_skill_field_alignment.py`.
- Local architecture KB is registered through `references/local_architecture_kb.md`.
- Knowledge auto retrieval and business payload enrichment are integrated.
- Landing Page field planning is documented.
- PR3 backend code for RBAC, idempotency, scheduler, formal task tables, and Manager decision task closed loop is merged locally and covered by tests.

## Escalation summary

The team can mark Hu Wentao-side Milestone 2 as closed at repository level. The 5.6 blockers were either resolved by the 5.8-5.9 real API smoke and regression work, or explicitly moved to Milestone 3 as deployment/frontend/profile API scope.
