from __future__ import annotations

import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from psycopg.types.json import Json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.config import load_runtime_settings
from automage_agents.db.postgres import connect_postgres


UTC8 = timezone(timedelta(hours=8))


def zh(text: str) -> str:
    return text.encode("ascii").decode("unicode_escape")


def to_json(value: object) -> Json:
    return Json(value)


def make_public_id(prefix: str, number: int) -> str:
    return f"{prefix}{number:022d}"


def truncate_public_tables(cur) -> list[str]:
    cur.execute(
        """
        select table_name
        from information_schema.tables
        where table_schema = 'public' and table_type = 'BASE TABLE'
        order by table_name
        """
    )
    tables = [row[0] for row in cur.fetchall()]
    if not tables:
        return []

    quoted = ", ".join(f'public."{table}"' for table in tables)
    cur.execute(f"TRUNCATE TABLE {quoted} RESTART IDENTITY CASCADE")
    return tables


def insert_organization(cur, now: datetime) -> int:
    cur.execute(
        """
        insert into organizations (
            public_id, name, code, status, created_at, updated_at, meta
        )
        values (%s, %s, %s, %s, %s, %s, %s)
        returning id
        """,
        (
            make_public_id("ORG", 1),
            zh("\\u661f\\u4e91\\u667a\\u9020\\u79d1\\u6280"),
            "xingyun-tech",
            1,
            now,
            now,
            to_json({"industry": zh("\\u4f01\\u4e1a\\u670d\\u52a1"), "note": zh("\\u4e2d\\u6587\\u6d4b\\u8bd5\\u7ec4\\u7ec7")}),
        ),
    )
    return cur.fetchone()[0]


def insert_roles(cur, org_id: int, now: datetime) -> dict[str, int]:
    roles = [
        ("staff", zh("\\u5458\\u5de5"), zh("\\u4e00\\u7ebf\\u6267\\u884c\\u5458\\u5de5")),
        ("manager", zh("\\u7ecf\\u7406"), zh("\\u90e8\\u95e8\\u8d1f\\u8d23\\u4eba")),
        ("executive", zh("\\u603b\\u76d1"), zh("\\u7ba1\\u7406\\u5c42\\u51b3\\u7b56\\u89d2\\u8272")),
    ]
    role_ids: dict[str, int] = {}
    for index, (code, name, description) in enumerate(roles, start=1):
        cur.execute(
            """
            insert into roles (
                public_id, org_id, code, name, description, status, created_at, updated_at, meta
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            returning id
            """,
            (
                make_public_id("ROL", index),
                org_id,
                code,
                name,
                description,
                1,
                now,
                now,
                to_json({"seed": True}),
            ),
        )
        role_ids[code] = cur.fetchone()[0]
    return role_ids


def insert_users(cur, org_id: int, now: datetime) -> dict[str, int]:
    users = [
        {
            "key": "exec",
            "username": "chenzong",
            "display_name": zh("\\u9648\\u603b"),
            "email": "chenzong@example.com",
            "manager_user_id": None,
            "title": zh("\\u8fd0\\u8425\\u603b\\u76d1"),
        },
        {
            "key": "manager",
            "username": "lijingli",
            "display_name": zh("\\u674e\\u7ecf\\u7406"),
            "email": "lijingli@example.com",
            "manager_user_id": None,
            "title": zh("\\u9500\\u552e\\u7ecf\\u7406"),
        },
        {
            "key": "staff_zhang",
            "username": "zhangsan",
            "display_name": zh("\\u5f20\\u4e09"),
            "email": "zhangsan@example.com",
            "manager_user_id": None,
            "title": zh("\\u9500\\u552e\\u987e\\u95ee"),
        },
        {
            "key": "staff_wang",
            "username": "wangxiaomei",
            "display_name": zh("\\u738b\\u5c0f\\u7f8e"),
            "email": "wangxiaomei@example.com",
            "manager_user_id": None,
            "title": zh("\\u9500\\u552e\\u987e\\u95ee"),
        },
    ]

    user_ids: dict[str, int] = {}
    for index, user in enumerate(users, start=1):
        cur.execute(
            """
            insert into users (
                public_id, org_id, manager_user_id, username, password_hash, display_name,
                email, status, last_login_at, created_at, updated_at, meta
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            returning id
            """,
            (
                make_public_id("USR", index),
                org_id,
                user["manager_user_id"],
                user["username"],
                "demo_password_hash",
                user["display_name"],
                user["email"],
                1,
                now,
                now,
                now,
                to_json({"job_title": user["title"], "seed": True}),
            ),
        )
        user_ids[user["key"]] = cur.fetchone()[0]

    cur.execute(
        "update users set manager_user_id = %s, updated_at = %s where id = %s",
        (user_ids["exec"], now, user_ids["manager"]),
    )
    cur.execute(
        "update users set manager_user_id = %s, updated_at = %s where id in (%s, %s)",
        (user_ids["manager"], now, user_ids["staff_zhang"], user_ids["staff_wang"]),
    )
    return user_ids


