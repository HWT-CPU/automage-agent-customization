from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.config import load_runtime_settings
from automage_agents.db import Base, create_postgres_engine


def main() -> None:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "configs/automage.local.toml"
    settings = load_runtime_settings(config_path)
    engine = create_postgres_engine(settings.postgres)
    Base.metadata.create_all(engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    main()
