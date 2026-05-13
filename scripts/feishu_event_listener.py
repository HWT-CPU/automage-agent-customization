from __future__ import annotations

import argparse
import copy
from dataclasses import dataclass
import io
import json
import os
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any
import zipfile
import xml.etree.ElementTree as ET

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.config.loader import load_runtime_settings
from automage_agents.core.models import SkillResult
from automage_agents.integrations.feishu.messages import FeishuMessageAdapter
from automage_agents.integrations.hermes import HermesOpenClawRuntime

OPENCLAW_BIN = "/home/vincenthu/.nvm/versions/node/v24.15.0/bin/openclaw"
OPENCLAW_WSL_DISTRO = "Ubuntu-22.04"
OPENCLAW_WSL_PATH = "/home/vincenthu/.nvm/versions/node/v24.15.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
OPENCLAW_TOOL_NAME = "automage_openclaw_event"
TEXT_FILE_EXTENSIONS = {".txt", ".md", ".markdown", ".csv", ".json", ".toml", ".yaml", ".yml", ".log"}


@dataclass(slots=True)
class RealOpenClawAgentResult:
    ok: bool
    reply_text: str
    returncode: int
    tool_called: bool
    tool_summary: dict[str, Any]
    stdout_tail: str
    stderr_tail: str
    error_code: str | None = None


@dataclass(slots=True)
class FeishuFileExtraction:
    ok: bool
    text: str = ""
    file_key: str = ""
    file_name: str = ""
    message_id: str = ""
    truncated: bool = False
    error: str | None = None


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


