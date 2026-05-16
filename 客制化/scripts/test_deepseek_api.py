#!/usr/bin/env python3
"""
测试 DeepSeek API 连接

验证 DeepSeek API Key 是否正常工作。
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from automage_agents.ai.llm_client import LLMClient, LLMMessage


def main():
    print("🧪 测试 DeepSeek API 连接\n")
    
    # 创建客户端（从环境变量加载配置）
    client = LLMClient()
    
    print(f"配置信息:")
    print(f"  Provider: {client.config.provider}")
    print(f"  Model: {client.config.model}")
    print(f"  API Base: {client.config.api_base}")
    print(f"  API Key: {client.config.api_key[:20]}..." if client.config.api_key else "  API Key: None")
    print()
    
    if client.config.provider == "mock":
        print("⚠️  当前使用 Mock 模式")
        print("提示: 请检查 .env 文件中的 LLM_PROVIDER 配置")
        return 1
    
    # 测试简单对话
    print("测试 DeepSeek API 调用...")
    messages = [
        LLMMessage(role="system", content="你是一个有帮助的助手。"),
        LLMMessage(role="user", content="请用一句话介绍 AutoMage 项目。"),
    ]
    
    try:
        response = client.chat(messages)
        print(f"✅ API 调用成功！\n")
        print(f"响应内容:")
        print(f"  {response.content}\n")
        print(f"模型: {response.model}")
        if response.usage:
            print(f"Token 使用: {response.usage}")
        print()
        print("🎉 DeepSeek API 配置正确，可以正常使用！")
        return 0
    except Exception as e:
        print(f"❌ API 调用失败: {e}\n")
        print("请检查:")
        print("  1. API Key 是否正确")
        print("  2. API Base URL 是否正确")
        print("  3. 网络连接是否正常")
        return 1


if __name__ == "__main__":
    sys.exit(main())
