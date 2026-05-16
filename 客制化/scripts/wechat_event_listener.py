"""WeChat 事件监听器 - 接收老板微信回复并路由到 AutoMage"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.config.loader import load_runtime_settings
from automage_agents.core.models import SkillResult
from automage_agents.integrations.wechat.events import WeChatEventAdapter
from automage_agents.integrations.wechat.messages import WeChatMessageAdapter
from automage_agents.integrations.hermes import HermesOpenClawRuntime


def main() -> None:
    args = _parse_args()
    settings = load_runtime_settings(args.settings)
    runtime = _build_runtime(args)
    wechat_adapter = WeChatEventAdapter(user_mapping=_load_user_mapping(args))
    wechat_messages = WeChatMessageAdapter(api_base_url=settings.api_base_url)
    
    if args.dry_run:
        print(json.dumps({
            "ok": True,
            "mode": "dry_run",
            "settings_path": args.settings,
            "backend_mode": settings.backend_mode,
            "api_base_url": settings.api_base_url,
            "wechat_enabled": True,
            "mapped_wechat_ids": sorted(wechat_adapter.user_mapping.keys()),
        }, ensure_ascii=False, indent=2))
        return
    
    print("[INFO] WeChat 监听器启动（Mock 模式）")
    print("[INFO] 生产环境需要对接真实的微信 Webhook")
    print("[INFO] 当前模式：轮询后端 API 获取待处理的决策")
    print("")
    
    # Mock 模式：轮询后端 API
    while True:
        try:
            _poll_and_process(runtime, wechat_adapter, wechat_messages, settings)
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
    runtime: HermesOpenClawRuntime,
    wechat_adapter: WeChatEventAdapter,
    wechat_messages: WeChatMessageAdapter,
    settings: Any,
) -> None:
    """轮询后端 API，获取需要推送的决策"""
    import requests
    
    try:
        response = requests.get(
            f"{settings.api_base_url}/internal/decision-card",
            timeout=10,
        )
        response.raise_for_status()
        data = response.json().get("data", {})
    except Exception as exc:
        print(f"[ERROR] 获取决策卡片失败: {exc}")
        return

    pending_decisions = data.get("pending_decisions", [])
    boss_wechat = data.get("boss_wechat", "o9cq80-4ZTet7x8h6pGOsyDexBik@im.wechat")
    
    if not pending_decisions:
        return
    
    # 推送第一个待处理的决策
    decision = pending_decisions[0]
    decision_id = decision.get("public_id", "")
    title = decision.get("title", "")
    options = decision.get("options", [])
    
    if not options:
        return
    
    print(f"[INFO] 发现待推送决策: {decision_id} - {title}")
    
    # 构建决策卡片
    message = wechat_messages.build_decision_card(
        target_user_id=boss_wechat,
        summary_id=decision_id,
        department="MVP Core",
        decision_options=options,
    )
    
    # 发送消息
    result = wechat_messages.send_message(message)
    
    print(json.dumps({
        "action": "push_decision",
        "decision_id": decision_id,
        "target": boss_wechat,
        "ok": result.get("ok", False),
        "result": result,
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
        description="监听微信消息并路由到 AutoMage Agent Skills"
    )
    parser.add_argument(
        "--settings",
        default=_default_settings_path(),
        help="Runtime settings TOML path",
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
        "--user-map-json",
        help="JSON 文件映射微信 ID 到 AutoMage user_id",
    )
    parser.add_argument(
        "--map",
        action="append",
        default=[],
        help="内联映射，格式: wechat_id=user_id",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=30,
        help="轮询间隔（秒）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="构建 runtime 并打印配置，不启动监听",
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
        wechat_id, sep, user_id = str(item).partition("=")
        if not sep or not wechat_id.strip() or not user_id.strip():
            raise ValueError("--map 格式必须是 wechat_id=user_id")
        mapping[wechat_id.strip()] = user_id.strip()
    return mapping


if __name__ == "__main__":
    main()
