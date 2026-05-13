from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    args = _parse_args()
    base_url = args.base_url.rstrip("/")
    checks = [
        _request_json("GET", f"{base_url}/openclaw/healthz", timeout=args.timeout_seconds),
        _request_json(
            "POST",
            f"{base_url}/openclaw/events",
            payload={
                "channel": args.channel,
                "accountId": args.account_id,
                "message": {
                    "id": args.message_id,
                    "text": args.text,
                    "from": {"id": args.actor_external_id, "name": args.actor_name},
                    "attachments": [],
                },
            },
            timeout=args.timeout_seconds,
        ),
    ]
    output = {
        "ok": all(check.get("ok") for check in checks),
        "base_url": base_url,
        "mode": "real_openclaw_bridge_smoke",
        "checks": checks,
    }
    if args.output_json:
        Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output_json).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(_summary(output) if args.summary_only else output, ensure_ascii=False, indent=2))
    if not output["ok"]:
        raise SystemExit(1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test AutoMage OpenClaw HTTP bridge for WSL2 OpenClaw channel integration.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--channel", default="feishu")
    parser.add_argument("--account-id", default="openclaw-local-account")
    parser.add_argument("--message-id", default="openclaw-smoke-msg-001")
    parser.add_argument("--actor-external-id", default="staff-open-id")
    parser.add_argument("--actor-name", default="Staff User")
    parser.add_argument("--text", default="查知识库 OpenAPI 契约")
    parser.add_argument("--timeout-seconds", type=float, default=10.0)
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--output-json")
    return parser.parse_args()


def _request_json(method: str, url: str, *, payload: dict[str, Any] | None = None, timeout: float) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(url, data=body, method=method, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8")
            data = json.loads(text) if text else None
            return {"ok": 200 <= response.status < 300, "method": method, "url": url, "status": response.status, "data": data}
    except HTTPError as exc:
        error_text = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "method": method, "url": url, "status": exc.code, "error": error_text[:1000]}
    except URLError as exc:
        return {"ok": False, "method": method, "url": url, "status": None, "error": str(exc.reason)}


def _summary(output: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": output["ok"],
        "base_url": output["base_url"],
        "mode": output["mode"],
        "checks": [
            {
                "ok": check.get("ok"),
                "method": check.get("method"),
                "url": check.get("url"),
                "status": check.get("status"),
                "reply_text": (check.get("data") or {}).get("reply", {}).get("text"),
                "skill_name": (check.get("data") or {}).get("response", {}).get("skill_name"),
                "error": check.get("error"),
            }
            for check in output["checks"]
        ],
    }


if __name__ == "__main__":
    main()