def insert_departments(cur, org_id: int, user_ids: dict[str, int], now: datetime) -> dict[str, int]:
    departments = [
        ("sales", zh("\\u9500\\u552e\\u90e8"), "sales", None, user_ids["manager"], 1),
        ("ops", zh("\\u8fd0\\u8425\\u652f\\u6301\\u90e8"), "ops", None, user_ids["exec"], 2),
    ]
    department_ids: dict[str, int] = {}
    for index, (key, name, code, parent_id, manager_user_id, sort_order) in enumerate(departments, start=1):
        cur.execute(
            """
            insert into departments (
                public_id, org_id, parent_id, manager_user_id, name, code, sort_order,
                status, created_at, updated_at, meta
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            returning id
            """,
            (
                make_public_id("DEP", index),
                org_id,
                parent_id,
                manager_user_id,
                name,
                code,
                sort_order,
                1,
                now,
                now,
                to_json({"seed": True}),
            ),
        )
        department_ids[key] = cur.fetchone()[0]
    return department_ids


def insert_department_members(cur, org_id: int, department_ids: dict[str, int], user_ids: dict[str, int], now: datetime) -> None:
    members = [
        (department_ids["sales"], user_ids["manager"], 2, True),
        (department_ids["sales"], user_ids["staff_zhang"], 1, True),
        (department_ids["sales"], user_ids["staff_wang"], 1, True),
        (department_ids["ops"], user_ids["exec"], 2, True),
    ]
    for department_id, user_id, member_type, is_primary in members:
        cur.execute(
            """
            insert into department_members (
                org_id, department_id, user_id, member_type, is_primary, created_at, created_by
            )
            values (%s, %s, %s, %s, %s, %s, %s)
            """,
            (org_id, department_id, user_id, member_type, is_primary, now, user_ids["exec"]),
        )


def insert_user_roles(cur, org_id: int, role_ids: dict[str, int], user_ids: dict[str, int], now: datetime) -> None:
    mappings = [
        (user_ids["exec"], role_ids["executive"]),
        (user_ids["manager"], role_ids["manager"]),
        (user_ids["staff_zhang"], role_ids["staff"]),
        (user_ids["staff_wang"], role_ids["staff"]),
    ]
    for user_id, role_id in mappings:
        cur.execute(
            """
            insert into user_roles (org_id, user_id, role_id, created_at, created_by)
            values (%s, %s, %s, %s, %s)
            """,
            (org_id, user_id, role_id, now, user_ids["exec"]),
        )


