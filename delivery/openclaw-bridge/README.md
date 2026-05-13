# AutoMage OpenClaw HTTP Forwarder

This folder contains a minimal Node.js forwarder for connecting real WSL2 OpenClaw channel messages to the Windows AutoMage HTTP bridge.

## Files

- `automage_openclaw_forwarder.mjs`: dependency-free Node 18+ module and CLI.

## Prerequisites

Start AutoMage on Windows:

```powershell
python -m uvicorn automage_agents.server.app:app --host 0.0.0.0 --port 8000
```

From WSL2, verify the bridge:

```bash
curl -s http://127.0.0.1:8000/openclaw/healthz
```

## CLI smoke test from WSL2

Copy or run this file from the repository path mounted under `/mnt/d`:

```bash
node /mnt/d/Auto-mage2/delivery/openclaw-bridge/automage_openclaw_forwarder.mjs \
  --base-url http://127.0.0.1:8000 \
  --channel feishu \
  --actor staff-open-id \
  --text '查知识库 OpenAPI 契约'
```

It returns the full AutoMage bridge response. The channel reply text is at `reply.text`.

## Module usage inside an OpenClaw plugin or skill

```js
import { handleOpenClawMessage } from './automage_openclaw_forwarder.mjs';

export async function onMessage(event) {
  return await handleOpenClawMessage(event, {
    baseUrl: process.env.AUTOMAGE_OPENCLAW_BRIDGE_URL || 'http://127.0.0.1:8000',
  });
}
```

Expected OpenClaw-like event shape:

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
    "attachments": []
  }
}
```

## Environment variables

- `AUTOMAGE_OPENCLAW_BRIDGE_URL`: defaults to `http://127.0.0.1:8000`.
- `AUTOMAGE_OPENCLAW_TIMEOUT_MS`: defaults to `30000`.
- `OPENCLAW_CHANNEL`: fallback channel name.
- `OPENCLAW_ACCOUNT_ID`: fallback account id.
- `OPENCLAW_ACTOR_ID`: fallback sender id.

## Integration boundary

This file is intentionally SDK-neutral. Once the exact OpenClaw plugin lifecycle is confirmed, keep `forwardOpenClawEvent()` and replace only the small `onMessage()` wrapper with the official SDK registration code.

## OpenClaw plugin template

A local plugin template is provided at:

```text
delivery/openclaw-bridge/plugin/
```

It contains:

- `package.json`
- `index.mjs`
- `openclaw.plugin.json`

The entry exports multiple common lifecycle names so it can be adapted quickly once the exact OpenClaw SDK hook name is confirmed:

- `onMessage(event, context)`
- `handleMessage(event, context)`
- `run(input, context)`
- `invoke(input, context)`

Install as a linked local plugin from WSL2:

```bash
export PATH="$HOME/.nvm/versions/node/v24.15.0/bin:$PATH"
export AUTOMAGE_OPENCLAW_BRIDGE_URL="http://127.0.0.1:8000"
openclaw plugins install --link /mnt/d/Auto-mage2/delivery/openclaw-bridge/plugin
openclaw plugins list
```

On WSL2, OpenClaw may block `/mnt/d/...` plugins because Windows-mounted paths can appear world-writable. In that case, copy the plugin to a native WSL directory first:

```bash
mkdir -p ~/.openclaw/local-plugins/automage-openclaw-bridge
cp /mnt/d/Auto-mage2/delivery/openclaw-bridge/automage_openclaw_forwarder.mjs ~/.openclaw/local-plugins/automage_openclaw_forwarder.mjs
cp /mnt/d/Auto-mage2/delivery/openclaw-bridge/plugin/package.json ~/.openclaw/local-plugins/automage-openclaw-bridge/package.json
cp /mnt/d/Auto-mage2/delivery/openclaw-bridge/plugin/index.mjs ~/.openclaw/local-plugins/automage-openclaw-bridge/index.mjs
cp /mnt/d/Auto-mage2/delivery/openclaw-bridge/plugin/openclaw.plugin.json ~/.openclaw/local-plugins/automage-openclaw-bridge/openclaw.plugin.json
chmod 700 ~/.openclaw/local-plugins ~/.openclaw/local-plugins/automage-openclaw-bridge
chmod 600 ~/.openclaw/local-plugins/automage_openclaw_forwarder.mjs ~/.openclaw/local-plugins/automage-openclaw-bridge/*
openclaw plugins install --link ~/.openclaw/local-plugins/automage-openclaw-bridge
openclaw plugins inspect automage-openclaw-bridge
```

The plugin is intentionally a thin wrapper around `automage_openclaw_forwarder.mjs`.

Final installed-plugin smoke test from Windows:

```powershell
python scripts/check_real_openclaw_plugin.py --base-url http://127.0.0.1:8000 --summary-only
```

Gateway readiness check from Windows:

```powershell
python scripts/check_real_openclaw_gateway_ready.py --summary-only
```

OpenClaw plugin-tool runtime check from Windows:

```powershell
python scripts/check_openclaw_plugin_tool_runtime.py
```

Optional final agent validation after the model provider is available:

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

## WSL2 gateway notes

For local gateway testing, the following WSL2-specific issues were observed:

- OpenClaw may reject `/mnt/d/...` linked plugins as world-writable. Use the native WSL copy path above.
- The bundled `bonjour` plugin can fail in WSL2 mDNS advertising with `CIAO ANNOUNCEMENT CANCELLED`; disable it for loopback-only development:

```bash
openclaw plugins disable bonjour
```

- The systemd gateway service may not inherit shell-loaded `.env` secrets. For local bridge validation, stop the service and run the gateway from a shell that has sourced the environment:

```bash
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

- If the CLI reports `scope upgrade pending approval`, approve the latest pending device request:

```bash
openclaw devices list
openclaw devices approve <requestId> --json
```

- To expose plugin-registered tools to the embedded agent runtime, enable the ACPX plugin-tools bridge in `~/.openclaw/openclaw.json`:

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

If `openclaw agent` fails with a model-provider 403 or insufficient balance error, the gateway/plugin path is ready but automatic agent tool invocation is blocked until the model provider is available.

If `openclaw agent` returns a normal natural-language answer without calling `automage_openclaw_event`, run `check_openclaw_plugin_tool_runtime.py`. If that script succeeds, the plugin tool runtime is healthy and the remaining issue is agent tool-selection or embedded ACP tool injection behavior rather than the AutoMage bridge.

The agent-level validation is sensitive to prompt wording. The stable validation prompt explicitly says to use the `automage-knowledge` skill, call `automage_openclaw_event`, avoid `memory_search`, and output only the tool result.
