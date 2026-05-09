# Landing Page P0 / P1 / P2 Field Plan

## Planning scope

This document defines the boss-side Landing Page display plan for AutoMage-2 Milestone 2.

The 5.6 goal is planning closure, not frontend implementation.

Recommended direction: combine Agent process transparency with enterprise delivery visibility.

## Display principles

- P0 must support the main demo chain: Staff daily report -> Manager summary -> Executive decision -> task assignment.
- P0 should only depend on fields already present in Agent/mock payloads or documented database tables.
- P1 can depend on richer backend aggregation once CRUD API is ready.
- P2 can depend on analytics, historical trends, and cross-team optimization.

## P0 fields

P0 is required for the first boss-side demo.

| Module | Field | Meaning | Source table / payload | Current readiness |
| ------ | ----- | ------- | ---------------------- | ----------------- |
| Project overview | project_name | Project name | runtime context / config | Ready |
| Project overview | milestone_name | Current milestone | runtime context / manual config | Ready |
| Project overview | run_date | Current operating date | `runtime_context.run_date` | Ready |
| Project overview | overall_status | Overall health: green/yellow/red | Manager report / Executive decision | Mock ready |
| Staff report | submitted_count | Number of submitted Staff reports | `staff_reports`, `work_records` | Mock ready |
| Staff report | missing_count | Number of missing reports | user list + reports | Needs user directory API |
| Staff report | key_progress | Key completed work | `staff_report.work_progress`, `work_record_items` | Mock ready |
| Staff report | issues_faced | Staff-side issues | `staff_report.issues_faced`, `work_record_items` | Mock ready |
| Manager summary | aggregated_summary | Department summary | `manager_reports.report.aggregated_summary` | Mock ready |
| Manager summary | top_risks | Top risks | `manager_reports.report.top_3_risks` | Mock ready |
| Manager summary | next_day_adjustment | Next-day adjustment | `manager_reports.report.next_day_adjustment` | Mock ready |
| Executive decision | decision_summary | Confirmed decision | `agent_decision_logs.comment`, decision payload | Mock ready |
| Executive decision | selected_option | Selected option | `agent_decision_logs.confirmed_option` | Mock ready |
| Task assignment | task_title | Generated task title | `task_queue.title` | Mock ready |
| Task assignment | assignee_user_id | Task assignee | `task_queue.assignee_user_id` | Mock ready |
| Task assignment | task_status | Task state | `task_queue.status` | Mock ready |
| Traceability | audit_log_id | Write trace ID | API response / `audit_logs` | Mock ready |
| Traceability | knowledge_refs | Feishu knowledge source refs | payload `meta.knowledge_refs` | Ready |

## P1 fields

P1 improves management visibility after real CRUD API is available.

| Module | Field | Meaning | Dependency |
| ------ | ----- | ------- | ---------- |
| Project overview | milestone_progress_percent | Milestone progress percentage | Task and report aggregation |
| Project overview | blocker_count | Active blocker count | Issue log / incident table |
| Staff report | late_submitters | Users who did not submit on time | User directory + report timestamps |
| Staff report | need_support_count | Staff reports requiring support | Formal Staff schema |
| Manager summary | department_health | Department-level health trend | Manager report history |
| Manager summary | unresolved_risks | Risks not yet converted to tasks | Risk/task linkage |
| Executive decision | pending_decision_count | Decisions waiting for boss confirmation | Decision status field |
| Task assignment | overdue_task_count | Overdue tasks | Task due date and status |
| Task assignment | task_completion_rate | Task completion rate | Task history |
| Traceability | request_id | API request trace | Real API middleware |
| Traceability | created_at / updated_at | Timeline fields | Real database timestamps |

## P2 fields

P2 is for later analytics and enterprise delivery enhancement.

| Module | Field | Meaning | Dependency |
| ------ | ----- | ------- | ---------- |
| Trend analytics | weekly_health_trend | Weekly project health trend | Historical reports |
| Trend analytics | risk_recurrence | Repeated risk topics | Risk classification |
| Agent performance | agent_success_rate | Agent flow success rate | Agent execution logs |
| Agent performance | correction_attempts | Schema correction count | Skill execution telemetry |
| Knowledge usage | knowledge_hit_rate | Feishu knowledge hit rate | Knowledge retrieval logs |
| Knowledge usage | most_used_sources | Most referenced docs | `knowledge_refs.sources` aggregation |
| Delivery assets | material_completion | Enterprise delivery asset readiness | Delivery checklist |
| Onboarding | missing_profile_fields | New employee missing information | User profile API |
| Onboarding | onboarding_task_progress | Onboarding task completion | Task workflow |

## P0 page layout

Recommended first version:

1. Top summary cards
   - Project status
   - Submitted reports
   - Active risks
   - Pending / generated tasks
2. Main chain timeline
   - Staff daily report
   - Manager summary
   - Executive decision
   - Task assignment
3. Risk and blocker panel
   - Top risks
   - Support needed
   - Main-chain blockers
4. Decision panel
   - Selected option
   - Decision summary
   - Generated tasks
5. Traceability panel
   - Audit log refs
   - Knowledge refs
   - Runtime context refs

## Implementation readiness

| Layer | Status | Notes |
| ----- | ------ | ----- |
| Agent mock payload | Ready | P0 can be displayed from mock flow |
| Real API data | Ready for P0 contract | Real smoke covers Staff, Manager, Decision, Task create/query/update; frontend binding remains M3 |
| Database timestamps | Ready for P0 contract | Backend models and real acceptance evidence include `created_at` / `updated_at` style trace fields |
| User directory | Deferred for M3 | M2 uses stable test identities; production Feishu roster/profile API remains M3 |
| Feishu knowledge refs | Ready | Lightweight refs are already attached to business payloads |
| Onboarding | Ready as minimal flow | Use `references/onboarding_information_completion_min_flow.md`; full profile API is deferred |

## Recommended 5.9 wording

Landing Page P0/P1/P2 field planning is complete at the product and data-contract level. P0 can be prototyped from mock Agent payloads and bound to the real main-chain API once frontend work starts. Remaining work is frontend implementation, production roster/profile data binding, and P1/P2 analytics, all outside the HWT Milestone 2 code-side blocker scope.