def insert_external_identities(cur, org_id: int, user_ids: dict[str, int], now: datetime) -> None:
    identities = [
        (1, user_ids["exec"], zh("\\u9648\\u603b"), "feishu_exec_001"),
        (2, user_ids["manager"], zh("\\u674e\\u7ecf\\u7406"), "feishu_manager_001"),
        (3, user_ids["staff_zhang"], zh("\\u5f20\\u4e09"), "feishu_staff_001"),
        (4, user_ids["staff_wang"], zh("\\u738b\\u5c0f\\u7f8e"), "feishu_staff_002"),
    ]
    for number, user_id, name, external_user_id in identities:
        cur.execute(
            """
            insert into external_identities (
                public_id, org_id, user_id, provider, app_id, tenant_key, external_user_id,
                open_id, union_id, name, avatar_url, status, bound_at, last_synced_at,
                created_at, updated_at, meta
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                make_public_id("EXT", number),
                org_id,
                user_id,
                "feishu",
                "demo-feishu-app",
                "demo-tenant",
                external_user_id,
                f"open_{external_user_id}",
                f"union_{external_user_id}",
                name,
                None,
                1,
                now,
                now,
                now,
                now,
                to_json({"seed": True}),
            ),
        )


def insert_agent_profiles(cur, org_id: int, user_ids: dict[str, int], now: datetime) -> None:
    profiles = [
        (
            1,
            user_ids["staff_zhang"],
            1,
            zh("\\u9500\\u552e\\u65e5\\u62a5\\u52a9\\u624b"),
            zh("\\u8d1f\\u8d23\\u63d0\\u4ea4\\u4e2a\\u4eba\\u65e5\\u62a5\\u3001\\u8ddf\\u8e2a\\u4efb\\u52a1\\u72b6\\u6001\\u3001\\u53cd\\u9988\\u5ba2\\u6237\\u95ee\\u9898\\u3002"),
        ),
        (
            2,
            user_ids["manager"],
            2,
            zh("\\u9500\\u552e\\u7ecf\\u7406\\u6c47\\u603b\\u52a9\\u624b"),
            zh("\\u8d1f\\u8d23\\u6c47\\u603b\\u56e2\\u961f\\u65e5\\u62a5\\u3001\\u8bc6\\u522b\\u98ce\\u9669\\u3001\\u8f93\\u51fa\\u90e8\\u95e8\\u6458\\u8981\\u3002"),
        ),
        (
            3,
            user_ids["exec"],
            3,
            zh("\\u8fd0\\u8425\\u51b3\\u7b56\\u52a9\\u624b"),
            zh("\\u8d1f\\u8d23\\u6839\\u636e\\u6c47\\u603b\\u4fe1\\u606f\\u751f\\u6210\\u51b3\\u7b56\\u5efa\\u8bae\\u5e76\\u4e0b\\u53d1\\u91cd\\u70b9\\u4efb\\u52a1\\u3002"),
        ),
    ]
    for number, user_id, profile_type, title, responsibilities in profiles:
        cur.execute(
            """
            insert into agent_profiles (
                public_id, org_id, user_id, profile_type, status, version, title,
                responsibilities, input_spec, output_spec, system_prompt, persona_prompt,
                tool_config, user_md_raw, created_at, updated_at, meta
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                make_public_id("AGT", number),
                org_id,
                user_id,
                profile_type,
                1,
                1,
                title,
                responsibilities,
                to_json({"required_fields": ["title", "summary"]}),
                to_json({"format": "json"}),
                zh("\\u4f60\\u662f\\u4e00\\u4e2a\\u4e2d\\u6587\\u4e1a\\u52a1\\u52a9\\u624b\\u3002"),
                zh("\\u56de\\u7b54\\u7b80\\u6d01\\u3001\\u6e05\\u6670\\u3001\\u53ef\\u6267\\u884c\\u3002"),
                to_json({"audit": True, "language": "zh-CN"}),
                f"# {title}\n- {responsibilities}",
                now,
                now,
                to_json({"seed": True}),
            ),
        )


def insert_form_template(cur, org_id: int, user_ids: dict[str, int], now: datetime) -> int:
    schema_json = {
        "title": zh("\\u5458\\u5de5\\u65e5\\u62a5\\u6a21\\u677f"),
        "type": "object",
        "properties": {
            "completed_work": {"type": "string", "title": zh("\\u4eca\\u65e5\\u5b8c\\u6210")},
            "issues": {"type": "string", "title": zh("\\u9047\\u5230\\u95ee\\u9898")},
            "support_needed": {"type": "string", "title": zh("\\u9700\\u8981\\u652f\\u6301")},
            "tomorrow_plan": {"type": "string", "title": zh("\\u660e\\u65e5\\u8ba1\\u5212")},
        },
        "required": ["completed_work", "tomorrow_plan"],
    }
    cur.execute(
        """
        insert into form_templates (
            public_id, org_id, name, scope, status, schema_json, version,
            created_at, updated_at, created_by, updated_by, meta
        )
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        returning id
        """,
        (
            make_public_id("TMP", 1),
            org_id,
            zh("\\u4e2d\\u6587\\u5458\\u5de5\\u65e5\\u62a5\\u6a21\\u677f"),
            1,
            1,
            to_json(schema_json),
            1,
            now,
            now,
            user_ids["manager"],
            user_ids["manager"],
            to_json({"seed": True}),
        ),
    )
    return cur.fetchone()[0]


