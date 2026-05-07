from __future__ import annotations

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.scheduler import build_scheduler_runtime


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    runtime = build_scheduler_runtime()
    runtime.run_forever()


if __name__ == "__main__":
    main()
