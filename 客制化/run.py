#!/usr/bin/env python3
"""
AutoMage 客制化一键运行脚本

使用方法:
    python run.py                    # 运行全链路工作流
    python run.py --server           # 启动 API 服务器
    python run.py --demo             # 运行集成示例
    python run.py --test             # 运行测试
    python run.py --help             # 显示帮助
"""

import argparse
import subprocess
import sys
from pathlib import Path

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    import os
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # 尝试设置控制台代码页为 UTF-8
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCP(65001)
        kernel32.SetConsoleOutputCP(65001)
    except:
        pass
    # 重新配置 stdout 和 stderr
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')


def print_banner():
    """打印横幅"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              AutoMage 客制化 - 一键运行工具                    ║
║                                                               ║
║  为 OpenClaw 和全栈前端提供统一的 Agent Runtime 接口          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)


def run_workflow(verbose: bool = False, use_real_api: bool = False):
    """运行全链路工作流"""
    print("[INFO] 运行全链路工作流...\n")
    cmd = ["python", "scripts/run_full_workflow.py"]
    if verbose:
        cmd.append("--verbose")
    if use_real_api:
        cmd.append("--use-real-api")
    subprocess.run(cmd)


def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """启动 API 服务器"""
    print(f"[INFO] 启动 Agent Runtime 服务器...\n")
    print(f"[ADDRESS] http://{host}:{port}")
    print(f"[API DOCS] http://{host}:{port}/docs")
    print(f"[HEALTH] http://{host}:{port}/api/v1/agent/health\n")

    cmd = ["python", "scripts/start_agent_runtime.py", "--host", host, "--port", str(port)]
    if reload:
        cmd.append("--reload")
    subprocess.run(cmd)


def run_demo():
    """运行集成示例"""
    print("[INFO] 运行集成示例...\n")
    subprocess.run(["python", "examples/integration_demo.py"])


def run_tests(verbose: bool = False):
    """运行测试"""
    print("[INFO] 运行测试...\n")
    cmd = ["pytest", "tests/test_integration_interfaces.py"]
    if verbose:
        cmd.append("-v")
    subprocess.run(cmd)


def show_status():
    """显示系统状态"""
    print("[INFO] 系统状态检查...\n")

    # 检查配置文件
    print("[FILES] 配置文件:")
    config_files = [
        "configs/hermes.example.toml",
        "configs/openclaw.example.toml",
        "configs/automage.example.toml",
    ]
    for config_file in config_files:
        path = Path(config_file)
        status = "[OK]" if path.exists() else "[MISSING]"
        print(f"   {status} {config_file}")

    # 检查关键文件
    print("\n[FILES] 关键文件:")
    key_files = [
        "automage_agents/api/agent_runtime.py",
        "automage_agents/server/app.py",
        "automage_agents/integrations/hermes/runtime.py",
    ]
    for key_file in key_files:
        path = Path(key_file)
        status = "[OK]" if path.exists() else "[MISSING]"
        print(f"   {status} {key_file}")

    # 检查文档
    print("\n[DOCS] 文档:")
    docs = [
        "docs/openclaw_integration_guide.md",
        "docs/frontend_integration_guide.md",
        "docs/INTEGRATION_SUMMARY.md",
    ]
    for doc in docs:
        path = Path(doc)
        status = "[OK]" if path.exists() else "[MISSING]"
        print(f"   {status} {doc}")

    print("\n[OK] 系统状态检查完成")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AutoMage 客制化一键运行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run.py                    # 运行全链路工作流（Mock 模式）
  python run.py --use-real-api     # 运行全链路工作流（真实 API）
  python run.py -v                 # 详细输出
  python run.py --server           # 启动 API 服务器
  python run.py --server --reload  # 启动服务器（热重载）
  python run.py --demo             # 运行集成示例
  python run.py --test             # 运行测试
  python run.py --status           # 显示系统状态
        """,
    )

    parser.add_argument(
        "--server",
        action="store_true",
        help="启动 Agent Runtime API 服务器",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="运行集成示例",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="运行测试",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="显示系统状态",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="服务器监听地址（默认: 0.0.0.0）",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="服务器监听端口（默认: 8000）",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="启用热重载（开发模式）",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="显示详细输出",
    )
    parser.add_argument(
        "--use-real-api",
        action="store_true",
        help="使用真实后端 API（默认使用 Mock）",
    )

    args = parser.parse_args()

    print_banner()

    try:
        if args.server:
            start_server(args.host, args.port, args.reload)
        elif args.demo:
            run_demo()
        elif args.test:
            run_tests(args.verbose)
        elif args.status:
            show_status()
        else:
            # 默认运行全链路工作流
            run_workflow(args.verbose, args.use_real_api)

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
    except Exception as exc:
        print(f"\n\n❌ 执行失败: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