def insert_work_records(cur, org_id: int, department_ids: dict[str, int], template_id: int, user_ids: dict[str, int], now: datetime) -> dict[str, int]:
    records = [
        (
            1,
            user_ids["staff_zhang"],
            zh("\\u5f20\\u4e09 5\\u67086\\u65e5\\u65e5\\u62a5"),
            zh("\\u4eca\\u65e5\\u5b8c\\u62103\\u4f4d\\u91cd\\u70b9\\u5ba2\\u6237\\u8ddf\\u8fdb\\uff0c\\u6574\\u74062\\u4efd\\u62a5\\u4ef7\\u65b9\\u6848\\u3002"),
            zh("\\u5ba2\\u6237\\u5173\\u6ce8\\u4ea4\\u4ed8\\u5468\\u671f\\uff0c\\u9700\\u8981\\u786e\\u8ba4\\u6392\\u671f\\u3002"),
            zh("\\u8bf7\\u7ecf\\u7406\\u534f\\u8c03\\u4ea4\\u4ed8\\u540c\\u4e8b\\u786e\\u8ba4\\u65f6\\u95f4\\u8868\\u3002"),
            zh("\\u7ee7\\u7eed\\u63a8\\u8fdb\\u62a5\\u4ef7\\u8f6c\\u5316\\uff0c\\u5e76\\u56de\\u8bbf\\u91cd\\u70b9\\u5ba2\\u6237\\u3002"),
            {"customer_calls": 6, "quotes": 2},
        ),
        (
            2,
            user_ids["staff_wang"],
            zh("\\u738b\\u5c0f\\u7f8e 5\\u67086\\u65e5\\u65e5\\u62a5"),
            zh("\\u5b8c\\u6210\\u8001\\u5ba2\\u6237\\u7eed\\u8d39\\u6c9f\\u901a\\uff0c\\u63d0\\u4ea41\\u4efd\\u7eed\\u8d39\\u7533\\u8bf7\\u3002"),
            zh("\\u90e8\\u5206\\u5ba2\\u6237\\u5bf9\\u4ef7\\u683c\\u8c03\\u6574\\u8f83\\u654f\\u611f\\u3002"),
            zh("\\u9700\\u8981\\u5e02\\u573a\\u90e8\\u63d0\\u4f9b\\u65b0\\u7248\\u6d3b\\u52a8\\u8bdd\\u672f\\u3002"),
            zh("\\u8ddf\\u8fdb\\u7eed\\u8d39\\u5ba1\\u6279\\uff0c\\u5e76\\u6574\\u7406\\u5ba2\\u6237\\u5f02\\u8bae\\u6e05\\u5355\\u3002"),
            {"renewals": 1, "customer_feedback": 4},
        ),
    ]
    work_record_ids: dict[str, int] = {}
    for number, user_id, title, completed, issues, support_needed, tomorrow_plan, meta in records:
        cur.execute(
            """
            insert into work_records (
                public_id, org_id, department_id, template_id, user_id, record_date, title,
                status, submitted_at, source_type, created_at, updated_at, created_by,
                updated_by, meta
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            returning id
            """,
            (
                make_public_id("WRK", number),
                org_id,
                department_ids["sales"],
                template_id,
                user_id,
                date(2026, 5, 6),
                title,
                1,
                now,
                1,
                now,
                now,
                user_id,
                user_id,
                to_json(meta),
            ),
        )
        work_record_id = cur.fetchone()[0]
        work_record_ids[f"record_{number}"] = work_record_id

        items = [
            ("completed_work", zh("\\u4eca\\u65e5\\u5b8c\\u6210"), "text", 1, completed, None),
            ("issues", zh("\\u9047\\u5230\\u95ee\\u9898"), "text", 2, issues, None),
            ("support_needed", zh("\\u9700\\u8981\\u652f\\u6301"), "text", 3, support_needed, None),
            ("tomorrow_plan", zh("\\u660e\\u65e5\\u8ba1\\u5212"), "text", 4, tomorrow_plan, None),
            ("metrics", zh("\\u8865\\u5145\\u6307\\u6807"), "json", 5, None, meta),
        ]
        for field_key, field_label, field_type, sort_order, value_text, value_json in items:
            cur.execute(
                """
                insert into work_record_items (
                    org_id, work_record_id, field_key, field_label, field_type, sort_order,
                    value_text, value_json, created_at, updated_at, meta
                )
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    org_id,
                    work_record_id,
                    field_key,
                    field_label,
                    field_type,
                    sort_order,
                    value_text,
                    to_json(value_json) if value_json is not None else None,
                    now,
                    now,
                    to_json({"seed": True}),
                ),
            )
    return work_record_ids


def insert_summary(cur, org_id: int, department_ids: dict[str, int], user_ids: dict[str, int], work_record_ids: dict[str, int], now: datetime) -> int:
    cur.execute(
        """
        insert into summaries (
            public_id, org_id, department_id, user_id, summary_type, scope_type, summary_date,
            week_start, status, title, content, source_count, generated_by_type,
            created_at, updated_at, created_by, updated_by, meta
        )
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        returning id
        """,
        (
            make_public_id("SUM", 1),
            org_id,
            department_ids["sales"],
            None,
            1,
            2,
            date(2026, 5, 6),
            date(2026, 5, 4),
            1,
            zh("\\u9500\\u552e\\u90e8 5\\u67086\\u65e5\\u6c47\\u603b"),
            zh("\\u56e2\\u961f\\u4eca\\u65e5\\u91cd\\u70b9\\u63a8\\u8fdb\\u5ba2\\u6237\\u8ddf\\u8fdb\\u4e0e\\u7eed\\u8d39\\u5de5\\u4f5c\\uff0c\\u4e3b\\u8981\\u98ce\\u9669\\u96c6\\u4e2d\\u5728\\u4ea4\\u4ed8\\u5468\\u671f\\u786e\\u8ba4\\u548c\\u4ef7\\u683c\\u5f02\\u8bae\\u5904\\u7406\\u3002"),
            len(work_record_ids),
            2,
            now,
            now,
            user_ids["manager"],
            user_ids["manager"],
            to_json({"risk_level": zh("\\u4e2d"), "seed": True}),
        ),
    )
    summary_id = cur.fetchone()[0]

    for source_id in work_record_ids.values():
        cur.execute(
            """
            insert into summary_source_links (org_id, summary_id, source_type, source_id, created_at)
            values (%s, %s, %s, %s, %s)
            """,
            (org_id, summary_id, 1, source_id, now),
        )
    return summary_id


def insert_decision_record(cur, org_id: int, department_ids: dict[str, int], user_ids: dict[str, int], summary_id: int, source_record_id: int, now: datetime) -> int:
    option_schema_json = {
        "options": [
            {"key": "A", "label": zh("\\u5148\\u786e\\u8ba4\\u4ea4\\u4ed8\\u5468\\u671f\\uff0c\\u518d\\u63a8\\u8fdb\\u7b7e\\u7ea6")},
            {"key": "B", "label": zh("\\u5148\\u63a8\\u8fdb\\u7b7e\\u7ea6\\uff0c\\u518d\\u8865\\u5145\\u4ea4\\u4ed8\\u8bf4\\u660e")},
        ]
    }
    decided_at = now + timedelta(hours=1)
    cur.execute(
        """
        insert into decision_records (
            public_id, org_id, department_id, source_record_id, source_summary_id, related_task_id,
            related_incident_id, requester_user_id, decision_owner_user_id, title, description,
            decision_type, status, priority, option_schema_json, selected_option_key,
            selected_option_label, decision_comment, due_at, decided_at, closed_at, created_at,
            updated_at, created_by, updated_by, meta
        )
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        returning id
        """,
        (
            make_public_id("DEC", 1),
            org_id,
            department_ids["sales"],
            source_record_id,
            summary_id,
            None,
            None,
            user_ids["manager"],
            user_ids["exec"],
            zh("\\u91cd\\u70b9\\u5ba2\\u6237\\u62a5\\u4ef7\\u662f\\u5426\\u7acb\\u5373\\u63a8\\u8fdb"),
            zh("\\u56e2\\u961f\\u9700\\u8981\\u5728\\u4ea4\\u4ed8\\u5468\\u671f\\u5c1a\\u672a\\u5b8c\\u5168\\u786e\\u8ba4\\u524d\\uff0c\\u51b3\\u5b9a\\u662f\\u5426\\u7ee7\\u7eed\\u5411\\u5ba2\\u6237\\u63a8\\u8fdb\\u62a5\\u4ef7\\u3002"),
            1,
            2,
            2,
            to_json(option_schema_json),
            "A",
            zh("\\u5148\\u786e\\u8ba4\\u4ea4\\u4ed8\\u5468\\u671f\\uff0c\\u518d\\u63a8\\u8fdb\\u7b7e\\u7ea6"),
            zh("\\u4f18\\u5148\\u63a7\\u5236\\u5c65\\u7ea6\\u98ce\\u9669\\uff0c\\u907f\\u514d\\u8fc7\\u5ea6\\u627f\\u8bfa\\u3002"),
            now + timedelta(days=1),
            decided_at,
            None,
            now,
            decided_at,
            user_ids["manager"],
            user_ids["exec"],
            to_json({"seed": True}),
        ),
    )
    return cur.fetchone()[0]


def insert_decision_logs(cur, org_id: int, decision_record_id: int, user_ids: dict[str, int], now: datetime) -> None:
    logs = [
        (
            user_ids["manager"],
            1,
            None,
            1,
            None,
            None,
            zh("\\u7ecf\\u7406\\u63d0\\u4ea4\\u5f85\\u51b3\\u7b56\\u4e8b\\u9879"),
            {"stage": "created"},
            now,
        ),
        (
            user_ids["exec"],
            2,
            1,
            2,
            "A",
            zh("\\u5148\\u786e\\u8ba4\\u4ea4\\u4ed8\\u5468\\u671f\\uff0c\\u518d\\u63a8\\u8fdb\\u7b7e\\u7ea6"),
            zh("\\u603b\\u76d1\\u786e\\u8ba4\\u91c7\\u7528\\u7a33\\u59a5\\u63a8\\u8fdb\\u65b9\\u6848"),
            {"stage": "approved"},
            now + timedelta(hours=1),
        ),
    ]
    for actor_user_id, action_type, status_before, status_after, option_key, option_label, comment, payload, event_at in logs:
        cur.execute(
            """
            insert into decision_logs (
                org_id, decision_record_id, actor_user_id, action_type, status_before, status_after,
                selected_option_key, selected_option_label, comment, payload, event_at, created_at
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                org_id,
                decision_record_id,
                actor_user_id,
                action_type,
                status_before,
                status_after,
                option_key,
                option_label,
                comment,
                to_json(payload),
                event_at,
                event_at,
            ),
        )


