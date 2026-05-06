from __future__ import annotations

from dataclasses import dataclass

import psycopg

from automage_agents.config.settings import PostgresSettings


@dataclass(slots=True)
class PostgresHealthCheckResult:
    ok: bool
    host: str
    port: int
    database: str
    current_user: str | None = None
    server_version: str | None = None
    error: str | None = None


def connect_postgres(settings: PostgresSettings) -> psycopg.Connection:
    return psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=settings.database,
        user=settings.user,
        password=settings.password,
        sslmode=settings.sslmode,
    )


def check_postgres_connection(settings: PostgresSettings) -> PostgresHealthCheckResult:
    try:
        with connect_postgres(settings) as conn:
            with conn.cursor() as cur:
                cur.execute("select current_user, version()")
                current_user, version = cur.fetchone()
        return PostgresHealthCheckResult(
            ok=True,
            host=settings.host,
            port=settings.port,
            database=settings.database,
            current_user=str(current_user),
            server_version=str(version),
        )
    except Exception as exc:
        return PostgresHealthCheckResult(
            ok=False,
            host=settings.host,
            port=settings.port,
            database=settings.database,
            error=str(exc),
        )
