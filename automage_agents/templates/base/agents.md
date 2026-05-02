# AutoMage-2 Base Agent Template

## Template Status

This is an AutoMage-2 draft template.

TODO(Hermes): Convert this file to the official Hermes Agent format after Hermes runtime conventions are confirmed.

## Shared Runtime Principles

- All database writes must go through AutoMage-2 backend APIs.
- Backend APIs and database are the source of truth.
- Local memory and prompt context are auxiliary only.
- Permission control must be enforced by backend auth, not prompt-only rules.
- OpenClaw / Feishu channel logic must stay outside business Skills.
- Skills must remain callable by Hermes, OpenClaw adapters, local scripts, and tests.

## Shared Context Variables

- `user_id`: current business user ID.
- `node_id`: current Agent node ID.
- `role`: `staff`, `manager`, or `executive`.
- `level`: `l1_staff`, `l2_manager`, or `l3_executive`.
- `department_id`: current department scope.
- `manager_node_id`: upstream manager node.

TODO(熊锦文): Confirm backend auth fields and whether `role_id` is required separately.
TODO(OpenClaw): Confirm IM user identity mapping to `user_id` / `node_id`.

## Shared Skills

- `agent_init`: initialize identity and permissions with backend.
- `check_auth_status`: check whether current Agent credentials are still valid.
- `load_user_profile`: load user.md-derived profile.
- `schema_self_correct`: correct schema payload after backend 422 response.

TODO(Hermes): Replace local Skill registry with official Hermes Skill registration.

## Error Handling Baseline

- 422 schema error: request self-correction through Hermes runtime, then retry within limit.
- 401 auth error: stop business action and notify administrator.
- 403 permission error: refuse cross-boundary action.
- 5xx / timeout: retry with exponential backoff.

TODO(熊锦文): Confirm exact backend error code schema.
