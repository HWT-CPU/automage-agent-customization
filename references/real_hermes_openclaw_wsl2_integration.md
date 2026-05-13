# Real Hermes / OpenClaw WSL2 Integration

This project now exposes AutoMage Skills through an HTTP Skill Server so the real WSL2 Hermes/OpenClaw stack can call AutoMage without importing Windows Python code.

## Target topology

```text
Windows AutoMage project
  uvicorn automage_agents.server.app:app --host 0.0.0.0 --port 8000
      exposes /hermes/skills and /hermes/skills/{skill_name}/invoke

WSL2 Hermes / OpenClaw
  Hermes: CLI / ACP / MCP / chat -q
  OpenClaw: npm runtime + gateway
      calls Windows AutoMage through http://127.0.0.1:8000/hermes/...

Model router
  http://127.0.0.1:8080/v1/chat/completions
  model: gpt-4o
```

## AutoMage HTTP Skill Server

Endpoints:

- `GET /hermes/healthz`
- `GET /hermes/skills`
- `POST /hermes/skills/{skill_name}/invoke`

Invoke request:

```json
{
  "actor_user_id": "user-001",
  "payload": {
    "query": "OpenAPI 契约",
    "limit": 1
  },
  "trace": {
    "correlation_id": "openclaw-msg-001"
  }
}
```

Invoke response follows the existing AutoMage Hermes envelope:

```json
{
  "ok": true,
  "skill_name": "search_feishu_knowledge",
  "actor_user_id": "user-001",
  "trace": {
    "run_id": "hermes-run-...",
    "trace_id": "hermes-trace-...",
    "correlation_id": "openclaw-msg-001",
    "created_at": "..."
  },
  "result": {
    "ok": true,
    "message": "...",
    "error_code": null,
    "data": {}
  }
}
```

## Start AutoMage on Windows

```powershell
python -m uvicorn automage_agents.server.app:app --host 0.0.0.0 --port 8000
```

For local smoke validation:

```powershell
python scripts/check_real_hermes_skill_server.py --base-url http://127.0.0.1:8000 --summary-only
```

From WSL2:

```bash
curl -s http://127.0.0.1:8000/hermes/healthz
curl -s http://127.0.0.1:8000/hermes/skills
curl -s -X POST http://127.0.0.1:8000/hermes/skills/search_feishu_knowledge/invoke \
  -H 'Content-Type: application/json' \
  -d '{"actor_user_id":"user-001","payload":{"query":"OpenAPI 契约","limit":1},"trace":{"correlation_id":"wsl2-curl-001"}}'
```

## Hermes side integration choice

The user selected Skill discovery option B: Hermes calls AutoMage Skills by HTTP.

Recommended Hermes tool definition shape:

```json
{
  "name": "search_feishu_knowledge",
  "description": "Search AutoMage Feishu knowledge cache.",
  "transport": "http",
  "method": "POST",
  "url": "http://127.0.0.1:8000/hermes/skills/search_feishu_knowledge/invoke"
}
```

If Hermes requires Python skill registration, register a thin Python wrapper that sends HTTP POST to AutoMage instead of importing AutoMage modules from WSL2.

## OpenClaw side integration choice

OpenClaw native event payloads are channel messages, not AutoMage's internal `OpenClawEvent` dataclass.

AutoMage also exposes a bridge endpoint for real OpenClaw channel-style messages:

- `GET /openclaw/healthz`
- `POST /openclaw/events`

Bridge request:

```json
{
  "channel": "feishu",
  "accountId": "openclaw-local-account",
  "message": {
    "id": "msg_001",
    "text": "查知识库 OpenAPI 契约",
    "from": {
      "id": "staff-open-id",
      "name": "Staff User"
    },
    "timestamp": 1740000000000,
    "attachments": []
  }
}
```

Bridge response:

```json
{
  "ok": true,
  "reply": {
    "text": "知识库命中：...",
    "attachments": [],
    "actions": []
  },
  "response": {
    "skill_name": "search_feishu_knowledge",
    "event_type": "knowledge_query"
  }
}
```

Recommended bridge behavior:

