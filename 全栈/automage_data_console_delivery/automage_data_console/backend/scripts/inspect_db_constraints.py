from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.config import load_runtime_settings
from automage_agents.db.postgres import connect_postgres


def main() -> None:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "configs/automage.local.toml"
    settings = load_runtime_settings(config_path)
    tables = ["summaries", "decision_records", "tasks"]

    with connect_postgres(settings.postgres) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select
                    conrelid::regclass::text as table_name,
                    conname,
                    pg_get_constraintdef(pg_constraint.oid)
                from pg_constraint
                where contype = 'c'
                  and conrelid::regclass::text = any(%s)
                order by conrelid::regclass::text, conname
                """,
                (tables,),
            )
            for table_name, conname, definition in cur.fetchall():
                print(f"{table_name} | {conname} | {definition}")


if __name__ == "__main__":
    main()
