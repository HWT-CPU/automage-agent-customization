#!/usr/bin/env python3
"""
测试 AI 集成功能

验证 LLM 客户端和分析服务是否正常工作。
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from automage_agents.ai.llm_client import LLMClient, LLMConfig, LLMMessage
from automage_agents.ai.analysis_service import AnalysisService


def test_llm_client():
    """测试 LLM 客户端"""
    print("=" * 60)
    print("测试 1: LLM 客户端")
    print("=" * 60)
    
    # 创建客户端（使用环境变量配置）
    client = LLMClient()
    print(f"✅ LLM 客户端创建成功")
    print(f"   Provider: {client.config.provider}")
    print(f"   Model: {client.config.model}")
    print(f"   Temperature: {client.config.temperature}")
    print()
    
    # 测试简单对话
    print("测试简单对话...")
    messages = [
        LLMMessage(role="system", content="你是一个有帮助的助手。"),
        LLMMessage(role="user", content="请用一句话介绍 AutoMage 项目。"),
    ]
    
    try:
        response = client.chat(messages)
        print(f"✅ LLM 响应成功")
        print(f"   内容: {response.content[:100]}...")
        print(f"   模型: {response.model}")
        if response.usage:
            print(f"   Token 使用: {response.usage}")
        print()
    except Exception as e:
        print(f"❌ LLM 调用失败: {e}")
        print()
        return False
    
    return True


def test_analysis_service():
    """测试分析服务"""
    print("=" * 60)
    print("测试 2: 分析服务")
    print("=" * 60)
    
    service = AnalysisService()
    print(f"✅ 分析服务创建成功")
    print()
    
    # 测试团队日报分析
    print("测试团队日报分析...")
    mock_reports = [
        {
            "user_id": "zhangsan",
            "work_progress": "完成了客户需求分析，推进了合同签订流程",
            "issues_faced": "客户对报价周期存在疑虑",
            "next_day_plan": "继续跟进合同签订，准备技术方案评审",
        },
        {
            "user_id": "lisi",
            "work_progress": "完成了技术方案设计，准备评审材料",
            "issues_faced": "评审时间紧张，需要协调资源",
            "next_day_plan": "完成技术方案评审，开始开发工作",
        },
    ]
    
    try:
        analysis = service.analyze_team_reports(
            reports=mock_reports,
            department="dept_mvp_core",
            date="2026-05-13",
        )
        print(f"✅ 日报分析成功")
        print(f"   整体健康度: {analysis.get('overall_health', 'unknown')}")
        print(f"   需要上报: {analysis.get('escalation_required', False)}")
        print(f"   风险数量: {len(analysis.get('top_3_risks', []))}")
        print(f"   汇总: {analysis.get('aggregated_summary', '')[:100]}...")
        print()
    except Exception as e:
        print(f"❌ 日报分析失败: {e}")
        print()
        return False
    
    # 测试汇总生成
    print("测试汇总生成...")
    try:
        summary = service.generate_manager_summary(
            analysis=analysis,
            department="dept_mvp_core",
            date="2026-05-13",
        )
        print(f"✅ 汇总生成成功")
        print(f"   汇总内容: {summary[:150]}...")
        print()
    except Exception as e:
        print(f"❌ 汇总生成失败: {e}")
        print()
        return False
    
    # 测试决策方案生成
    print("测试决策方案生成...")
    mock_manager_summary = {
        "summary_public_id": "MSUM-test-001",
        "overall_health": "yellow",
        "aggregated_summary": analysis.get("aggregated_summary", ""),
        "top_3_risks": analysis.get("top_3_risks", []),
    }
    
    try:
        decision = service.generate_decision_options(
            manager_summary=mock_manager_summary,
            department="dept_mvp_core",
            date="2026-05-13",
        )
        print(f"✅ 决策方案生成成功")
        options = decision.get("decision_options", [])
        print(f"   方案数量: {len(options)}")
        for option in options:
            print(f"   - 方案 {option.get('option_id', '?')}: {option.get('title', 'unknown')}")
            print(f"     策略: {option.get('summary', '')[:80]}...")
            print(f"     任务数: {len(option.get('task_candidates', []))}")
        print()
    except Exception as e:
        print(f"❌ 决策方案生成失败: {e}")
        print()
        return False
    
    return True


def main():
    print()
    print("🧪 AutoMage AI 集成测试")
    print()
    
    # 测试 LLM 客户端
    llm_ok = test_llm_client()
    
    # 测试分析服务
    analysis_ok = test_analysis_service()
    
    # 总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"LLM 客户端: {'✅ 通过' if llm_ok else '❌ 失败'}")
    print(f"分析服务: {'✅ 通过' if analysis_ok else '❌ 失败'}")
    print()
    
    if llm_ok and analysis_ok:
        print("🎉 所有测试通过！AI 集成正常工作。")
        print()
        print("下一步：")
        print("1. 如果使用 Mock 模式，配置真实 LLM API Key")
        print("2. 运行全链路工作流: python run.py workflow --use-real-api")
        print("3. 查看 AI_INTEGRATION_GUIDE.md 了解更多")
        return 0
    else:
        print("❌ 部分测试失败，请检查配置和日志。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
