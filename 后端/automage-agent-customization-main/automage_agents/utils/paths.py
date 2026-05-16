from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = PROJECT_ROOT / "automage_agents"
CONFIG_ROOT = PROJECT_ROOT / "configs"
TEMPLATE_ROOT = PACKAGE_ROOT / "templates"
EXAMPLES_ROOT = PROJECT_ROOT / "examples"