def _default_user_map_path() -> str | None:
    configured_path = os.getenv("AUTOMAGE_FEISHU_USER_MAP_JSON") or os.getenv("FEISHU_USER_MAP_JSON")
    if configured_path:
        return configured_path
    local_mapping = PROJECT_ROOT / "configs" / "feishu_user_map.local.json"
    if local_mapping.exists():
        return str(local_mapping)
    return None


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
                    "route_mode": args.route_mode,
                    "openclaw_agent": args.openclaw_agent,
                    "openclaw_bridge_url": args.openclaw_bridge_url,
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
            ),
            flush=True,
        )
        return
    if not settings.feishu_app_id or not settings.feishu_app_secret:
        raise RuntimeError("FEISHU_APP_ID and FEISHU_APP_SECRET are required in .env or environment variables.")
    if settings.feishu_event_mode != "websocket":
        print(f"FEISHU_EVENT_MODE is `{settings.feishu_event_mode}`; websocket listener will still start for local testing.", flush=True)

    lark = _load_lark_sdk()
    feishu_messages = runtime.feishu_messages
    lark_client = (
        lark.Client.builder()
        .app_id(settings.feishu_app_id)
        .app_secret(settings.feishu_app_secret)
        .log_level(lark.LogLevel.INFO)
        .build()
    )
    recent_files: dict[str, FeishuFileExtraction] = {}

    def handle_message(data: Any) -> None:
        internal_event = None
        try:
            should_route = True
            raw_event = _event_to_dict(lark, data)
            file_cache_key = _feishu_file_cache_key(raw_event)
            raw_event, file_extraction = _prepare_feishu_file_event(
                lark_client,
                raw_event,
                max_bytes=args.feishu_file_max_bytes,
                max_chars=args.feishu_file_max_chars,
            )
            feishu_event = runtime.feishu_events.from_message_receive_v1(raw_event)
            internal_event = runtime.feishu_events.to_internal_event(feishu_event)
            if file_extraction is not None and file_extraction.ok:
                recent_files[file_cache_key] = file_extraction
            if file_extraction is not None:
                internal_event.payload["feishu_file"] = {
                    "ok": file_extraction.ok,
                    "file_key": file_extraction.file_key,
                    "file_name": file_extraction.file_name,
                    "message_id": file_extraction.message_id,
                    "truncated": file_extraction.truncated,
                    "error": file_extraction.error,
                }
            if file_extraction is None and _is_file_summary_request(str(internal_event.payload.get("raw_text") or "")):
                cached_file = recent_files.get(file_cache_key)
                if cached_file is not None:
                    internal_event.payload["raw_text"] = _file_text_from_extraction(cached_file)
                    internal_event.payload["feishu_file"] = {
                        "ok": cached_file.ok,
                        "file_key": cached_file.file_key,
                        "file_name": cached_file.file_name,
                        "message_id": cached_file.message_id,
                        "truncated": cached_file.truncated,
                        "error": cached_file.error,
                        "reused": True,
                    }
                else:
                    internal_event.payload["feishu_file"] = {
                        "ok": False,
                        "requested": True,
                        "error": "missing_attachment",
                    }
            if should_route and file_extraction is not None and not file_extraction.ok:
                result = SkillResult(
                    ok=False,
                    data={"feishu_file": internal_event.payload["feishu_file"]},
                    message=f"飞书文件解析失败：{file_extraction.error or 'unknown error'}",
                    error_code="feishu_file_parse_failed",
                )
                reply_result = _reply_text_to_feishu_chat(
                    feishu_messages,
                    lark_client,
                    internal_event.payload,
                    result.message,
                    ok=False,
                    error_code=result.error_code,
                )
                should_route = False
            if should_route and args.route_mode == "real-openclaw-agent":
                agent_result = _run_real_openclaw_agent(
                    args,
                    text=str(internal_event.payload.get("raw_text") or ""),
                    actor_external_id=feishu_event.open_id,
                    event_id=internal_event.correlation_id,
                    chat_id=_chat_id_from_payload(internal_event.payload),
                    payload=_openclaw_tool_payload_from_internal_event(internal_event.payload),
                )
                result = SkillResult(
                    ok=agent_result.ok,
                    data={
                        "route_mode": args.route_mode,
                        "tool_called": agent_result.tool_called,
                        "tool_summary": agent_result.tool_summary,
                        "agent_returncode": agent_result.returncode,
                        "stdout_tail": agent_result.stdout_tail,
                        "stderr_tail": agent_result.stderr_tail,
                    },
                    message=agent_result.reply_text,
                    error_code=agent_result.error_code,
                )
                reply_result = _reply_text_to_feishu_chat(
                    feishu_messages,
                    lark_client,
                    internal_event.payload,
                    agent_result.reply_text if agent_result.ok else f"OpenClaw Agent 处理失败：{agent_result.reply_text}",
                    ok=agent_result.ok,
                    error_code=agent_result.error_code,
                )
            elif should_route:
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
                        ),
                        flush=True,
                    )
                reply_result = _reply_to_feishu_chat(feishu_messages, lark_client, internal_event.payload, internal_event.event_type.value, result)
            print(
                json.dumps(
                    {
                        "route_mode": args.route_mode,
                        "event_type": internal_event.event_type.value,
                        "feishu_open_id": internal_event.payload.get("feishu_open_id"),
                        "actor_user_id": internal_event.actor_user_id,
                        "message_id": internal_event.correlation_id,
                        "message_type": internal_event.payload.get("resource_usage", {}).get("message_type") if isinstance(internal_event.payload.get("resource_usage"), dict) else None,
                        "raw_text": internal_event.payload.get("raw_text", ""),
                        "feishu_file": internal_event.payload.get("feishu_file"),
                        "ok": result.ok,
                        "message": result.message,
                        "error_code": result.error_code,
                        "openclaw_agent": result.data.get("tool_summary") if isinstance(result.data, dict) else None,
                        "reply": reply_result,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                flush=True,
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
                ),
                flush=True,
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
    print("Feishu websocket listener started. Send a private message to the bot to test Agent routing.", flush=True)
    client.start()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Listen to Feishu IM messages and route them into AutoMage Agent Skills.")
    parser.add_argument("--settings", default=_default_settings_path(), help="Runtime settings TOML path. Defaults to AUTOMAGE_CONFIG_PATH, local config, then example config.")
    parser.add_argument("--staff-profile", default=_default_profile_path("staff"))
    parser.add_argument("--manager-profile", default=_default_profile_path("manager"))
    parser.add_argument("--executive-profile", default=_default_profile_path("executive"))
    parser.add_argument("--user-map-json", default=_default_user_map_path(), help="JSON file mapping Feishu open_id to AutoMage user_id.")
    parser.add_argument("--map", action="append", default=[], help="Inline Feishu open_id to user_id mapping, e.g. open_id=user_backend_001.")
    parser.add_argument("--route-mode", choices=["local-runtime", "real-openclaw-agent"], default="local-runtime", help="local-runtime routes directly to the in-process Hermes/OpenClaw runtime; real-openclaw-agent sends the Feishu message through a real OpenClaw agent tool call.")
    parser.add_argument("--openclaw-agent", default="main")
    parser.add_argument("--openclaw-bin", default=os.getenv("OPENCLAW_BIN", OPENCLAW_BIN))
    parser.add_argument("--openclaw-wsl-distro", default=os.getenv("OPENCLAW_WSL_DISTRO", OPENCLAW_WSL_DISTRO))
    parser.add_argument("--openclaw-wsl-path", default=os.getenv("OPENCLAW_WSL_PATH", OPENCLAW_WSL_PATH))
    parser.add_argument("--openclaw-bridge-url", default=os.getenv("AUTOMAGE_OPENCLAW_BRIDGE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--openclaw-timeout-seconds", type=int, default=180)
    parser.add_argument("--feishu-file-max-bytes", type=int, default=2_000_000)
    parser.add_argument("--feishu-file-max-chars", type=int, default=16_000)
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


def _actor_user_id_from_raw_event(runtime: HermesOpenClawRuntime, raw_event: dict[str, Any]) -> str:
    event = raw_event.get("event", raw_event)
    sender_id = event.get("sender", {}).get("sender_id", {}) if isinstance(event, dict) else {}
    open_id = str(sender_id.get("open_id") or sender_id.get("user_id") or sender_id.get("union_id") or "unknown_feishu_user")
    return runtime.feishu_events.user_mapping.get(open_id, open_id)


def _feishu_file_cache_key(raw_event: dict[str, Any]) -> str:
    event = raw_event.get("event", raw_event)
    if not isinstance(event, dict):
        return "unknown"
    message = event.get("message", {}) if isinstance(event.get("message"), dict) else {}
    chat_id = str(message.get("chat_id") or "")
    sender_id = event.get("sender", {}).get("sender_id", {}) if isinstance(event.get("sender"), dict) else {}
    open_id = str(sender_id.get("open_id") or sender_id.get("user_id") or sender_id.get("union_id") or "unknown_feishu_user")
    return chat_id or open_id


def _is_file_summary_request(text: str) -> bool:
    normalized = text.strip()
    if not normalized:
        return False
    return "汇总" in normalized and any(keyword in normalized for keyword in ["文件", "附件"])


def _prepare_feishu_file_event(
    lark_client: Any,
    raw_event: dict[str, Any],
    *,
    max_bytes: int,
    max_chars: int,
) -> tuple[dict[str, Any], FeishuFileExtraction | None]:
    event = raw_event.get("event", raw_event)
    message = event.get("message", {}) if isinstance(event, dict) else {}
    metadata = _extract_feishu_file_metadata(message)
    if not metadata:
        return raw_event, None
    extraction = _download_feishu_message_file(
        lark_client,
        message_id=str(message.get("message_id") or ""),
        file_key=str(metadata.get("file_key") or ""),
        file_name=str(metadata.get("file_name") or ""),
        max_bytes=max_bytes,
        max_chars=max_chars,
    )
    text = _file_text_from_extraction(extraction)
    updated = copy.deepcopy(raw_event)
    updated_event = updated.get("event", updated)
    updated_message = updated_event.get("message", {}) if isinstance(updated_event, dict) else {}
    updated_message["content"] = json.dumps({"text": text}, ensure_ascii=False)
    return updated, extraction


def _extract_feishu_file_metadata(message: dict[str, Any]) -> dict[str, Any]:
    direct = _find_feishu_file_metadata(message)
    if direct:
        return direct
    content = message.get("content", {})
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            return {}
    if not isinstance(content, dict):
        return {}
    file_key = content.get("file_key") or content.get("fileKey") or content.get("key")
    if not file_key:
        return {}
    file_name = content.get("file_name") or content.get("fileName") or content.get("name") or ""
    return {"file_key": str(file_key), "file_name": str(file_name)}


def _find_feishu_file_metadata(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        stripped = value.strip()
        if not _looks_like_json_text(stripped):
            return {}
        try:
            return _find_feishu_file_metadata(json.loads(stripped))
        except json.JSONDecodeError:
            return {}
    if isinstance(value, dict):
        file_key = value.get("file_key") or value.get("fileKey")
        if file_key:
            file_name = value.get("file_name") or value.get("fileName") or value.get("name") or value.get("file_name_i18n") or ""
            return {"file_key": str(file_key), "file_name": str(file_name)}
        for child in value.values():
            found = _find_feishu_file_metadata(child)
            if found:
                return found
    if isinstance(value, list):
        for child in value:
            found = _find_feishu_file_metadata(child)
            if found:
                return found
    return {}


def _download_feishu_message_file(
    lark_client: Any,
    *,
    message_id: str,
    file_key: str,
    file_name: str,
    max_bytes: int,
    max_chars: int,
) -> FeishuFileExtraction:
    if not message_id or not file_key:
        return FeishuFileExtraction(ok=False, file_key=file_key, file_name=file_name, message_id=message_id, error="missing message_id or file_key")
    try:
        from lark_oapi.api.im.v1 import GetMessageResourceRequest

        request = (
            GetMessageResourceRequest.builder()
            .message_id(message_id)
            .file_key(file_key)
            .type("file")
            .build()
        )
        response = lark_client.im.v1.message_resource.get(request)
    except Exception as exc:
        return FeishuFileExtraction(ok=False, file_key=file_key, file_name=file_name, message_id=message_id, error=str(exc))
    if hasattr(response, "success") and not response.success():
        return FeishuFileExtraction(
            ok=False,
            file_key=file_key,
            file_name=getattr(response, "file_name", None) or file_name,
            message_id=message_id,
            error=f"{getattr(response, 'code', '')} {getattr(response, 'msg', '')}".strip() or "download failed",
        )
    resolved_name = str(getattr(response, "file_name", None) or file_name)
    raw, byte_truncated = _read_file_bytes(getattr(response, "file", None), max_bytes=max_bytes)
    if not raw:
        return FeishuFileExtraction(ok=False, file_key=file_key, file_name=resolved_name, message_id=message_id, error="downloaded file is empty")
    text, char_truncated = _extract_text_from_file_bytes(raw, resolved_name, max_chars=max_chars)
    if not text.strip():
        return FeishuFileExtraction(ok=False, file_key=file_key, file_name=resolved_name, message_id=message_id, error=f"unsupported or empty file: {resolved_name}")
    return FeishuFileExtraction(
        ok=True,
        text=text,
        file_key=file_key,
        file_name=resolved_name,
        message_id=message_id,
        truncated=byte_truncated or char_truncated,
    )


def _read_file_bytes(file_obj: Any, *, max_bytes: int) -> tuple[bytes, bool]:
    if isinstance(file_obj, bytes):
        return file_obj[:max_bytes], len(file_obj) > max_bytes
    if isinstance(file_obj, str):
        raw = file_obj.encode("utf-8")
        return raw[:max_bytes], len(raw) > max_bytes
    if file_obj is None or not hasattr(file_obj, "read"):
        return b"", False
    raw = file_obj.read(max_bytes + 1)
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    return raw[:max_bytes], len(raw) > max_bytes


def _extract_text_from_file_bytes(raw: bytes, file_name: str, *, max_chars: int) -> tuple[str, bool]:
    suffix = Path(file_name).suffix.lower()
    if suffix in TEXT_FILE_EXTENSIONS or not suffix:
        return _truncate_text(_decode_text_bytes(raw), max_chars)
    if suffix == ".docx":
        return _truncate_text(_extract_docx_text(raw), max_chars)
    if suffix == ".xlsx":
        return _truncate_text(_extract_xlsx_text(raw), max_chars)
    return "", False


def _decode_text_bytes(raw: bytes) -> str:
    for encoding in ["utf-8-sig", "utf-8", "gb18030"]:
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _extract_docx_text(raw: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            xml_text = archive.read("word/document.xml")
    except Exception:
        return ""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return ""
    lines: list[str] = []
    for paragraph in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
        line = "".join(node.text or "" for node in paragraph.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"))
        if line.strip():
            lines.append(line)
    return "\n".join(lines)


def _extract_xlsx_text(raw: bytes) -> str:
    try:
        archive = zipfile.ZipFile(io.BytesIO(raw))
    except Exception:
        return ""
    with archive:
        shared_strings = _xlsx_shared_strings(archive)
        rows: list[str] = []
        sheet_names = sorted(name for name in archive.namelist() if name.startswith("xl/worksheets/") and name.endswith(".xml"))
        for sheet_name in sheet_names:
            try:
                root = ET.fromstring(archive.read(sheet_name))
            except Exception:
                continue
            for row in root.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row"):
                cells = [_xlsx_cell_text(cell, shared_strings) for cell in row.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c")]
                line = "\t".join(cell for cell in cells if cell.strip())
                if line.strip():
                    rows.append(line)
    return "\n".join(rows)


def _xlsx_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    try:
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    except Exception:
        return []
    strings: list[str] = []
    for item in root.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si"):
        strings.append("".join(node.text or "" for node in item.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")))
    return strings


def _xlsx_cell_text(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"))
    value = next(cell.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v"), None)
    if value is None or value.text is None:
        return ""
    if cell_type == "s":
        try:
            return shared_strings[int(value.text)]
        except (ValueError, IndexError):
            return ""
    return value.text


def _truncate_text(text: str, max_chars: int) -> tuple[str, bool]:
    if len(text) <= max_chars:
        return text, False
    return text[:max_chars], True


def _file_text_from_extraction(extraction: FeishuFileExtraction) -> str:
    if not extraction.ok:
        return f"飞书文件解析失败：{extraction.error or 'unknown error'}\n文件名：{extraction.file_name or 'unknown'}"
    header = f"文件名：{extraction.file_name or 'unknown'}"
    if extraction.truncated:
        header = f"{header}\n文件内容已按长度限制截断。"
    return f"{header}\n\n{extraction.text}"


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


def _run_real_openclaw_agent(
    args: argparse.Namespace,
    *,
    text: str,
    actor_external_id: str,
    event_id: str | None,
    chat_id: str | None,
    payload: dict[str, Any] | None = None,
) -> RealOpenClawAgentResult:
    prompt = _build_real_openclaw_agent_message(text=text, actor_external_id=actor_external_id, event_id=event_id, chat_id=chat_id, payload=payload)
    env = {
        "PATH": args.openclaw_wsl_path,
        "AUTOMAGE_OPENCLAW_BRIDGE_URL": args.openclaw_bridge_url,
        "AUTOMAGE_OPENCLAW_ACTOR_ID": actor_external_id,
        "AUTOMAGE_OPENCLAW_CHANNEL": "feishu",
    }
    if chat_id:
        env["AUTOMAGE_OPENCLAW_ACCOUNT_ID"] = chat_id
    command = [
        "wsl",
        "-d",
        args.openclaw_wsl_distro,
        "--",
        "env",
        *[f"{key}={value}" for key, value in env.items()],
        args.openclaw_bin,
        "agent",
        "--agent",
        args.openclaw_agent,
        "--message",
        prompt,
        "--json",
        "--timeout",
        str(args.openclaw_timeout_seconds),
    ]
    try:
        process = subprocess.run(
            command,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=args.openclaw_timeout_seconds + 30,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return RealOpenClawAgentResult(
            ok=False,
            reply_text=f"openclaw agent timed out after {exc.timeout} seconds",
            returncode=-1,
            tool_called=False,
            tool_summary={},
            stdout_tail=_redact_sensitive_text((exc.stdout or "")[-8000:] if isinstance(exc.stdout, str) else ""),
            stderr_tail=_redact_sensitive_text((exc.stderr or "")[-3000:] if isinstance(exc.stderr, str) else ""),
            error_code="openclaw_agent_timeout",
        )
    except FileNotFoundError as exc:
        return RealOpenClawAgentResult(
            ok=False,
            reply_text=str(exc),
            returncode=-1,
            tool_called=False,
            tool_summary={},
            stdout_tail="",
            stderr_tail="",
            error_code="openclaw_agent_unavailable",
        )
    stdout_tail = _redact_sensitive_text(process.stdout[-8000:])
    stderr_tail = _redact_sensitive_text(process.stderr[-3000:])
    agent_json = _parse_json_object(process.stdout)
    tool_summary = _find_tool_summary(agent_json) if agent_json else {}
    tool_called = _tool_called(tool_summary, f"{process.stdout}\n{process.stderr}")
    reply_text = _extract_tool_text(agent_json) or _extract_agent_reply_text(agent_json) or _extract_json_reply_text(stdout_tail)
    if process.returncode != 0:
        return RealOpenClawAgentResult(
            ok=False,
            reply_text=reply_text or stderr_tail or f"openclaw agent exited with {process.returncode}",
            returncode=process.returncode,
            tool_called=tool_called,
            tool_summary=tool_summary,
            stdout_tail=stdout_tail,
            stderr_tail=stderr_tail,
            error_code="openclaw_agent_failed",
        )
    if not tool_called:
        return RealOpenClawAgentResult(
            ok=False,
            reply_text=reply_text or "OpenClaw Agent did not call automage_openclaw_event.",
            returncode=process.returncode,
            tool_called=False,
            tool_summary=tool_summary,
            stdout_tail=stdout_tail,
            stderr_tail=stderr_tail,
            error_code="openclaw_tool_not_called",
        )
    return RealOpenClawAgentResult(
        ok=True,
        reply_text=reply_text or "OpenClaw Agent 已通过 automage_openclaw_event 处理该 Feishu 消息。",
        returncode=process.returncode,
        tool_called=True,
        tool_summary=tool_summary,
        stdout_tail=stdout_tail,
        stderr_tail=stderr_tail,
    )


def _build_real_openclaw_agent_message(*, text: str, actor_external_id: str, event_id: str | None, chat_id: str | None, payload: dict[str, Any] | None = None) -> str:
    tool_params = {
        "text": text,
        "actorExternalId": actor_external_id,
        "channel": "feishu",
    }
    if payload:
        tool_params["payload"] = payload
    return "\n".join(
        [
            "使用 automage-knowledge skill。",
            f"必须调用 {OPENCLAW_TOOL_NAME} 工具处理这条 Feishu 用户消息。",
            f"工具参数必须严格使用：{json.dumps(tool_params, ensure_ascii=False)}",
            "不要调用 memory_search、web 或本地文件来代替该工具。",
            "只输出工具返回文本。",
            f"Feishu message_id: {event_id or ''}",
            f"Feishu chat_id: {chat_id or ''}",
        ]
    )


def _openclaw_tool_payload_from_internal_event(payload: dict[str, Any]) -> dict[str, Any]:
    tool_payload: dict[str, Any] = {}
    feishu_file = payload.get("feishu_file")
    if isinstance(feishu_file, dict):
        tool_payload["feishu_file"] = dict(feishu_file)
    message_id = payload.get("message_id")
    if message_id:
        tool_payload["feishu_message_id"] = message_id
    resource_usage = payload.get("resource_usage")
    if isinstance(resource_usage, dict):
        chat_id = resource_usage.get("chat_id")
        if chat_id:
            tool_payload["feishu_chat_id"] = chat_id
        message_type = resource_usage.get("message_type")
        if message_type:
            tool_payload["feishu_message_type"] = message_type
    return tool_payload


def _parse_json_object(text: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    fallback: dict[str, Any] = {}
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            value, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if not isinstance(value, dict):
            continue
        if not fallback:
            fallback = value
        if isinstance(value.get("result"), dict) and isinstance(value["result"].get("toolSummary"), dict):
            return value
    return fallback


def _find_tool_summary(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        candidate = value.get("toolSummary")
        if isinstance(candidate, dict):
            return candidate
        for child in value.values():
            found = _find_tool_summary(child)
            if found:
                return found
    if isinstance(value, list):
        for child in value:
            found = _find_tool_summary(child)
            if found:
                return found
    return {}


def _tool_called(tool_summary: dict[str, Any], raw_output: str) -> bool:
    tools = tool_summary.get("tools")
    if isinstance(tools, list) and OPENCLAW_TOOL_NAME in tools:
        return True
    calls = tool_summary.get("calls")
    if isinstance(calls, int) and calls > 0 and OPENCLAW_TOOL_NAME in raw_output:
        return True
    if f'"name":"{OPENCLAW_TOOL_NAME}"' in raw_output.replace(" ", ""):
        return True
    if f'"tool":"{OPENCLAW_TOOL_NAME}"' in raw_output.replace(" ", ""):
        return True
    return False


def _extract_agent_reply_text(value: Any) -> str:
    if isinstance(value, dict):
        for key in ["finalAssistantVisibleText", "finalAssistantRawText", "reply_text"]:
            found = _extract_reply_string(value.get(key))
            if found:
                return found
        reply = value.get("reply")
        if isinstance(reply, dict):
            found = _extract_agent_reply_text(reply)
            if found:
                return found
        content = value.get("content")
        if isinstance(content, list):
            lines = [item.get("text", "") for item in content if isinstance(item, dict) and isinstance(item.get("text"), str)]
            if any(line.strip() for line in lines):
                return "\n".join(line for line in lines if line.strip())
        for key in ["result", "finalMessage", "assistant", "data"]:
            found = _extract_agent_reply_text(value.get(key))
            if found:
                return found
        for key in ["text", "message", "output", "final", "response"]:
            found = _extract_reply_string(value.get(key))
            if found:
                return found
        messages = value.get("messages")
        if isinstance(messages, list):
            for item in reversed(messages):
                found = _extract_agent_reply_text(item)
                if found:
                    return found
    if isinstance(value, list):
        for item in reversed(value):
            found = _extract_agent_reply_text(item)
            if found:
                return found
    return ""


def _extract_reply_string(value: Any) -> str:
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return ""
        found = _extract_json_reply_text(stripped)
        if found:
            return found
        if _looks_like_json_text(stripped):
            return ""
        return stripped
    if isinstance(value, dict | list):
        return _extract_agent_reply_text(value)
    return ""


def _extract_json_reply_text(text: str) -> str:
    stripped = text.strip()
    if not stripped or stripped[0] not in "{[":
        return ""
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError:
        if stripped[0] != "{":
            return ""
        value = _parse_json_object(stripped)
    return _extract_agent_reply_text(value) or _extract_tool_text(value)


def _looks_like_json_text(text: str) -> bool:
    stripped = text.strip()
    return len(stripped) >= 2 and stripped[0] in "{[" and stripped[-1] in "}]"


def _extract_tool_text(value: Any) -> str:
    if isinstance(value, dict):
        result = value.get("result")
        if isinstance(result, dict):
            tool_results = result.get("toolResults") or result.get("tools")
            if isinstance(tool_results, list):
                for item in reversed(tool_results):
                    found = _extract_agent_reply_text(item)
                    if found:
                        return found
        for child in value.values():
            found = _extract_tool_text(child)
            if found:
                return found
    if isinstance(value, list):
        for child in reversed(value):
            found = _extract_tool_text(child)
            if found:
                return found
    return ""


def _redact_sensitive_text(text: str) -> str:
    redacted = text
    for marker in ["OPENAI_API_KEY", "CLOSEAI_API_KEY", "FEISHU_APP_SECRET", "LARK_APP_SECRET"]:
        redacted = redacted.replace(marker, f"{marker[:4]}***")
    return redacted


def _chat_id_from_payload(payload: dict[str, Any]) -> str | None:
    resource_usage = payload.get("resource_usage", {})
    if isinstance(resource_usage, dict) and resource_usage.get("chat_id"):
        return str(resource_usage["chat_id"])
    return None


def _reply_text_to_feishu_chat(
    feishu_messages: FeishuMessageAdapter,
    lark_client: Any,
    payload: dict[str, Any],
    body: str,
    *,
    ok: bool = True,
    error_code: str | None = None,
) -> dict[str, Any]:
    chat_id = _chat_id_from_payload(payload)
    if not chat_id:
        return {"ok": False, "channel": "feishu", "msg": "missing chat_id"}
    try:
        return feishu_messages.send_lark_text(
            lark_client,
            feishu_messages.build_processing_result_reply(
                chat_id,
                "openclaw_agent_result",
                SkillResult(ok=ok, data={}, message=body, error_code=error_code),
            ),
        )
    except Exception as exc:
        return {"ok": False, "channel": "feishu", "msg": str(exc)}


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
