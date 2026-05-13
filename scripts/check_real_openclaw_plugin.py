from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


PLUGIN_PATH = "/home/vincenthu/.openclaw/local-plugins/automage-openclaw-bridge/index.mjs"
OPENCLAW_BIN = "/home/vincenthu/.nvm/versions/node/v24.15.0/bin/openclaw"
WSL_PATH = "/home/vincenthu/.nvm/versions/node/v24.15.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"


def main() -> None:
    args = _parse_args()
    inspect = _run_wsl([OPENCLAW_BIN, "plugins", "inspect", "automage-openclaw-bridge"], env={"PATH": WSL_PATH})
    node_script = _node_script(args.text, args.actor_external_id, args.base_url)
    invoke = _run_wsl(["node", "-e", node_script], env={"PATH": WSL_PATH, "AUTOMAGE_OPENCLAW_BRIDGE_URL": args.base_url})
    reply = _parse_json_output(invoke["stdout"])
    output = {
        "ok": inspect["returncode"] == 0 and invoke["returncode"] == 0 and bool(reply.get("text")),
        "mode": "real_openclaw_plugin_smoke",
        "base_url": args.base_url,
        "plugin_path": PLUGIN_PATH,
        "inspect": _summarize_process(inspect),
        "invoke": {**_summarize_process(invoke), "reply": reply},
    }
    if args.output_json:
        Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output_json).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(_summary(output) if args.summary_only else output, ensure_ascii=False, indent=2))
    if not output["ok"]:
        raise SystemExit(1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test installed WSL2 OpenClaw AutoMage bridge plugin.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--actor-external-id", default="staff-open-id")
    parser.add_argument("--text", default="查知识库 OpenAPI 契约")
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--output-json")
    return parser.parse_args()


def _run_wsl(command: list[str], *, env: dict[str, str]) -> dict[str, Any]:
    env_args = [f"{key}={value}" for key, value in env.items()]
    process = subprocess.run(
        ["wsl", "-d", "Ubuntu-22.04", "--", "env", *env_args, *command],
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {"returncode": process.returncode, "stdout": process.stdout, "stderr": process.stderr}


def _node_script(text: str, actor_external_id: str, base_url: str) -> str:
    payload = {
        "channel": "feishu",
        "message": {
            "id": "real-openclaw-plugin-smoke",
            "text": text,
            "from": {"id": actor_external_id, "name": "Staff User"},
            "attachments": [],
        },
    }
    return (
        f"import('{PLUGIN_PATH}').then(async m=>{{"
        f"const r=await m.onMessage({json.dumps(payload, ensure_ascii=False)}, {{baseUrl: {json.dumps(base_url)}}});"
        "console.log(JSON.stringify(r));"
        "if(!r.text) process.exit(2);"
        "})"
    )


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


def _summarize_process(process: dict[str, Any]) -> dict[str, Any]:
    return {
        "returncode": process["returncode"],
        "stdout_tail": process["stdout"][-1000:],
        "stderr_tail": process["stderr"][-1000:],
    }


def _summary(output: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": output["ok"],
        "mode": output["mode"],
        "base_url": output["base_url"],
        "plugin_path": output["plugin_path"],
        "inspect_returncode": output["inspect"]["returncode"],
        "invoke_returncode": output["invoke"]["returncode"],
        "reply_text": output["invoke"].get("reply", {}).get("text"),
    }


if __name__ == "__main__":
    main()
