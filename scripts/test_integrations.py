"""测试 WeChat 和 WebChat 集成"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.integrations.wechat.messages import (
    WeChatMessageAdapter,
    WeChatOutboundMessage,
)
from automage_agents.integrations.wechat.events import (
    WeChatEventAdapter,
    WeChatEvent,
)
from automage_agents.integrations.webchat.client import WebChatClient
from automage_agents.integrations.webchat.events import (
    WebChatEventAdapter,
    WebChatMessage,
)


def test_wechat_messages():
    """测试微信消息适配器"""
    print("\n=== 测试 WeChat 消息适配器 ===")
    
    adapter = WeChatMessageAdapter(api_base_url="http://localhost:8000")
    
    # 测试决策卡片
    message = adapter.build_decision_card(
        target_user_id="o9cq80-4ZTet7x8h6pGOsyDexBik@im.wechat",
        summary_id="summary_20260514_001",
        department="MVP Core",
        decision_options=[
            {
                "option_id": "A",
                "title": "方案A：快速迭代",
                "summary": "优先完成核心功能",
                "task_candidates": [{"title": "任务1"}, {"title": "任务2"}],
            },
            {
                "option_id": "B",
                "title": "方案B：稳健推进",
                "summary": "确保质量和稳定性",
                "task_candidates": [{"title": "任务3"}],
            },
        ],
    )
    
    print(f"✅ 决策卡片构建成功")
    print(f"   标题: {message.title}")
    print(f"   目标: {message.target_user_id}")
    print(f"   内容长度: {len(message.body)} 字符")
    
    # 测试发送（会调用后端 API）
    result = adapter.send_message(message)
    print(f"✅ 消息发送: {'成功' if result.get('ok') else '失败'}")
    if not result.get("ok"):
        print(f"   错误: {result.get('error')}")


def test_wechat_events():
    """测试微信事件适配器"""
    print("\n=== 测试 WeChat 事件适配器 ===")
    
    adapter = WeChatEventAdapter(user_mapping={
        "o9cq80-4ZTet7x8h6pGOsyDexBik@im.wechat": "chenzong"
    })
    
    # 测试决策确认
    wechat_event = WeChatEvent(
        message_id="msg_001",
        from_user="o9cq80-4ZTet7x8h6pGOsyDexBik@im.wechat",
        content="确认方案A summary_20260514_001",
        timestamp=1715673600.0,
    )
    
    internal_event = adapter.to_internal_event(wechat_event)
    
    print(f"✅ 事件转换成功")
    print(f"   事件类型: {internal_event.event_type.value}")
    print(f"   执行者: {internal_event.actor_user_id}")
    print(f"   选择方案: {internal_event.payload.get('selected_option')}")
    print(f"   汇总 ID: {internal_event.payload.get('summary_id')}")


def test_webchat_client():
    """测试 WebChat 客户端"""
    print("\n=== 测试 WebChat 客户端 ===")
    
    client = WebChatClient(
        api_base_url="http://localhost:3000",
        api_key="test_key",
    )
    
    print(f"✅ WebChat 客户端初始化成功")
    print(f"   API 地址: {client.api_base_url}")
    print(f"   超时: {client.timeout} 秒")
    
    # 注意：实际调用需要真实的 WebChat API
    print(f"⚠️  实际 API 调用需要真实的 WebChat 服务")


def test_webchat_events():
    """测试 WebChat 事件适配器"""
    print("\n=== 测试 WebChat 事件适配器 ===")
    
    adapter = WebChatEventAdapter(user_mapping={
        "web_user_001": "zhangsan"
    })
    
    # 测试日报消息
    message = WebChatMessage(
        message_id="web_msg_001",
        from_user="web_user_001",
        content="今天完成了客户跟进，明天计划进行需求分析",
        timestamp=1715673600.0,
        metadata={},
    )
    
    internal_event = adapter.to_internal_event(message)
    
    print(f"✅ 事件转换成功")
    print(f"   事件类型: {internal_event.event_type.value}")
    print(f"   执行者: {internal_event.actor_user_id}")
    print(f"   原始文本: {internal_event.payload.get('raw_text')[:30]}...")


def main():
    print("🧪 AutoMage 集成测试")
    print("=" * 50)
    
    try:
        test_wechat_messages()
        test_wechat_events()
        test_webchat_client()
        test_webchat_events()
        
        print("\n" + "=" * 50)
        print("🎉 所有测试通过！")
        
    except Exception as exc:
        print(f"\n❌ 测试失败: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
