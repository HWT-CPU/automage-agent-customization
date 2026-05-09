from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.core.enums import RuntimeChannel
from automage_agents.integrations.hermes import HermesOpenClawRuntime
from automage_agents.integrations.openclaw import OpenClawEvent


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AutoMage OpenClaw local CLI event through Hermes runtime.")
    parser.add_argument("text", help="User text to submit to OpenClaw.")
    parser.add_argument("--actor", default="staff-open-id", help="External actor id, e.g. Feishu open_id or local user id.")
    parser.add_argument("--channel", choices=["cli", "feishu", "mock"], default="cli")
    parser.add_argument("--hermes-config", default="configs/hermes.example.toml")
    parser.add_argument("--openclaw-config", default="configs/openclaw.example.toml")
    parser.add_argument("--json", action="store_true", help="Print full JSON response.")
    args = parser.parse_args()

    runtime = HermesOpenClawRuntime.from_config_files(
        hermes_config_path=args.hermes_config,
        openclaw_config_path=args.openclaw_config,
        user_mapping={"staff-open-id": "user-001", "manager-open-id": "manager-001", "executive-open-id": "executive-001"},
    )
    if runtime.openclaw_client is None:
        raise RuntimeError("OpenClaw client was not initialized.")

    response = runtime.openclaw_client.submit_event(
        OpenClawEvent(
            channel=RuntimeChannel(args.channel),
            actor_external_id=args.actor,
            text=args.text,
        )
    )
    if args.json:
        print(json.dumps({"response": response.to_dict(), "state": runtime.state_summary()}, ensure_ascii=False, indent=2))
        return
    print(response.reply_text)


if __name__ == "__main__":
    main()
