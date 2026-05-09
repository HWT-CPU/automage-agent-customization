from __future__ import annotations

import sys
from pathlib import Path

import uvicorn

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    host = "0.0.0.0"
    port = 8000

    print("AutoMage API 即将启动")
    print(f"Swagger 文档: http://localhost:{port}/docs")
    print(f"OpenAPI JSON: http://localhost:{port}/openapi.json")
    print(f"健康检查: http://localhost:{port}/healthz")
    print("")

    uvicorn.run("automage_agents.server.app:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
