from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from automage_agents.config import load_runtime_settings
from automage_agents.db import create_session_factory


_settings = load_runtime_settings("configs/automage.local.toml")
_session_factory = create_session_factory(_settings.postgres)


def get_db_session() -> Generator[Session, None, None]:
    session = _session_factory()
    try:
        yield session
    finally:
        session.close()
