"""WebChat 事件监听器 - 接收 Web 聊天消息并路由到 AutoMage"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.config.loader import load_runtime_settings
from automage_agents.integrations.webchat.client import WebChatClient
from automage_agents.integrations.webchat.events import WebChatEventAdapter
from automage_agents.integrations.hermes import HermesOpenClawRuntime


def main() -> None:
    args = _parse_args()
    settings = load_runtime_settings(args.settings)
    runtime = _build_runtime(args)
    
    webchat_client = WebChatClient(
        api_base_url=args.webchat_api_url,
        api_key=args.webchat_api_key,
    )
    webchat_adapter = WebChatEventAdapter(
        user_mapping=_load_user_mapping(args)
    )
    
    if args.dry_run:
        print(json.dumps({
            "ok": True,
            "mode": "dry_run",
            "webchat_api_url": args.webchat_api_url,
            "mapped_users": sorted(webchat_adapter.user_mapping.keys()),
        }, ensure_ascii=False, indent=2))
        return
    
    print("[INFO] WebChat 监听器启动")
    print(f"[INFO] WebChat API: {args.webchat_api_url}")
    print(f"[INFO] 轮询间隔: {args.poll_interval} 秒")
    print("")
    
    while True:
        try:
            _poll_and_process(
                webchat_client,
                webchat_adapter,
                runtime,
            )
            time.sleep(args.poll_interval)
        except KeyboardInterrupt:
            print("\n[INFO] 监听器已停止")
            break
        except Exception as exc:
            print(json.dumps({
                "ok": False,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(limit=8),
            }, ensure_ascii=False, indent=2))
            time.sleep(args.poll_interval)


def _poll_and_process(
    webchat_client: WebChatClient,
    webchat_adapter: WebChatEventAdapter,
    runtime: HermesOpenClawRuntime,
) -> None:
    """轮询并处理 WebChat 消息"""
    messages = webchat_client.get_pending_messages()
    
    if not messages:
        return
    
    print(f"[INFO] 收到 {len(messages)} 条待处理消息")
    
    for raw_message in messages:
        try:
            message = webchat_adapter.from_webchat_message(raw_message)
            internal_event = webchat_adapter.to_internal_event(message)
            
            # 处理事件
            result = runtime.openclaw.handle_event(internal_event)
            
            # 发送回复
            if result.ok:
                reply_text = result.message or "已处理"
                webchat_client.send_reply(message.message_id, reply_text)
            
            # 标记为已处理
            webchat_client.mark_as_processed(message.message_id)
            
            print(json.dumps({
                "message_id": message.message_id,
                "from_user": message.from_user,
                "event_type": internal_event.event_type.value,
                "ok": result.ok,
                "message": result.message,
            }, ensure_ascii=False, indent=2))
            
        except Exception as exc:
            print(json.dumps({
                "ok": False,
                "message_id": raw_message.get("id"),
                "error_type": type(exc).__name__,
                "error": str(exc),
            }, ensure_ascii=False, indent=2))


def _build_runtime(args: argparse.Namespace) -> HermesOpenClawRuntime:
    return HermesOpenClawRuntime.from_demo_configs(
        staff_user_path=args.staff_profile,
        manager_user_path=args.manager_profile,
        executive_user_path=args.executive_profile,
        settings_path=args.settings,
        user_mapping={},
        auto_initialize=not args.dry_run,
    )



def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="监听 WebChat 消息并路由到 AutoMage"
    )
    parser.add_argument(
        "--settings",
        default=_default_settings_path(),
    )
    parser.add_argument(
        "--staff-profile",
        default=_default_profile_path("staff"),
    )
    parser.add_argument(
        "--manager-profile",
        default=_default_profile_path("manager"),
    )
    parser.add_argument(
        "--executive-profile",
        default=_default_profile_path("executive"),
    )
    parser.add_argument(
        "--webchat-api-url",
        default=os.getenv("WEBCHAT_API_URL", "http://localhost:3000"),
        help="WebChat API 地址",
    )
    parser.add_argument(
        "--webchat-api-key",
        default=os.getenv("WEBCHAT_API_KEY", ""),
        help="WebChat API Key",
    )
    parser.add_argument(
        "--user-map-json",
        help="JSON 文件映射 WebChat user_id 到 AutoMage user_id",
    )
    parser.add_argument(
        "--map",
        action="append",
        default=[],
        help="内联映射，格式: webchat_id=user_id",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=10,
        help="轮询间隔（秒）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
    )
    return parser.parse_args()


def _default_settings_path() -> str:
    config_override = os.getenv("AUTOMAGE_CONFIG_PATH", "").strip()
    if config_override:
        return config_override
    local_config = PROJECT_ROOT / "configs" / "automage.local.toml"
    if local_config.exists():
        return str(local_config)
    return str(PROJECT_ROOT / "configs" / "automage.example.toml")


def _default_profile_path(role: str) -> str:
    local_profile = PROJECT_ROOT / "examples" / f"user.{role}.local.toml"
    if local_profile.exists():
        return str(local_profile)
    return str(PROJECT_ROOT / "examples" / f"user.{role}.example.toml")


def _load_user_mapping(args: argparse.Namespace) -> dict[str, str]:
    mapping: dict[str, str] = {}
    if args.user_map_json:
        raw = json.loads(Path(args.user_map_json).read_text(encoding="utf-8-sig"))
        if not isinstance(raw, dict):
            raise ValueError("--user-map-json 必须是 JSON 对象")
        mapping.update({str(k): str(v) for k, v in raw.items()})
    for item in args.map:
        webchat_id, sep, user_id = str(item).partition("=")
        if not sep or not webchat_id.strip() or not user_id.strip():
            raise ValueError("--map 格式必须是 webchat_id=user_id")
        mapping[webchat_id.strip()] = user_id.strip()
    return mapping


if __name__ == "__main__":
    main()