def insert_tasks(cur, org_id: int, department_ids: dict[str, int], user_ids: dict[str, int], decision_record_id: int, source_record_id: int, now: datetime) -> dict[str, int]:
    tasks = [
        (
            1,
            zh("\\u786e\\u8ba4\\u91cd\\u70b9\\u5ba2\\u6237\\u4ea4\\u4ed8\\u6392\\u671f"),
            zh("\\u8054\\u7cfb\\u4ea4\\u4ed8\\u540c\\u4e8b\\u786e\\u8ba4\\u4e24\\u4e2a\\u91cd\\u70b9\\u5ba2\\u6237\\u7684\\u9884\\u8ba1\\u4e0a\\u7ebf\\u65f6\\u95f4\\uff0c\\u5e76\\u540c\\u6b65\\u7ed9\\u7ecf\\u7406\\u3002"),
            1,
            2,
            user_ids["manager"],
            user_ids["staff_zhang"],
            now + timedelta(days=1),
        ),
        (
            2,
            zh("\\u6574\\u7406\\u7eed\\u8d39\\u5ba2\\u6237\\u5f02\\u8bae\\u6e05\\u5355"),
            zh("\\u68b3\\u7406\\u7eed\\u8d39\\u5ba2\\u6237\\u5bf9\\u4ef7\\u683c\\u8c03\\u6574\\u7684\\u4e3b\\u8981\\u5f02\\u8bae\\uff0c\\u5e76\\u5f62\\u6210\\u4e00\\u9875\\u6c47\\u603b\\u3002"),
            2,
            1,
            user_ids["manager"],
            user_ids["staff_wang"],
            now + timedelta(days=2),
        ),
    ]
    task_ids: dict[str, int] = {}
    for number, title, description, status, priority, creator_user_id, assignee_user_id, due_at in tasks:
        cur.execute(
            """
            insert into tasks (
                public_id, org_id, department_id, decision_record_id, source_record_id, creator_user_id,
                title, description, status, priority, due_at, started_at, closed_at, result_summary,
                created_at, updated_at, created_by, updated_by, meta
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            returning id
            """,
            (
                make_public_id("TSK", number),
                org_id,
                department_ids["sales"],
                decision_record_id if number == 1 else None,
                source_record_id if number == 1 else None,
                creator_user_id,
                title,
                description,
                status,
                priority,
                due_at,
                now if status == 2 else None,
                None,
                None,
                now,
                now,
                creator_user_id,
                creator_user_id,
                to_json({"seed": True}),
            ),
        )
        task_id = cur.fetchone()[0]
        task_ids[f"task_{number}"] = task_id

        cur.execute(
            """
            insert into task_assignments (org_id, task_id, user_id, assignment_type, created_at, created_by)
            values (%s, %s, %s, %s, %s, %s)
            """,
            (org_id, task_id, assignee_user_id, 1, now, creator_user_id),
        )
    return task_ids


