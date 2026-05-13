from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


OPENCLAW_BIN = "/home/vincenthu/.nvm/versions/node/v24.15.0/bin/openclaw"
WSL_PATH = "/home/vincenthu/.nvm/versions/node/v24.15.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
PLUGIN_ID = "automage-openclaw-bridge"
SKILL_NAME = "automage-knowledge"
TOOL_NAME = "automage_openclaw_event"
MODEL_BALANCE_ERROR_MARKERS = ("余额不足", "insufficient balance", "insufficient_quota")


def main() -> None:
    args = _parse_args()
    checks = {
        "gateway_health": _run_openclaw(["gateway", "health"], timeout=args.timeout_seconds),
        "plugin_inspect": _run_openclaw(["plugins", "inspect", PLUGIN_ID], timeout=args.timeout_seconds),
        "skill_info": _run_openclaw(["skills", "info", SKILL_NAME], timeout=args.timeout_seconds),
        "models_list": _run_openclaw(["models", "list"], timeout=args.timeout_seconds),
    }
    agent_check: dict[str, Any] | None = None
    if args.run_agent:
        agent_check = _run_openclaw(
            [
                "agent",
                "--agent",
                args.agent,
                "--message",
                args.message,
                "--json",
                "--timeout",
                str(args.agent_timeout_seconds),
            ],
            timeout=args.agent_timeout_seconds + 20,
        )
        checks["agent_tool_invocation"] = agent_check

    output = {
        "ok": _is_ready(checks),
        "mode": "real_openclaw_gateway_ready",
        "plugin_id": PLUGIN_ID,
        "skill_name": SKILL_NAME,
        "tool_name": TOOL_NAME,
        "checks": checks,
        "blockers": _blockers(checks, agent_check),
    }
    if args.output_json:
        Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output_json).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(_summary(output) if args.summary_only else output, ensure_ascii=False, indent=2))
    if args.fail_on_not_ready and not output["ok"]:
        raise SystemExit(1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check WSL2 OpenClaw gateway readiness for the AutoMage bridge plugin.")
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--output-json")
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--fail-on-not-ready", action="store_true")
    parser.add_argument("--run-agent", action="store_true")
    parser.add_argument("--agent", default="main")
    parser.add_argument("--agent-timeout-seconds", type=int, default=150)
    parser.add_argument(
        "--message",
        default="使用 automage-knowledge skill。必须调用 automage_openclaw_event 工具查询：查知识库 OpenAPI 契约。不要调用 memory_search。只输出工具返回文本。",
    )
    return parser.parse_args()


def _run_openclaw(args: list[str], *, timeout: int) -> dict[str, Any]:
    env = {"PATH": WSL_PATH}
    process = subprocess.run(
        ["wsl", "-d", "Ubuntu-22.04", "--", "env", *[f"{key}={value}" for key, value in env.items()], OPENCLAW_BIN, *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    return {
        "returncode": process.returncode,
        "stdout_tail": process.stdout[-80000:],
        "stderr_tail": process.stderr[-2000:],
    }


def _is_ready(checks: dict[str, dict[str, Any]]) -> bool:
    return (
        checks["gateway_health"]["returncode"] == 0
        and checks["plugin_inspect"]["returncode"] == 0
        and TOOL_NAME in checks["plugin_inspect"]["stdout_tail"]
        and checks["skill_info"]["returncode"] == 0
    )


def _blockers(checks: dict[str, dict[str, Any]], agent_check: dict[str, Any] | None) -> list[str]:
    blockers: list[str] = []
    if checks["gateway_health"]["returncode"] != 0:
        blockers.append("openclaw_gateway_health_failed")
    if checks["plugin_inspect"]["returncode"] != 0:
        blockers.append("automage_plugin_not_inspectable")
    if TOOL_NAME not in checks["plugin_inspect"]["stdout_tail"]:
        blockers.append("automage_tool_contract_not_visible")
    if checks["skill_info"]["returncode"] != 0:
        blockers.append("automage_skill_not_visible")
    if agent_check is not None:
        agent_text = f"{agent_check.get('stdout_tail', '')}\n{agent_check.get('stderr_tail', '')}"
        if any(marker.lower() in agent_text.lower() for marker in MODEL_BALANCE_ERROR_MARKERS):
            blockers.append("model_provider_balance_or_auth_blocked")
        elif agent_check["returncode"] != 0:
            blockers.append("agent_tool_invocation_failed")
    return blockers


def _summary(output: dict[str, Any]) -> dict[str, Any]:
    checks = output["checks"]
    summary = {
        "ok": output["ok"],
        "mode": output["mode"],
        "plugin_id": output["plugin_id"],
        "skill_name": output["skill_name"],
        "tool_name": output["tool_name"],
        "gateway_health_returncode": checks["gateway_health"]["returncode"],
        "plugin_inspect_returncode": checks["plugin_inspect"]["returncode"],
        "skill_info_returncode": checks["skill_info"]["returncode"],
        "tool_visible": output["tool_name"] in checks["plugin_inspect"]["stdout_tail"],
        "skill_visible": checks["skill_info"]["returncode"] == 0,
        "models_tail": checks["models_list"]["stdout_tail"][-500:],
        "blockers": output["blockers"],
    }
    if "agent_tool_invocation" in checks:
        agent = checks["agent_tool_invocation"]
        agent_json = _parse_json_object(agent["stdout_tail"])
        tool_summary = _find_tool_summary(agent_json) if agent_json else {}
        summary.update({
            "agent_returncode": agent["returncode"],
            "agent_tool_calls": tool_summary.get("calls"),
            "agent_tools": tool_summary.get("tools"),
            "agent_failures": tool_summary.get("failures"),
        })
    return summary


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


if __name__ == "__main__":
    main()
