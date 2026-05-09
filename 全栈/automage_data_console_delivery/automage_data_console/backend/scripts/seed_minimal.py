"""Minimal seed data for development - matches current ORM model schema."""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.config import load_runtime_settings
from automage_agents.db.session import create_postgres_engine, create_session_factory

# User IDs the frontend uses: chenzong, lijingli, zhangsan, wangxiaomei

SEED_SQL = """
-- Organization
INSERT INTO organizations (public_id, name, code)
VALUES ('org_automage_mvp', '星云智造科技', 'xingyun-tech')
ON CONFLICT (code) DO NOTHING;

-- Users
INSERT INTO users (public_id, org_id, username, display_name, manager_user_id, status, meta)
SELECT 'usr_chenzong', id, 'chenzong', '陈总', NULL, 1, '{"job_title":"运营总监"}'
FROM organizations WHERE code = 'xingyun-tech'
AND NOT EXISTS (SELECT 1 FROM users WHERE username = 'chenzong');

INSERT INTO users (public_id, org_id, username, display_name, manager_user_id, status, meta)
SELECT 'usr_lijingli', id, 'lijingli', '李经理', (SELECT id FROM users WHERE username = 'chenzong'), 1, '{"job_title":"销售经理"}'
FROM organizations WHERE code = 'xingyun-tech'
AND NOT EXISTS (SELECT 1 FROM users WHERE username = 'lijingli');

INSERT INTO users (public_id, org_id, username, display_name, manager_user_id, status, meta)
SELECT 'usr_zhangsan', id, 'zhangsan', '张三', (SELECT id FROM users WHERE username = 'lijingli'), 1, '{"job_title":"销售顾问"}'
FROM organizations WHERE code = 'xingyun-tech'
AND NOT EXISTS (SELECT 1 FROM users WHERE username = 'zhangsan');

INSERT INTO users (public_id, org_id, username, display_name, manager_user_id, status, meta)
SELECT 'usr_wangxiaomei', id, 'wangxiaomei', '王小姐', (SELECT id FROM users WHERE username = 'lijingli'), 1, '{"job_title":"销售顾问"}'
FROM organizations WHERE code = 'xingyun-tech'
AND NOT EXISTS (SELECT 1 FROM users WHERE username = 'wangxiaomei');

-- Departments
INSERT INTO departments (public_id, org_id, manager_user_id, name, code, status, meta)
SELECT 'dept_mvp_core', o.id, u.id, '销售部', 'sales', 1, '{}'
FROM organizations o, users u
WHERE o.code = 'xingyun-tech' AND u.username = 'lijingli'
AND NOT EXISTS (SELECT 1 FROM departments WHERE code = 'sales');
""".strip()


def main() -> None:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "configs/automage.local.toml"
    settings = load_runtime_settings(config_path)
    engine = create_postgres_engine(settings.postgres)
    with engine.begin() as conn:
        for statement in SEED_SQL.split(";"):
            stmt = statement.strip()
            if stmt:
                conn.exec_driver_sql(stmt)
    print("Seed data inserted successfully.")


if __name__ == "__main__":
    main()