def insert_task_updates(cur, org_id: int, task_ids: dict[str, int], user_ids: dict[str, int], now: datetime) -> None:
    updates = [
        (
            task_ids["task_1"],
            user_ids["staff_zhang"],
            1,
            zh("\\u5df2\\u8054\\u7cfb\\u4ea4\\u4ed8\\u540c\\u4e8b\\uff0c\\u9884\\u8ba1\\u4e0b\\u5348\\u7ed9\\u51fa\\u521d\\u6b65\\u6392\\u671f\\u3002"),
            1,
            2,
            now + timedelta(hours=2),
            {"progress": "50%"},
        ),
        (
            task_ids["task_2"],
            user_ids["staff_wang"],
            1,
            zh("\\u5df2\\u6574\\u7406\\u51fa\\u4e09\\u7c7b\\u4ef7\\u683c\\u5f02\\u8bae\\uff0c\\u5f85\\u8865\\u5145\\u5178\\u578b\\u5ba2\\u6237\\u6848\\u4f8b\\u3002"),
            2,
            2,
            now + timedelta(hours=3),
            {"progress": "70%"},
        ),
    ]
    for task_id, actor_user_id, update_type, content, status_before, status_after, event_at, meta in updates:
        cur.execute(
            """
            insert into task_updates (
                org_id, task_id, actor_user_id, update_type, content, status_before,
                status_after, event_at, created_at, meta
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                org_id,
                task_id,
                actor_user_id,
                update_type,
                content,
                status_before,
                status_after,
                event_at,
                event_at,
                to_json(meta),
            ),
        )


def insert_local_helper_data(cur, org_id: int, department_ids: dict[str, int], user_ids: dict[str, int], task_ids: dict[str, int], now: datetime) -> None:
    sessions = [
        ("node-staff-001", "zhangsan", "staff", "line", str(department_ids["sales"]), "node-manager-001"),
        ("node-manager-001", "lijingli", "manager", "manager", str(department_ids["sales"]), "node-exec-001"),
        ("node-exec-001", "chenzong", "executive", "executive", str(department_ids["ops"]), None),
    ]
    for node_id, user_id, role, level, department_id, manager_node_id in sessions:
        cur.execute(
            """
            insert into agent_sessions (
                node_id, user_id, role, level, department_id, manager_node_id, metadata, created_at
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                node_id,
                user_id,
                role,
                level,
                department_id,
                manager_node_id,
                to_json({"seed": True, "language": "zh-CN"}),
                now,
            ),
        )

    cur.execute(
        """
        insert into staff_reports (node_id, user_id, role, report, created_at)
        values (%s, %s, %s, %s, %s), (%s, %s, %s, %s, %s)
        """,
        (
            "node-staff-001",
            "zhangsan",
            "staff",
            to_json({"title": zh("\\u5f20\\u4e09\\u65e5\\u62a5"), "status": "submitted", "language": zh("\\u4e2d\\u6587")}),
            now,
            "node-staff-002",
            "wangxiaomei",
            "staff",
            to_json({"title": zh("\\u738b\\u5c0f\\u7f8e\\u65e5\\u62a5"), "status": "submitted", "language": zh("\\u4e2d\\u6587")}),
            now,
        ),
    )
    cur.execute(
        """
        insert into manager_reports (node_id, user_id, role, report, created_at)
        values (%s, %s, %s, %s, %s)
        """,
        (
            "node-manager-001",
            "lijingli",
            "manager",
            to_json({"title": zh("\\u9500\\u552e\\u90e8\\u6c47\\u603b"), "risk_level": zh("\\u4e2d"), "language": zh("\\u4e2d\\u6587")}),
            now,
        ),
    )
    cur.execute(
        """
        insert into agent_decision_logs (node_id, user_id, role, decision, created_at)
        values (%s, %s, %s, %s, %s)
        """,
        (
            "node-exec-001",
            "chenzong",
            "executive",
            to_json({"selected_option": "A", "comment": zh("\\u5148\\u63a7\\u98ce\\u9669\\u540e\\u63a8\\u8fdb\\u7b7e\\u7ea6")}),
            now,
        ),
    )
    cur.execute(
        """
        insert into task_queue (task_id, assignee_user_id, title, description, status, task_payload, created_at)
        values (%s, %s, %s, %s, %s, %s, %s), (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            f"queue-{task_ids['task_1']}",
            "zhangsan",
            zh("\\u786e\\u8ba4\\u91cd\\u70b9\\u5ba2\\u6237\\u4ea4\\u4ed8\\u6392\\u671f"),
            zh("\\u7528\\u4e8e\\u63a5\\u53e3\\u8054\\u8c03\\u7684\\u961f\\u5217\\u4efb\\u52a1"),
            "pending",
            to_json({"task_ref": task_ids["task_1"], "language": zh("\\u4e2d\\u6587")}),
            now,
            f"queue-{task_ids['task_2']}",
            "wangxiaomei",
            zh("\\u6574\\u7406\\u7eed\\u8d39\\u5ba2\\u6237\\u5f02\\u8bae\\u6e05\\u5355"),
            zh("\\u7528\\u4e8e\\u63a5\\u53e3\\u8054\\u8c03\\u7684\\u961f\\u5217\\u4efb\\u52a1"),
            "in_progress",
            to_json({"task_ref": task_ids["task_2"], "language": zh("\\u4e2d\\u6587")}),
            now,
        ),
    )

    audits = [
        (user_ids["manager"], "form_templates", 1, "seed_create", zh("\\u5df2\\u521b\\u5efa\\u4e2d\\u6587\\u65e5\\u62a5\\u6a21\\u677f")),
        (user_ids["staff_zhang"], "work_records", 1, "seed_create", zh("\\u5df2\\u521b\\u5efa\\u5f20\\u4e09\\u65e5\\u62a5")),
        (user_ids["staff_wang"], "work_records", 2, "seed_create", zh("\\u5df2\\u521b\\u5efa\\u738b\\u5c0f\\u7f8e\\u65e5\\u62a5")),
        (user_ids["exec"], "decision_records", 1, "seed_decision", zh("\\u5df2\\u5199\\u5165\\u51b3\\u7b56\\u793a\\u4f8b")),
    ]
    for actor_user_id, target_type, target_id, action, summary in audits:
        cur.execute(
            """
            insert into audit_logs (
                org_id, actor_user_id, target_type, target_id, action, summary, payload, event_at, created_at
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                org_id,
                actor_user_id,
                target_type,
                target_id,
                action,
                summary,
                to_json({"seed": True, "language": "zh-CN"}),
                now,
                now,
            ),
        )


