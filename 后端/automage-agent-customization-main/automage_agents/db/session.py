from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from automage_agents.config.settings import PostgresSettings


def build_sqlalchemy_url(settings: PostgresSettings) -> str:
    return (
        f"postgresql+psycopg://{settings.user}:{settings.password or ''}"
        f"@{settings.host}:{settings.port}/{settings.database}"
        f"?sslmode={settings.sslmode}"
    )


def create_postgres_engine(settings: PostgresSettings) -> Engine:
    return create_engine(build_sqlalchemy_url(settings), future=True)


def create_session_factory(settings: PostgresSettings) -> sessionmaker[Session]:
    engine = create_postgres_engine(settings)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
