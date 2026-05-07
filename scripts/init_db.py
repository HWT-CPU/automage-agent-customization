from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.config import load_runtime_settings
from automage_agents.db import Base, create_postgres_engine


def ensure_postgres_idempotency_constraints(engine) -> None:
    statements = [
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_work_records_org_user_record_date_active
        ON work_records (org_id, user_id, record_date)
        WHERE deleted_at IS NULL
        """,
        """
        ALTER TABLE task_updates
        ADD COLUMN IF NOT EXISTS request_id VARCHAR(128)
        """,
        """
        CREATE INDEX IF NOT EXISTS ix_task_updates_request_id
        ON task_updates (request_id)
        """,
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_task_updates_task_request_id_not_null
        ON task_updates (task_id, request_id)
        WHERE request_id IS NOT NULL
        """,
        """
        UPDATE task_updates
        SET request_id = NULLIF(meta ->> 'request_id', '')
        WHERE request_id IS NULL
        """,
    ]
    with engine.begin() as connection:
        for statement in statements:
            connection.exec_driver_sql(statement)


def main() -> None:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "configs/automage.local.toml"
    settings = load_runtime_settings(config_path)
    engine = create_postgres_engine(settings.postgres)
    Base.metadata.create_all(engine)
    ensure_postgres_idempotency_constraints(engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    main()
