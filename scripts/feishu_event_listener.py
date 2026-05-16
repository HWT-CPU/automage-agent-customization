from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.config.loader import load_runtime_settings
from automage_agents.core.models import SkillResult
from automage_agents.integrations.feishu.messages import FeishuMessageAdapter
from automage_agents.integrations.hermes import HermesOpenClawRuntime


def _load_lark_sdk():
    try:
        import lark_oapi as lark
    except ImportError as exc:
        raise RuntimeError("Missing dependency: install lark-oapi first, e.g. `python -m pip install -e .` or `python -m pip install lark-oapi`.") from exc
    return lark


def _event_to_dict(lark: Any, data: Any) -> dict[str, Any]:
    serialized = lark.JSON.marshal(data)
    if isinstance(serialized, bytes):
        serialized = serialized.decode("utf-8")
    raw = json.loads(serialized)
    if isinstance(raw.get("data"), dict) and "event" in raw["data"]:
        return raw["data"]
    return raw


def _default_settings_path() -> str:
    config_override = os.getenv("AUTOMAGE_CONFIG_PATH", "").strip()
    if config_override:
        return config_override
    local_config = PROJECT_ROOT / "configs" / "automage.local.toml"
    if local_config.exists():
        return str(local_config)
    return str(PROJECT_ROOT / "configs" / "automage.example.toml")


def _default_profile_path(role: str) -> str:
    local_profile = PROJECT_ROOT / "examples" / f"user.{role}.local.example.toml"
    if local_profile.exists():
        return str(local_profile)
    return str(PROJECT_ROOT / "examples" / f"user.{role}.example.toml")


def _build_runtime(args: argparse.Namespace) -> HermesOpenClawRuntime:
    return HermesOpenClawRuntime.from_demo_configs(
        staff_user_path=args.staff_profile,
        manager_user_path=args.manager_profile,
        executive_user_path=args.executive_profile,
        settings_path=args.settings,
        user_mapping=_load_user_mapping(args),
        auto_initialize=not args.dry_run,
    )


