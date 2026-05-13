from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

NODE_BIN = "/home/vincenthu/.nvm/versions/node/v24.15.0/bin/node"
WSL_PATH = "/home/vincenthu/.nvm/versions/node/v24.15.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
TOOL_NAME = "automage_openclaw_event"


def main() -> None:
    args = _parse_args()
    node_script = _node_script(args.text, args.actor_external_id, args.channel)
    process = subprocess.run(
        [
            "wsl",
            "-d",
            "Ubuntu-22.04",
            "--",
            "env",
            f"PATH={WSL_PATH}",
            f"AUTOMAGE_OPENCLAW_BRIDGE_URL={args.base_url}",
            NODE_BIN,
            "--input-type=module",
            "-e",
            node_script,
        ],
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=args.timeout_seconds,
        check=False,
    )
    parsed = _parse_json_output(process.stdout)
    text = _extract_text(parsed)
    output = {
        "ok": process.returncode == 0 and bool(text),
        "mode": "openclaw_plugin_tool_runtime_smoke",
        "base_url": args.base_url,
        "tool_name": TOOL_NAME,
        "returncode": process.returncode,
        "reply_text": text,
        "stderr_tail": process.stderr[-2000:],
    }
    if args.output_json:
        Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output_json).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if not output["ok"]:
        raise SystemExit(1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test OpenClaw plugin tool resolution and direct execution.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--text", default="查知识库 OpenAPI 契约")
    parser.add_argument("--actor-external-id", default="staff-open-id")
    parser.add_argument("--channel", default="openclaw")
    parser.add_argument("--timeout-seconds", type=int, default=60)
    parser.add_argument("--output-json")
    return parser.parse_args()


def _node_script(text: str, actor_external_id: str, channel: str) -> str:
    params = {"text": text, "actorExternalId": actor_external_id, "channel": channel}
    return f"""
import {{ r as resolvePluginTools }} from '/home/vincenthu/.nvm/versions/node/v24.15.0/lib/node_modules/openclaw/dist/tools-CZr3orc0.js';
import {{ a as loadConfig }} from '/home/vincenthu/.nvm/versions/node/v24.15.0/lib/node_modules/openclaw/dist/io-Dv_xNAZB.js';
const config = loadConfig();
const tools = resolvePluginTools({{ context: {{ config }}, suppressNameConflicts: true }});
const tool = tools.find((candidate) => candidate.name === {json.dumps(TOOL_NAME)});
if (!tool) {{
  console.log(JSON.stringify({{ ok: false, error: 'tool_not_found', toolNames: tools.map((candidate) => candidate.name) }}));
  process.exit(2);
}}
const result = await tool.execute('openclaw-runtime-smoke', {json.dumps(params, ensure_ascii=False)});
console.log(JSON.stringify({{ ok: true, toolName: tool.name, result }}));
"""


def _parse_json_output(stdout: str) -> dict[str, Any]:
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            return data if isinstance(data, dict) else {"value": data}
        except json.JSONDecodeError:
            continue
    return {}


def _extract_text(parsed: dict[str, Any]) -> str | None:
    content = parsed.get("result", {}).get("content", [])
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text" and item.get("text"):
                return str(item["text"])
    return None


if __name__ == "__main__":
    main()
