# Database Skill Alignment

This note records how the current Agent-side code aligns with `delivery/database-api-skill`.

## Source delivery

- `delivery/database-skill-delivery-zh.md`
- `delivery/database-api-skill/SKILL.md`
- `delivery/database-api-skill/references/table-map.md`

## Snapshot mode

Snapshot mode keeps Agent workflow payloads flexible and stores an Agent-view JSON record.

- `post_daily_report` -> `AutoMageApiClient.post_staff_report` -> `POST /api/v1/report/staff`
- Mock table: `staff_reports`
- Mock audit table: `audit_logs`

- `generate_manager_report` -> `AutoMageApiClient.post_manager_report` -> `POST /api/v1/report/manager`
- Mock table: `manager_reports`
- Mock audit table: `audit_logs`

This is the path used by the current Feishu/OpenClaw demo flow.

## Formal daily-report mode

Formal mode represents the database Skill delivery path for Markdown daily reports.

- `import_staff_daily_report_from_markdown` -> `AutoMageApiClient.import_staff_daily_report_from_markdown` -> `POST /api/v1/report/staff/import-markdown`
- Mock tables: `form_templates`, `work_records`, `work_record_items`
- Mock audit table: `audit_logs`

- `read_staff_daily_report` -> `AutoMageApiClient.read_staff_daily_report` -> `GET /api/v1/report/staff/{work_record_id}`
- Supported mock formats: `json`, `markdown`

Formal mode is exposed as a separate Staff Skill and is not wired into the existing Feishu daily-report path by default.

## Decision and task path

- `commit_decision` -> `AutoMageApiClient.commit_decision` -> `POST /api/v1/decision/commit`
- Mock table: `agent_decision_logs`
- Compatibility alias: `decision_logs`
- Generated tasks mock table: `task_queue`
- Mock audit table: `audit_logs`

- `fetch_my_tasks` -> `AutoMageApiClient.fetch_tasks` -> `GET /api/v1/tasks`
- Mock table: `task_queue`

## Current boundary

Staff v1 and Manager v1 schema coercion stays in adapter/Skill layers. Database-specific table names are represented in mock state and alignment docs, not hardcoded into business payload construction beyond explicit database Skill methods.

## Real database handoff

The backend owner provided a PostgreSQL database endpoint for later real database validation.

Secrets must not be committed. Put real database credentials only in local `.env` or a secret manager.

Local `.env` keys:

```env
AUTOMAGE_DATABASE_DRIVER=postgresql
AUTOMAGE_DATABASE_HOST=182.92.93.16
AUTOMAGE_DATABASE_PORT=5432
AUTOMAGE_DATABASE_NAME=automage
AUTOMAGE_DATABASE_USER=automage
AUTOMAGE_DATABASE_PASSWORD=your-local-password
```

Safe connectivity check:

```powershell
python scripts/check_database_connection.py
```

Optional PostgreSQL login check, if `psycopg` is installed locally:

```powershell
python scripts/check_database_connection.py --postgres
```

Open confirmation items before real write tests:

- Confirm the database type is PostgreSQL.
- Confirm the external port is `5432`.
- Confirm the server allows inbound access from the local development network.
- Confirm whether direct SQLAlchemy access is allowed, or whether Agent tests must go through FastAPI only.