def main() -> None:
    args = _parse_args()
    settings = load_runtime_settings(args.settings)
    runtime = _build_runtime(args)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "ok": True,
                    "mode": "dry_run",
                    "settings_path": args.settings,
                    "backend_mode": settings.backend_mode,
                    "api_base_url": settings.api_base_url,
                    "feishu_event_mode": settings.feishu_event_mode,
                    "mapped_open_ids": sorted(runtime.feishu_events.user_mapping),
                    "agent_identities": {
                        "staff": runtime.contexts.staff.identity.to_dict(),
                        "manager": runtime.contexts.manager.identity.to_dict(),
                        "executive": runtime.contexts.executive.identity.to_dict(),
                    },
                    "state_summary": runtime.state_summary(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if not settings.feishu_app_id or not settings.feishu_app_secret:
        print("[WARNING] FEISHU_APP_ID and FEISHU_APP_SECRET not configured")
        print("[INFO] Running in mock mode - no real Feishu connection")
        print("[INFO] To enable Feishu integration:")
        print("  1. Get credentials from https://open.feishu.cn/")
        print("  2. Set AUTOMAGE_FEISHU_APP_ID and AUTOMAGE_FEISHU_APP_SECRET in .env")
        print("")
        print("[INFO] Press Ctrl+C to exit")
        try:
            while True:
                import time
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n[INFO] Mock listener stopped")
        return
    if settings.feishu_event_mode != "websocket":
        print(f"FEISHU_EVENT_MODE is `{settings.feishu_event_mode}`; websocket listener will still start for local testing.")

    lark = _load_lark_sdk()
    feishu_messages = runtime.feishu_messages
    lark_client = (
        lark.Client.builder()
        .app_id(settings.feishu_app_id)
        .app_secret(settings.feishu_app_secret)
        .log_level(lark.LogLevel.INFO)
        .build()
    )

    def handle_message(data: Any) -> None:
        internal_event = None
        try:
            raw_event = _event_to_dict(lark, data)
            feishu_event = runtime.feishu_events.from_message_receive_v1(raw_event)
            internal_event = runtime.feishu_events.to_internal_event(feishu_event)
            try:
                result = runtime.openclaw.handle_event(internal_event)
            except Exception as exc:
                result = SkillResult(
                    ok=False,
                    data={"error_type": type(exc).__name__, "error": str(exc)},
                    message="AutoMage 后端暂时不可用，请稍后重试。",
                    error_code="server_error",
                )
                print(
                    json.dumps(
                        {
                            "ok": False,
                            "stage": "automage_event_processing",
                            "event_type": internal_event.event_type.value,
                            "actor_user_id": internal_event.actor_user_id,
                            "error_type": type(exc).__name__,
                            "error": str(exc),
                            "traceback": traceback.format_exc(limit=8),
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                )
            reply_result = _reply_to_feishu_chat(feishu_messages, lark_client, internal_event.payload, internal_event.event_type.value, result)
            print(
                json.dumps(
                    {
                        "event_type": internal_event.event_type.value,
                        "feishu_open_id": internal_event.payload.get("feishu_open_id"),
                        "actor_user_id": internal_event.actor_user_id,
                        "message_id": internal_event.correlation_id,
                        "raw_text": internal_event.payload.get("raw_text", ""),
                        "ok": result.ok,
                        "message": result.message,
                        "error_code": result.error_code,
                        "reply": reply_result,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        except Exception as exc:
            event_type = internal_event.event_type.value if internal_event is not None else None
            actor_user_id = internal_event.actor_user_id if internal_event is not None else None
            print(
                json.dumps(
                    {
                        "ok": False,
                        "stage": "feishu_message_handler",
                        "event_type": event_type,
                        "actor_user_id": actor_user_id,
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                        "traceback": traceback.format_exc(limit=8),
                        "raw_event_preview": _safe_event_preview(lark, data),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )

    event_handler = (
        lark.EventDispatcherHandler.builder("", "")
        .register_p2_im_message_receive_v1(handle_message)
        .build()
    )
    client = lark.ws.Client(
        settings.feishu_app_id,
        settings.feishu_app_secret,
        event_handler=event_handler,
        log_level=lark.LogLevel.INFO,
    )
    print("Feishu websocket listener started. Send a private message to the bot to test Agent routing.")
    client.start()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Listen to Feishu IM messages and route them into AutoMage Agent Skills.")
    parser.add_argument("--settings", default=_default_settings_path(), help="Runtime settings TOML path. Defaults to AUTOMAGE_CONFIG_PATH, local config, then example config.")
    parser.add_argument("--staff-profile", default=_default_profile_path("staff"))
    parser.add_argument("--manager-profile", default=_default_profile_path("manager"))
    parser.add_argument("--executive-profile", default=_default_profile_path("executive"))
    parser.add_argument("--user-map-json", help="JSON file mapping Feishu open_id to AutoMage user_id.")
    parser.add_argument("--map", action="append", default=[], help="Inline Feishu open_id to user_id mapping, e.g. open_id=user_backend_001.")
    parser.add_argument("--dry-run", action="store_true", help="Build runtime and print listener configuration without connecting to Feishu.")
    return parser.parse_args()


def _load_user_mapping(args: argparse.Namespace) -> dict[str, str]:
    mapping: dict[str, str] = {}
    if args.user_map_json:
        raw = json.loads(Path(args.user_map_json).read_text(encoding="utf-8-sig"))
        if not isinstance(raw, dict):
            raise ValueError("--user-map-json must contain a JSON object mapping open_id to user_id.")
        mapping.update({str(key): str(value) for key, value in raw.items()})
    for item in args.map:
        open_id, separator, user_id = str(item).partition("=")
        if not separator or not open_id.strip() or not user_id.strip():
            raise ValueError("--map values must use open_id=user_id format.")
        mapping[open_id.strip()] = user_id.strip()
    return mapping


def _safe_event_preview(lark: Any, data: Any) -> dict[str, Any]:
    try:
        raw_event = _event_to_dict(lark, data)
    except Exception as exc:
        return {"ok": False, "error_type": type(exc).__name__, "error": str(exc)}
    event = raw_event.get("event", raw_event)
    sender_id = event.get("sender", {}).get("sender_id", {}) if isinstance(event, dict) else {}
    message = event.get("message", {}) if isinstance(event, dict) else {}
    content = message.get("content") if isinstance(message, dict) else None
    if isinstance(content, str) and len(content) > 240:
        content = content[:240]
    return {
        "ok": True,
        "event_keys": sorted(raw_event.keys()) if isinstance(raw_event, dict) else [],
        "header_event_type": raw_event.get("header", {}).get("event_type") if isinstance(raw_event, dict) else None,
        "open_id": sender_id.get("open_id") if isinstance(sender_id, dict) else None,
        "message_id": message.get("message_id") if isinstance(message, dict) else None,
        "message_type": message.get("message_type") if isinstance(message, dict) else None,
        "content": content,
    }


def _reply_to_feishu_chat(
    feishu_messages: FeishuMessageAdapter,
    lark_client: Any,
    payload: dict[str, Any],
    event_type: str,
    result: Any,
) -> dict[str, Any]:
    resource_usage = payload.get("resource_usage", {})
    chat_id = resource_usage.get("chat_id") if isinstance(resource_usage, dict) else None
    if not chat_id:
        return {"ok": False, "channel": "feishu", "msg": "missing chat_id"}
    reply = feishu_messages.build_processing_result_reply(str(chat_id), event_type, result)
    try:
        return feishu_messages.send_lark_text(lark_client, reply)
    except Exception as exc:
        return {"ok": False, "channel": "feishu", "msg": str(exc)}


if __name__ == "__main__":
    main()
