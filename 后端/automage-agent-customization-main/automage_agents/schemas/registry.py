from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

SCHEMA_DELIVERY_DIR = Path(__file__).resolve().parents[2] / "里程碑一_杨卓_交付v1.0.0"

SCHEMA_FILES = {
    "schema_v1_staff": "schema_v1_staff.json",
    "schema_v1_manager": "schema_v1_manager.json",
    "schema_v1_executive": "schema_v1_executive.json",
    "schema_v1_task": "schema_v1_task.json",
    "schema_v1_incident": "schema_v1_incident.json",
}


@lru_cache(maxsize=None)
def load_schema(schema_id: str) -> dict[str, Any]:
    file_name = SCHEMA_FILES[schema_id]
    schema_path = SCHEMA_DELIVERY_DIR / file_name
    with schema_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def schema_available(schema_id: str) -> bool:
    file_name = SCHEMA_FILES.get(schema_id)
    return bool(file_name and (SCHEMA_DELIVERY_DIR / file_name).exists())
