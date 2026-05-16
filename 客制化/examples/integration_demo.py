#!/usr/bin/env python3
"""
集成示例 - 演示 OpenClaw 和前端如何调用客制化接口

此脚本展示：
1. OpenClaw 本地 Python 集成
2. 前端 HTTP API 调用模拟
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def demo_openclaw_integration():
    """演示 OpenClaw 本地 Python 集成"""
    print("=" * 60)
    print("📦 OpenClaw 本地 Python 集成示例")
    print("=" * 60)

    from automage_agents.integrations.hermes.client import LocalHermesClient
    from automage_agents.integrations.hermes.contracts import HermesInvokeRequest
    from automage_agents.integrations.hermes.runtime import HermesOpenClawRuntime

    # 1. 初始化 Runtime
    print("\n1️⃣ 初始化 Hermes Runtime...")
    runtime = HermesOpenClawRuntime.from_config_files(
        hermes_config_path="configs/hermes.example.toml",
        openclaw_config_path="configs/openclaw.example.toml",
        auto_initialize=True,
    )
    hermes_client = runtime.hermes_client
    print("   ✅ Runtime 初始化成功")

    # 2. 调用 fetch_my_tasks Skill
    print("\n2️⃣ 调用 fetch_my_tasks Skill...")
    request = HermesInvokeRequest(
        skill_name="fetch_my_tasks",
        actor_user_id="zhangsan",
        payload={},
    )
    response = hermes_client.invoke_skill(request)

    print(f"   ✅ 调用成功: {response.ok}")
    print(f"   📊 返回数据: {json.dumps(response.result.data, indent=2, ensure_ascii=False)}")

    # 3. 调用 post_daily_report Skill
    print("\n3️⃣ 调用 post_daily_report Skill...")
    request = HermesInvokeRequest(
        skill_name="post_daily_report",
        actor_user_id="zhangsan",
        payload={
            "timestamp": "2026-05-13T10:00:00+08:00",
            "work_progress": "完成了客户跟进",
            "issues_faced": "报价周期不明确",
            "solution_attempt": "已联系产品经理确认",
            "need_support": False,
            "next_day_plan": "继续推进合同签订",
            "resource_usage": {},
        },
    )
    response = hermes_client.invoke_skill(request)

    print(f"   ✅ 调用成功: {response.ok}")
    if response.ok:
        print(f"   📊 返回数据: {json.dumps(response.result.data, indent=2, ensure_ascii=False)}")
    else:
        print(f"   ❌ 错误: {response.result.message}")
        print(f"   🔍 错误码: {response.result.error_code}")

    print("\n" + "=" * 60)


def demo_frontend_http_integration():
    """演示前端 HTTP API 调用（需要先启动服务）"""
    print("=" * 60)
    print("🌐 前端 HTTP API 集成示例")
    print("=" * 60)

    try:
        import requests
    except ImportError:
        print("\n❌ 错误: 未安装 requests 库")
        print("请运行: pip install requests")
        return

    base_url = "http://localhost:8000"

    # 1. 健康检查
    print("\n1️⃣ 健康检查...")
    try:
        response = requests.get(f"{base_url}/api/v1/agent/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 服务状态: {data['status']}")
            print(f"   📊 可用 Skills: {data['available_skills']}")
        else:
            print(f"   ❌ 健康检查失败: HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ 无法连接到服务")
        print("   💡 请先启动服务: python scripts/start_agent_runtime.py")
        return
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return

    # 2. 查询可用 Skills
    print("\n2️⃣ 查询可用 Skills...")
    try:
        response = requests.get(
            f"{base_url}/api/v1/agent/skills",
            params={"agent_type": "staff"},
            headers={
                "X-User-Id": "zhangsan",
                "X-Role": "staff",
            },
            timeout=5,
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 找到 {len(data['skills'])} 个 Skills:")
            for skill in data["skills"][:5]:  # 只显示前 5 个
                print(f"      - {skill['name']}: {skill['description']}")
        else:
            print(f"   ❌ 查询失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")

    # 3. 运行 Skill - 查询任务
    print("\n3️⃣ 运行 Skill - 查询任务...")
    try:
        response = requests.post(
            f"{base_url}/api/v1/agent/run",
            json={
                "agent_type": "staff",
                "org_id": "org_automage_mvp",
                "user_id": "zhangsan",
                "node_id": "staff_agent_mvp_001",
                "run_date": "2026-05-13",
                "input": {
                    "skill_name": "fetch_my_tasks",
                    "skill_args": {},
                },
            },
            headers={
                "Content-Type": "application/json",
                "X-User-Id": "zhangsan",
                "X-Role": "staff",
                "X-Node-Id": "staff_agent_mvp_001",
            },
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 调用成功: {data['ok']}")
            print(f"   📊 Schema ID: {data['output_schema_id']}")
            print(f"   🔍 Trace ID: {data['trace_id']}")
            print(f"   📦 输出数据: {json.dumps(data['output'], indent=2, ensure_ascii=False)}")
        else:
            print(f"   ❌ 调用失败: HTTP {response.status_code}")
            print(f"   📄 响应: {response.text}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")

    # 4. 运行 Skill - 提交日报
    print("\n4️⃣ 运行 Skill - 提交日报...")
    try:
        response = requests.post(
            f"{base_url}/api/v1/agent/run",
            json={
                "agent_type": "staff",
                "org_id": "org_automage_mvp",
                "user_id": "zhangsan",
                "node_id": "staff_agent_mvp_001",
                "run_date": "2026-05-13",
                "input": {
                    "skill_name": "post_daily_report",
                    "skill_args": {
                        "timestamp": "2026-05-13T10:00:00+08:00",
                        "work_progress": "完成了客户跟进",
                        "issues_faced": "报价周期不明确",
                        "solution_attempt": "已联系产品经理确认",
                        "need_support": False,
                        "next_day_plan": "继续推进合同签订",
                        "resource_usage": {},
                    },
                },
            },
            headers={
                "Content-Type": "application/json",
                "X-User-Id": "zhangsan",
                "X-Role": "staff",
                "X-Node-Id": "staff_agent_mvp_001",
            },
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 调用成功: {data['ok']}")
            if data["ok"]:
                print(f"   📊 返回数据: {json.dumps(data['output'], indent=2, ensure_ascii=False)}")
            else:
                print(f"   ⚠️ 警告: {', '.join(data['warnings'])}")
        else:
            print(f"   ❌ 调用失败: HTTP {response.status_code}")
            print(f"   📄 响应: {response.text}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")

    print("\n" + "=" * 60)


def main():
    """主函数"""
    print("\n🎯 AutoMage 客制化集成示例\n")

    # 1. OpenClaw 本地集成
    try:
        demo_openclaw_integration()
    except Exception as e:
        print(f"\n❌ OpenClaw 集成示例失败: {e}")
        import traceback

        traceback.print_exc()

    print("\n")

    # 2. 前端 HTTP 集成
    try:
        demo_frontend_http_integration()
    except Exception as e:
        print(f"\n❌ 前端 HTTP 集成示例失败: {e}")
        import traceback

        traceback.print_exc()

    print("\n✅ 示例运行完成\n")


if __name__ == "__main__":
    main()