```text
OpenClaw channel message.text
  -> choose AutoMage skill by command keywords or model tool-call
  -> POST /hermes/skills/{skill_name}/invoke
  -> reply with result.message or a formatted summary from result.data
```

For the first working path, call these endpoints directly from an OpenClaw plugin or skill:

- `search_feishu_knowledge` for knowledge lookup.
- `post_daily_report` for Staff report submission.
- `fetch_my_tasks` for task query.
- `generate_manager_report` for manager summary.
- `dream_decision_engine` and `commit_decision` for executive decision flow.

Smoke test from Windows:

```powershell
python scripts/check_real_openclaw_bridge.py --base-url http://127.0.0.1:8000 --summary-only
```

Smoke test from WSL2:

```bash
curl -s -X POST http://127.0.0.1:8000/openclaw/events \
  -H 'Content-Type: application/json' \
  -d '{"channel":"feishu","accountId":"openclaw-local-account","message":{"id":"msg_001","text":"查知识库 OpenAPI 契约","from":{"id":"staff-open-id","name":"Staff User"},"attachments":[]}}'
```

## OpenClaw forwarder delivery

An SDK-neutral Node.js forwarder is available at:

- `delivery/openclaw-bridge/automage_openclaw_forwarder.mjs`
- `delivery/openclaw-bridge/README.md`

Run it from WSL2:

```bash
node /mnt/d/Auto-mage2/delivery/openclaw-bridge/automage_openclaw_forwarder.mjs \
  --base-url http://127.0.0.1:8000 \
  --channel feishu \
  --actor staff-open-id \
  --text '查知识库 OpenAPI 契约'
```

Inside a real OpenClaw plugin, import `handleOpenClawMessage(event)` and return the resulting `{ text, attachments, actions }` reply object.

The linked plugin template is available at:

```bash
export PATH="$HOME/.nvm/versions/node/v24.15.0/bin:$PATH"
export AUTOMAGE_OPENCLAW_BRIDGE_URL="http://127.0.0.1:8000"
openclaw plugins install --link /mnt/d/Auto-mage2/delivery/openclaw-bridge/plugin
openclaw plugins list
```

If OpenClaw blocks the `/mnt/d` path as world-writable, install from a native WSL copy:

```bash
mkdir -p ~/.openclaw/local-plugins/automage-openclaw-bridge
cp /mnt/d/Auto-mage2/delivery/openclaw-bridge/automage_openclaw_forwarder.mjs ~/.openclaw/local-plugins/automage_openclaw_forwarder.mjs
cp /mnt/d/Auto-mage2/delivery/openclaw-bridge/plugin/* ~/.openclaw/local-plugins/automage-openclaw-bridge/
chmod 700 ~/.openclaw/local-plugins ~/.openclaw/local-plugins/automage-openclaw-bridge
chmod 600 ~/.openclaw/local-plugins/automage_openclaw_forwarder.mjs ~/.openclaw/local-plugins/automage-openclaw-bridge/*
openclaw plugins install --link ~/.openclaw/local-plugins/automage-openclaw-bridge
openclaw plugins inspect automage-openclaw-bridge
```

Installed-plugin smoke test:

```powershell
python scripts/check_real_openclaw_plugin.py --base-url http://127.0.0.1:8000 --summary-only
```

Gateway readiness smoke test:

```powershell
python scripts/check_real_openclaw_gateway_ready.py --summary-only
```

OpenClaw plugin-tool runtime smoke test:

```powershell
python scripts/check_openclaw_plugin_tool_runtime.py
```

Expected ready summary:

```json
{
  "ok": true,
  "gateway_health_returncode": 0,
  "plugin_inspect_returncode": 0,
  "skill_info_returncode": 0,
  "tool_visible": true,
  "skill_visible": true,
  "blockers": []
}
```

For WSL2 loopback development, the stable gateway setup is:

```bash
openclaw plugins disable bonjour
openclaw gateway stop
systemctl --user disable openclaw-gateway.service
set -a
source ~/.hermes/.env
set +a
export PATH="$HOME/.nvm/versions/node/v24.15.0/bin:$PATH"
export AUTOMAGE_OPENCLAW_BRIDGE_URL="http://127.0.0.1:8000"
export OPENCLAW_NO_RESPAWN=1
setsid openclaw gateway run --force --verbose > /tmp/openclaw/automage-gateway-foreground.log 2>&1 < /dev/null &
```

