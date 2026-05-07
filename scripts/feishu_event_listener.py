from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.config.loader import load_runtime_settings
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


def _build_runtime() -> HermesOpenClawRuntime:
    return HermesOpenClawRuntime.from_demo_configs()


def main() -> None:
    settings = load_runtime_settings("configs/automage.example.toml")
    if not settings.feishu_app_id or not settings.feishu_app_secret:
        raise RuntimeError("FEISHU_APP_ID and FEISHU_APP_SECRET are required in .env or environment variables.")
    if settings.feishu_event_mode != "websocket":
        print(f"FEISHU_EVENT_MODE is `{settings.feishu_event_mode}`; websocket listener will still start for local testing.")

    lark = _load_lark_sdk()
    runtime = _build_runtime()
    feishu_messages = runtime.feishu_messages
    lark_client = (
        lark.Client.builder()
        .app_id(settings.feishu_app_id)
        .app_secret(settings.feishu_app_secret)
        .log_level(lark.LogLevel.INFO)
        .build()
    )

    def handle_message(data: Any) -> None:
        raw_event = _event_to_dict(lark, data)
        feishu_event = runtime.feishu_events.from_message_receive_v1(raw_event)
        internal_event = runtime.feishu_events.to_internal_event(feishu_event)
        result = runtime.openclaw.handle_event(internal_event)
        reply_result = _reply_to_feishu_chat(feishu_messages, lark_client, internal_event.payload, internal_event.event_type.value, result)
        print(
            json.dumps(
                {
                    "event_type": internal_event.event_type.value,
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
