# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AutoMage is a **multi-agent enterprise workflow platform** with three AI agent tiers:
- **Staff Agent** (L1): Daily reports, task queries/updates
- **Manager Agent** (L2): Team report aggregation, risk identification, task delegation
- **Executive Agent** (L3): Strategic decisions, "Dream" decision engine, strategy broadcast

The main package lives in `客制化/automage_agents/` — that's where all production code is. The `后端/` directory contains backend feedback docs and a snapshot copy.

## Code Architecture

```
客制化/
├── automage_agents/
│   ├── core/           # Enums (AgentRole, AgentLevel), data models (AgentIdentity, SkillResult)
│   ├── config/         # RuntimeSettings, PostgresSettings (env/TOML-driven)
│   ├── server/         # FastAPI app, CRUD routes, middleware, RBAC, audit logging
│   ├── db/             # SQLAlchemy ORM models (20+ tables), session management
│   ├── agents/         # Agent template registry (base/staff/manager/executive)
│   ├── skills/         # Per-tier skill implementations + registry + context
│   ├── schemas/        # Schema definitions, persistence, parsing, rendering
│   ├── api/            # HTTP client, mock client, SQLAlchemy-backed client
│   ├── integrations/   # Feishu (Lark), Hermes, OpenClaw adapters + event router
│   ├── knowledge/      # Feishu wiki sync, auto-context, payload enrichment
│   ├── scheduler/      # Background cron scheduler for reminders/auto-generation
│   └── templates/      # Agent prompt builder templates
├── scripts/            # CLI entrypoints (run_api, run_scheduler, demo_mock_flow, etc.)
├── tests/              # Pytest test suite
├── configs/            # TOML config files (automage.example.toml, etc.)
└── docs/               # Deployment docs, swagger test flows
```

### Key Design Principles

- **Three isolated tiers** with RBAC enforcement: Staff can only read/write own data, Manager sees department scope, Executive has global access.
- **Database is source of truth** — local memory is auxiliary context.
- **API client abstraction**: `api/client.py` (HTTP) and `api/mock_client.py` / `api/sqlalchemy_client.py` backends, switchable via config.
- **Integrations are adapters**: Feishu, Hermes, OpenClaw logic stays out of business skills.
- **Idempotency & conflict detection**: Write-protected paths use request_id/idempotency-key for safe retries.
- **Audit trail**: All write operations log to `audit_logs` table.

### Critical Models

- `AgentIdentity`: node_id, user_id, role, level, department_id — carried through every skill call
- `SkillResult`: ok bool + data dict — the return type of every skill function
- `RuntimeContextV0`: workflow context (org_id, run_date, source_channel)
- `SkillContext`: holds settings, api_client, user_profile, runtime — passed as first arg to all skills

### Key Flows

1. **Staff Daily Report**: POST /api/v1/report/staff → conflict check on (org_id, user_id, record_date) → persists work_record + items + optional incident + audit log
2. **Manager Summary**: POST /api/v1/report/manager → aggregates staff reports → creates SummaryModel + summary_source_links + snapshot
3. **Dream Decision**: POST /internal/dream/run → generates A/B decision options from a manager summary
4. **Decision Commit**: POST /api/v1/decision/commit → creates decision_record → optionally creates tasks + task_assignments + task_queue entries

## Commands

```bash
# Start with Docker
docker compose up -d --build

# Start API server locally
python scripts/run_api.py

# Start background scheduler
python scripts/run_scheduler.py

# Initialize database schema
python scripts/init_db.py

# Run end-to-end mock demo
python scripts/demo_mock_flow.py

# Run all tests
pytest

# Run a single test file
pytest tests/test_staff_daily_report_parser.py -v

# Run tests matching a keyword
pytest -k test_idempotency

# Smoke test against real API
python scripts/smoke_real_api.py

# Verify backend acceptance criteria
python scripts/verify_backend_acceptance.py

# Render agent templates
python scripts/render_agents.py --user examples/user.staff.example.toml --output /tmp/agents.md
```

## Configuration

Settings are loaded from environment (prefix `AUTOMAGE_`) or `configs/automage.local.toml`. Key toggles:
- `AUTOMAGE_RBAC_ENABLED` — RBAC enforcement (default: true)
- `AUTOMAGE_ABUSE_PROTECTION_ENABLED` — rate limiting + idempotency
- `AUTOMAGE_AUDIT_ENABLED` — write audit logs
- `AUTOMAGE_SCHEDULER_ENABLED` — background cron jobs
- `AUTOMAGE_BACKEND_MODE` — `http` (real API) or `mock` or `sqlalchemy`