If `openclaw agent` reports `scope upgrade pending approval`, approve the pending request:

```bash
openclaw devices list
openclaw devices approve <requestId> --json
```

The OpenClaw plugin now exposes:

- Skill: `automage-knowledge`
- Tool contract: `automage_openclaw_event`

To let the embedded ACPX runtime see plugin-registered tools, set:

```json
{
  "plugins": {
    "entries": {
      "acpx": {
        "enabled": true,
        "config": {
          "pluginToolsMcpBridge": true
        }
      }
    }
  }
}
```

Final agent-level validation after the model provider is available:

```powershell
python scripts/check_real_openclaw_gateway_ready.py --summary-only --run-agent --agent-timeout-seconds 220
```

Expected agent-level fields:

```json
{
  "ok": true,
  "blockers": [],
  "agent_returncode": 0,
  "agent_tool_calls": 1,
  "agent_tools": [
    "automage_openclaw_event"
  ],
  "agent_failures": 0
}
```

## Feishu listener through real OpenClaw Agent

By default, the Feishu websocket listener keeps the stable in-process route:

```text
Feishu -> scripts/feishu_event_listener.py -> HermesOpenClawRuntime -> local OpenClaw adapter -> Skill
```

To validate the real OpenClaw Agent/plugin route, start the AutoMage API so `/openclaw/events` is reachable, keep the OpenClaw gateway setup above running, then launch:

```powershell
python scripts/feishu_event_listener.py --route-mode real-openclaw-agent --openclaw-agent main --openclaw-bridge-url http://127.0.0.1:8000
```

In this mode the route is:

```text
Feishu -> scripts/feishu_event_listener.py -> openclaw agent -> automage_openclaw_event -> AutoMage /openclaw/events -> Hermes Skill -> Feishu reply
```

The listener forces the agent prompt to call `automage_openclaw_event` with `text`, `actorExternalId`, and `channel="feishu"`. It treats the run as failed if the agent exits non-zero or if the OpenClaw JSON/tool summary does not show the tool call.

## Current boundary

This implementation does not turn Hermes itself into an HTTP server. Hermes remains the WSL2 CLI/ACP/MCP runtime. AutoMage exposes the HTTP callable Skill surface that Hermes/OpenClaw can consume.

Trace IDs remain AutoMage-owned. Hermes/OpenClaw should pass their own message/session IDs as `trace.correlation_id`.

The model-provider balance blocker was cleared during validation. Agent-level validation now succeeds with `agent_tool_calls=1` and `agent_tools=["automage_openclaw_event"]` when the prompt explicitly asks to use the `automage-knowledge` skill, call `automage_openclaw_event`, avoid `memory_search`, and output only the tool result.

If a future `openclaw agent` run produces a plain natural-language answer instead of selecting `automage_openclaw_event`, use the plugin-tool runtime smoke test above as the authoritative non-LLM validation for OpenClaw plugin tool resolution and execution, then tighten the agent prompt or skill instructions.

## Feishu production loop smoke

The minimal production loop for the business flow is:

```text
Feishu staff daily report
-> Staff report Skill
-> Manager summary Skill
-> Executive Dream decision Skill
-> optional Executive decision commit
-> generated task candidates
```

Mock/agent-side validation:

```powershell
python scripts/feishu_production_loop_smoke.py --summary-only --auto-confirm-decision
```

Expected summary:

```json
{
  "ok": true,
  "stage": "executive_decision",
  "staff_report_ok": true,
  "manager_summary_ok": true,
  "executive_dream_ok": true,
  "executive_decision_ok": true,
  "generated_task_ids": [
    "mock-dream-mock-summary-1-B-1"
  ]
}
```

Without `--auto-confirm-decision`, the loop stops after sending Manager and Executive notification payloads, so the boss can manually confirm the selected option.

The current `FeishuMessageAdapter.send_message()` still returns `feishu_mock` unless a real Lark client is wired through `send_lark_text()`. Real production deployment must provide app credentials, callback verification, open_id mapping, and secure message sending outside repository files.
