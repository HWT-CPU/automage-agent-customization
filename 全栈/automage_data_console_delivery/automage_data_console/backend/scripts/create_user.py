"""CLI tool to create users with hashed passwords."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import bcrypt
from sqlalchemy import text

from automage_agents.config import load_runtime_settings
from automage_agents.db import create_session_factory


def main():
    parser = argparse.ArgumentParser(description="Create an AutoMage user")
    parser.add_argument("--username", required=True, help="Username")
    parser.add_argument("--password", required=True, help="Password (will be hashed)")
    parser.add_argument("--display-name", default=None, help="Display name (defaults to username)")
    parser.add_argument("--email", default=None, help="Email address")
    parser.add_argument("--role", default="staff", choices=["staff", "manager", "executive", "admin"])
    parser.add_argument("--level", default=None, help="Agent level (l1_staff/l2_manager/l3_executive)")
    parser.add_argument("--department-id", default="dept_mvp_core", help="Department ID")
    parser.add_argument("--org-id", default="org_automage_mvp", help="Organization ID")
    parser.add_argument("--config", default="configs/automage.local.toml", help="Config path")

    args = parser.parse_args()
    settings = load_runtime_settings(args.config)
    session_factory = create_session_factory(settings.postgres)
    db = session_factory()

    display_name = args.display_name or args.username
    level = args.level or {"staff": "l1_staff", "manager": "l2_manager", "executive": "l3_executive", "admin": "l3_executive"}[args.role]

    password_hash = bcrypt.hashpw(args.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    import secrets
    public_id = f"usr_{secrets.token_hex(8)}"

    # Look up org_id
    org = db.execute(
        text("SELECT id FROM organizations WHERE public_id = :pid OR code = :pid LIMIT 1"),
        {"pid": args.org_id},
    ).fetchone()
    org_id = org[0] if org else 1

    # Check existing user
    existing = db.execute(
        text("SELECT id, username FROM users WHERE username = :u AND deleted_at IS NULL"),
        {"u": args.username},
    ).fetchone()

    if existing:
        # Update password and meta
        import json as _json
        new_meta = _json.dumps({"role": args.role, "level": level, "department_id": args.department_id})
        db.execute(
            text("UPDATE users SET password_hash = :ph, email = COALESCE(:em, email), meta = CAST(:meta AS jsonb) WHERE id = :uid"),
            {"ph": password_hash, "em": args.email, "meta": new_meta, "uid": existing[0]},
        )
        db.commit()
        print(f"✅ 用户已存在，已更新密码: {args.username} (id={existing[0]})")
    else:
        db.execute(
            text(
                "INSERT INTO users (public_id, org_id, username, display_name, password_hash, email, status, meta) "
                "VALUES (:pid, :oid, :u, :dn, :ph, :em, 1, CAST(:meta AS jsonb))"
            ),
            {
                "pid": public_id,
                "oid": org_id,
                "u": args.username,
                "dn": display_name,
                "ph": password_hash,
                "em": args.email,
                "meta": f'{{"role": "{args.role}", "level": "{level}", "department_id": "{args.department_id}"}}',
            },
        )
        db.commit()
        new_user = db.execute(text("SELECT id FROM users WHERE username = :u"), {"u": args.username}).fetchone()
        print(f"✅ 用户已创建: {args.username} (id={new_user[0]}, role={args.role}, level={level})")

    db.close()
    print(f"   用户名: {args.username}")
    print(f"   密码:   {args.password}")
    print(f"   角色:   {args.role}")


if __name__ == "__main__":
    main()
