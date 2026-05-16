#!/usr/bin/env python3
"""
启动 Agent Runtime 服务

此脚本启动完整的 Agent Runtime HTTP API 服务，供 OpenClaw 和全栈前端调用。

使用方法:
    python scripts/start_agent_runtime.py
    python scripts/start_agent_runtime.py --host 0.0.0.0 --port 8000
    python scripts/start_agent_runtime.py --reload
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    parser = argparse.ArgumentParser(description="启动 Agent Runtime 服务")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="服务监听地址 (默认: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="服务监听端口 (默认: 8000)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="启用热重载 (开发模式)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["critical", "error", "warning", "info", "debug"],
        help="日志级别 (默认: info)",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("[INFO] 启动 AutoMage Agent Runtime 服务")
    print("=" * 60)
    print(f"[ADDRESS] http://{args.host}:{args.port}")
    print(f"[API DOCS] http://{args.host}:{args.port}/docs")
    print(f"[HEALTH] http://{args.host}:{args.port}/api/v1/agent/health")
    print(f"[RELOAD] {'启用' if args.reload else '禁用'}")
    print(f"[LOG LEVEL] {args.log_level}")
    print("=" * 60)
    print()

    try:
        import uvicorn

        uvicorn.run(
            "automage_agents.server.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
        )
    except ImportError:
        print("[ERROR] 未安装 uvicorn")
        print("请运行: pip install uvicorn")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[INFO] 服务已停止")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
