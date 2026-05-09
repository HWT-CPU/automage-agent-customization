# New Employee Onboarding / Information Completion Minimal Flow

## Purpose

This document closes the Milestone 2 requirement for a minimal new employee onboarding and information completion flow from Hu Wentao's side.

The Milestone 2 scope is a half-manual contract that can be executed by Agent/Manager/Backend operators without adding new product scope before 5.9. Full self-service onboarding UI and formal profile APIs are Milestone 3 work.

## Scope boundary

| Area | Milestone 2 decision |
| ---- | -------------------- |
| User source of truth | Existing backend `users`, `departments`, `organizations`, and Agent identity headers/body identity |
| Missing information detection | Half-manual checklist driven by user metadata and Agent init payload |
| Task dispatch | Use existing `POST /api/v1/tasks` to create completion tasks |
| Staff follow-up | Staff can query task list with `GET /api/v1/tasks` and update status with `PATCH /api/v1/tasks/{task_id}` |
| Audit / trace | Use `X-Request-Id`, `Idempotency-Key`, and backend audit logs |
| Out of scope for M2 | New profile table, new onboarding UI, HRIS import, automatic Feishu roster sync |

## Minimum required profile fields

| Field | Source | Required for M2 | Fallback |
| ----- | ------ | --------------- | -------- |
| `org_id` | User/org seed data or Agent metadata | Yes | `org_automage_mvp` for demo |
| `department_id` | Department seed data or Agent identity | Yes | Manager assigns manually |
| `user_id` | Backend user username/public id or Agent identity | Yes | Use existing smoke/mock IDs |
| `display_name` | User model or Agent metadata | Yes | Feishu display name / manual entry |
| `role` | Agent identity | Yes | Staff until promoted by Manager |
| `level` | Agent identity | Yes | `l1_staff` for Staff |
| `manager_node_id` | Agent identity / department manager | Yes for Staff | Manager fills manually |
| `node_id` | Agent registry / init request | Yes | Generated stable Agent node ID |
| `feishu_open_id` | Feishu roster | No for M2 | Deferred to production roster mapping |
| `contact` | HR/user profile API | No for M2 | Deferred to M3 profile API |

## Flow

| Step | Actor | Action | API / artifact | Output |
| ---- | ----- | ------ | -------------- | ------ |
| 1 | Manager / operator | Collect minimal identity fields for the new employee | Manual form or issue checklist | Draft identity payload |
| 2 | Manager / operator | Initialize Staff Agent session | `POST /api/v1/agent/init` | Agent session and traceable request ID |
| 3 | Manager | Create an information completion task for the employee | `POST /api/v1/tasks` with `Idempotency-Key` | Task assigned to Staff |
| 4 | Staff | Query assigned onboarding task | `GET /api/v1/tasks?org_id=...&assignee_user_id=...` | Visible task list |
| 5 | Staff | Fill missing information in the current agreed channel | Manual reply / Staff daily report / future profile form | Completed fields |
| 6 | Staff | Mark task in progress or completed | `PATCH /api/v1/tasks/{task_id}` with `Idempotency-Key` | Audited task update |
| 7 | Manager | Verify identity fields before the employee enters main workflow | Task state + Agent identity payload | Employee can join Staff daily report flow |

## Suggested onboarding task payload

```json
{
  "tasks": [
    {
      "schema_id": "schema_v1_task",
      "schema_version": "1.0.0",
      "task_id": "TASK-ONBOARDING-<alphanumeric_run_id>",
      "org_id": "org_automage_mvp",
      "department_id": "dept_mvp_core",
      "task_title": "Complete new employee information",
      "task_description": "Confirm org, department, display name, role, manager node, and Agent node before joining the Staff daily report workflow.",
      "source_type": "onboarding_min_flow",
      "source_id": "<request_or_run_id>",
      "creator_user_id": "<manager_user_id>",
      "created_by_node_id": "<manager_node_id>",
      "manager_user_id": "<manager_user_id>",
      "manager_node_id": "<manager_node_id>",
      "assignee_user_id": "<staff_user_id>",
      "assignee_node_id": "<staff_node_id>",
      "priority": "medium",
      "status": "pending",
      "meta": {
        "required_profile_fields": [
          "org_id",
          "department_id",
          "user_id",
          "display_name",
          "role",
          "level",
          "manager_node_id",
          "node_id"
        ]
      }
    }
  ]
}
```

## Acceptance criteria

| Criterion | M2 status |
| --------- | --------- |
| Minimal identity payload is defined | Done |
| Onboarding can be represented by existing task API | Done |
| Staff can query and update onboarding task through existing task APIs | Done through real smoke task query/update coverage |
| Audit/request trace strategy is defined | Done through `X-Request-Id` and `Idempotency-Key` strategy |
| Dedicated profile API is required before M3 production onboarding | Deferred / non-blocking for M2 |

## M3 follow-ups

- Add formal user profile read/update API if backend owner confirms scope.
- Bind Feishu `open_id` roster to backend `user_id` without hardcoding production identifiers.
- Add Landing Page onboarding widgets from `missing_profile_fields` and `onboarding_task_progress` once profile API exists.
- Add staff-facing revision UX for correcting missing or stale information.