def collect_counts(cur, tables: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for table in tables:
        cur.execute(f'SELECT COUNT(*) FROM public."{table}"')
        counts[table] = cur.fetchone()[0]
    return counts


def main() -> None:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "configs/automage.local.toml"
    settings = load_runtime_settings(config_path)
    now = datetime(2026, 5, 6, 10, 30, tzinfo=UTC8)

    with connect_postgres(settings.postgres) as conn:
        with conn.cursor() as cur:
            truncated_tables = truncate_public_tables(cur)

            org_id = insert_organization(cur, now)
            role_ids = insert_roles(cur, org_id, now)
            user_ids = insert_users(cur, org_id, now)
            department_ids = insert_departments(cur, org_id, user_ids, now)
            insert_department_members(cur, org_id, department_ids, user_ids, now)
            insert_user_roles(cur, org_id, role_ids, user_ids, now)
            insert_external_identities(cur, org_id, user_ids, now)
            insert_agent_profiles(cur, org_id, user_ids, now)
            template_id = insert_form_template(cur, org_id, user_ids, now)
            work_record_ids = insert_work_records(cur, org_id, department_ids, template_id, user_ids, now)
            summary_id = insert_summary(cur, org_id, department_ids, user_ids, work_record_ids, now)
            decision_record_id = insert_decision_record(
                cur,
                org_id,
                department_ids,
                user_ids,
                summary_id,
                work_record_ids["record_1"],
                now,
            )
            insert_decision_logs(cur, org_id, decision_record_id, user_ids, now)
            task_ids = insert_tasks(
                cur,
                org_id,
                department_ids,
                user_ids,
                decision_record_id,
                work_record_ids["record_1"],
                now,
            )
            insert_task_updates(cur, org_id, task_ids, user_ids, now)
            insert_local_helper_data(cur, org_id, department_ids, user_ids, task_ids, now)
        conn.commit()

        with conn.cursor() as cur:
            counts = collect_counts(
                cur,
                [
                    "organizations",
                    "roles",
                    "users",
                    "departments",
                    "department_members",
                    "user_roles",
                    "external_identities",
                    "agent_profiles",
                    "form_templates",
                    "work_records",
                    "work_record_items",
                    "summaries",
                    "summary_source_links",
                    "decision_records",
                    "decision_logs",
                    "tasks",
                    "task_assignments",
                    "task_updates",
                    "agent_sessions",
                    "staff_reports",
                    "manager_reports",
                    "agent_decision_logs",
                    "task_queue",
                    "audit_logs",
                ],
            )

    print(zh("\\u6570\\u636e\\u5e93\\u5df2\\u6e05\\u7a7a\\u5e76\\u5199\\u5165\\u4e2d\\u6587\\u6d4b\\u8bd5\\u6570\\u636e\\u3002"))
    print(f"{zh('\\u5df2\\u6e05\\u7a7a\\u6570\\u636e\\u8868\\u6570\\u91cf')}: {len(truncated_tables)}")
    print(zh("\\u6838\\u5fc3\\u6570\\u636e\\u7edf\\u8ba1:"))
    for table, count in counts.items():
        print(f"- {table}: {count}")
    print(zh("\\u6d4b\\u8bd5\\u8d26\\u53f7:"))
    print(f"- {zh('\\u9648\\u603b')} / chenzong")
    print(f"- {zh('\\u674e\\u7ecf\\u7406')} / lijingli")
    print(f"- {zh('\\u5f20\\u4e09')} / zhangsan")
    print(f"- {zh('\\u738b\\u5c0f\\u7f8e')} / wangxiaomei")


if __name__ == "__main__":
    main()
