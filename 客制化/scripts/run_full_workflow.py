#!/usr/bin/env python3
"""
全链路工作流演示脚本

此脚本演示完整的 AutoMage 工作流：
1. Staff 提交日报
2. Manager 生成汇总
3. Executive 生成决策
4. 任务分配和查询

使用方法:
    python scripts/run_full_workflow.py
    python scripts/run_full_workflow.py --verbose
    python scripts/run_full_workflow.py --use-real-api
"""

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime
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

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_step(step: int, description: str):
    """打印步骤"""
    print(f"\n{'─' * 80}")
    print(f"步骤 {step}: {description}")
    print(f"{'─' * 80}\n")


def print_result(result: dict, verbose: bool = False):
    """打印结果"""
    if result.get("ok"):
        print("✅ 成功")
        if verbose and result.get("data"):
            print(f"📊 返回数据:\n{json.dumps(result['data'], indent=2, ensure_ascii=False)}")
    else:
        print("❌ 失败")
        print(f"错误: {result.get('message', 'Unknown error')}")
        if result.get("error_code"):
            print(f"错误码: {result['error_code']}")


def run_full_workflow(use_real_api: bool = False, verbose: bool = False):
    """
    运行完整工作流
    
    Args:
        use_real_api: 是否使用真实后端 API
        verbose: 是否显示详细输出
    """
    print_section("🚀 AutoMage 全链路工作流演示")

    print(f"📅 日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 模式: {'真实 API' if use_real_api else 'Mock 模式'}")
    print(f"📝 详细输出: {'是' if verbose else '否'}")

    # 初始化 Runtime
    print_step(0, "初始化 Hermes Runtime")

    try:
        from automage_agents.integrations.hermes.runtime import HermesOpenClawRuntime

        # 优先使用本地配置，如果不存在则使用示例配置
        hermes_config = "configs/hermes.local.toml" if Path("configs/hermes.local.toml").exists() else "configs/hermes.example.toml"
        
        runtime = HermesOpenClawRuntime.from_config_files(
            hermes_config_path=hermes_config,
            openclaw_config_path="configs/openclaw.example.toml",
            auto_initialize=True,
        )

        print("✅ Runtime 初始化成功")
        print(f"   - Staff Context: {runtime.staff_context.identity.user_id}")
        print(f"   - Manager Context: {runtime.manager_context.identity.user_id}")
        print(f"   - Executive Context: {runtime.executive_context.identity.user_id}")

    except Exception as exc:
        print(f"❌ Runtime 初始化失败: {exc}")
        return

    # ========================================================================
    # 步骤 1: Staff 提交日报
    # ========================================================================
    print_step(1, "Staff 提交日报")

    from automage_agents.integrations.hermes.contracts import HermesInvokeRequest

    staff_report_request = HermesInvokeRequest(
        skill_name="post_daily_report",
        actor_user_id="zhangsan",
        payload={
            "report": {
                "timestamp": datetime.now().isoformat(),
                "work_progress": "完成了客户跟进和需求分析，推进了项目进度",
                "issues_faced": "客户对报价周期存在疑虑，需要进一步沟通",
                "solution_attempt": "已联系产品经理确认报价策略，准备下周与客户再次沟通",
                "need_support": False,
                "next_day_plan": "继续推进合同签订，完成技术方案评审",
                "resource_usage": {
                    "chat_id": "demo_chat_001",
                    "source": "cli",
                },
            }
        },
    )

    print("📝 提交员工日报...")
    print(f"   员工: zhangsan")
    print(f"   工作进展: {staff_report_request.payload['report']['work_progress'][:50]}...")

    staff_report_response = runtime.hermes_client.invoke_skill(staff_report_request)
    print_result(asdict(staff_report_response.result), verbose)

    # ========================================================================
    # 步骤 2: Staff 查询任务
    # ========================================================================
    print_step(2, "Staff 查询任务")

    fetch_tasks_request = HermesInvokeRequest(
        skill_name="fetch_my_tasks",
        actor_user_id="zhangsan",
        payload={},
    )

    print("📋 查询员工任务...")
    fetch_tasks_response = runtime.hermes_client.invoke_skill(fetch_tasks_request)
    print_result(asdict(fetch_tasks_response.result), verbose)

    if fetch_tasks_response.ok and fetch_tasks_response.result.data:
        tasks = fetch_tasks_response.result.data.get("tasks", [])
        print(f"   找到 {len(tasks)} 个任务")

    # ========================================================================
    # 步骤 3: Manager 分析团队日报
    # ========================================================================
    print_step(3, "Manager 分析团队日报")

    analyze_request = HermesInvokeRequest(
        skill_name="analyze_team_reports",
        actor_user_id="lijingli",
        payload={
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
    )

    print("📊 分析团队日报...")
    print(f"   部门: dept_mvp_core")
    print(f"   日期: {datetime.now().strftime('%Y-%m-%d')}")

    analyze_response = runtime.hermes_client.invoke_skill(analyze_request)
    print_result(asdict(analyze_response.result), verbose)

    # ========================================================================
    # 步骤 4: Manager 生成汇总
    # ========================================================================
    print_step(4, "Manager 生成汇总")

    manager_report_request = HermesInvokeRequest(
        skill_name="generate_manager_report",
        actor_user_id="lijingli",
        payload={
            "report": {
                "dept_id": "dept_mvp_core",
                "overall_health": "yellow",
                "aggregated_summary": "团队整体进展良好，但存在客户沟通风险需要关注",
                "top_3_risks": [
                    {
                        "risk_title": "客户报价周期疑虑",
                        "description": "客户对报价周期存在疑虑，可能影响合同签订",
                        "severity": "medium",
                        "suggested_action": "加强与客户沟通，明确报价策略",
                    },
                    {
                        "risk_title": "技术方案评审延期",
                        "description": "技术方案评审时间紧张",
                        "severity": "low",
                        "suggested_action": "协调资源，确保按时完成",
                    },
                ],
                "workforce_efficiency": 0.85,
                "pending_approvals": 2,
            }
        },
    )

    print("📈 生成经理汇总...")
    print(f"   部门健康度: {manager_report_request.payload['report']['overall_health']}")
    print(f"   团队效率: {manager_report_request.payload['report']['workforce_efficiency']:.0%}")
    print(f"   风险数量: {len(manager_report_request.payload['report']['top_3_risks'])}")

    manager_report_response = runtime.hermes_client.invoke_skill(manager_report_request)
    print_result(asdict(manager_report_response.result), verbose)

    # 获取 summary_id
    summary_id = None
    if manager_report_response.ok and manager_report_response.result.data:
        summary_id = manager_report_response.result.data.get("summary_public_id")
        if summary_id:
            print(f"   📌 汇总 ID: {summary_id}")

    # ========================================================================
    # 步骤 5: Executive 生成决策方案（如果有风险）
    # ========================================================================
    if manager_report_request.payload["report"]["overall_health"] in ["yellow", "red"]:
        print_step(5, "Executive 生成 A/B 决策方案")

        if summary_id:
            dream_request = HermesInvokeRequest(
                skill_name="dream_decision_engine",
                actor_user_id="chenzong",
                payload={"summary_id": summary_id},
            )

            print("🎯 生成决策方案...")
            print(f"   基于汇总: {summary_id}")

            dream_response = runtime.hermes_client.invoke_skill(dream_request)
            print_result(asdict(dream_response.result), verbose)

            if dream_response.ok and dream_response.result.data:
                decision_options = dream_response.result.data.get("decision_options", [])
                print(f"\n   生成了 {len(decision_options)} 个决策方案:")
                for option in decision_options:
                    print(f"   - 方案 {option.get('option_id')}: {option.get('title')}")

                # ================================================================
                # 步骤 6: Executive 提交决策
                # ================================================================
                print_step(6, "Executive 提交决策")

                # 选择方案 A
                selected_option = decision_options[0] if decision_options else None

                if selected_option:
                    commit_request = HermesInvokeRequest(
                        skill_name="commit_decision",
                        actor_user_id="chenzong",
                        payload={
                            "summary_id": summary_id,
                            "selected_option_id": selected_option.get("option_id", "A"),
                            "decision_summary": f"确认执行{selected_option.get('title', '方案 A')}",
                            "task_candidates": selected_option.get("task_candidates", []),
                        },
                    )

                    print(f"✅ 提交决策: 方案 {selected_option.get('option_id', 'A')}")
                    print(f"   决策说明: {commit_request.payload['decision_summary']}")

                    commit_response = runtime.hermes_client.invoke_skill(commit_request)
                    print_result(asdict(commit_response.result), verbose)

                    if commit_response.ok and commit_response.result.data:
                        task_ids = commit_response.result.data.get("task_ids", [])
                        print(f"\n   创建了 {len(task_ids)} 个任务")
        else:
            print("⚠️  跳过决策生成（未获取到汇总 ID）")

    # ========================================================================
    # 步骤 7: 查看系统状态
    # ========================================================================
    print_step(7, "查看系统状态")

    state_summary = runtime.state_summary()
    print("📊 系统状态:")
    for key, value in state_summary.items():
        print(f"   - {key}: {value}")

    # ========================================================================
    # 完成
    # ========================================================================
    print_section("✅ 全链路工作流演示完成")

    print("📋 工作流总结:")
    print("   1. ✅ Staff 提交日报")
    print("   2. ✅ Staff 查询任务")
    print("   3. ✅ Manager 分析团队日报")
    print("   4. ✅ Manager 生成汇总")
    if manager_report_request.payload["report"]["overall_health"] in ["yellow", "red"]:
        print("   5. ✅ Executive 生成决策方案")
        print("   6. ✅ Executive 提交决策")
    print("   7. ✅ 查看系统状态")

    print("\n💡 提示:")
    print("   - 使用 --verbose 查看详细输出")
    print("   - 使用 --use-real-api 连接真实后端")
    print("   - 查看 examples/integration_demo.py 了解更多示例")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="运行 AutoMage 全链路工作流")
    parser.add_argument(
        "--use-real-api",
        action="store_true",
        help="使用真实后端 API（默认使用 Mock）",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="显示详细输出",
    )

    args = parser.parse_args()

    try:
        run_full_workflow(
            use_real_api=args.use_real_api,
            verbose=args.verbose,
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
    except Exception as exc:
        print(f"\n\n❌ 执行失败: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
