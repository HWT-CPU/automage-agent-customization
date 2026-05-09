from __future__ import annotations

import argparse
import json
import socket
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.config.loader import load_runtime_settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Check AutoMage database settings without printing secrets.")
    parser.add_argument("--settings", default="configs/automage.example.toml")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--postgres", action="store_true", help="Attempt a PostgreSQL login with psycopg if installed.")
    args = parser.parse_args()

    settings = load_runtime_settings(args.settings)
    output: dict[str, Any] = {
        "database_configured": settings.database_configured(),
        "driver": settings.database_driver,
        "host": settings.database_host,
        "port": settings.database_port,
        "name": settings.database_name,
        "user": settings.database_user,
        "password_loaded": bool(settings.database_password),
        "tcp": None,
        "postgres": None,
    }

    if not settings.database_host:
        output["tcp"] = {"ok": False, "message": "AUTOMAGE_DATABASE_HOST or [database].host is not configured."}
        print(json.dumps(output, ensure_ascii=False, indent=2))
        raise SystemExit(1)

    output["tcp"] = _check_tcp(settings.database_host, settings.database_port, args.timeout)
    if args.postgres:
        output["postgres"] = _check_postgres(settings)

    print(json.dumps(output, ensure_ascii=False, indent=2))
    if not output["tcp"]["ok"] or (args.postgres and not output["postgres"]["ok"]):
        raise SystemExit(1)


def _check_tcp(host: str, port: int, timeout: float) -> dict[str, Any]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return {"ok": True, "message": "TCP connection succeeded."}
    except OSError as exc:
        return {"ok": False, "message": str(exc)}


def _check_postgres(settings: Any) -> dict[str, Any]:
    if not settings.database_configured():
        return {"ok": False, "message": "Database host/name/user/password are not fully configured."}
    try:
        import psycopg
    except ImportError:
        return {"ok": False, "message": "psycopg is not installed. Install it only if you need direct PostgreSQL checks."}

    try:
        with psycopg.connect(
            host=settings.database_host,
            port=settings.database_port,
            dbname=settings.database_name,
            user=settings.database_user,
            password=settings.database_password,
            connect_timeout=5,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("select current_database(), current_user")
                database_name, database_user = cursor.fetchone()
        return {"ok": True, "current_database": database_name, "current_user": database_user}
    except Exception as exc:
        return {"ok": False, "message": str(exc)}


if __name__ == "__main__":
    main()
