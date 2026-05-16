# Hermes / OpenClaw Runtime

This project treats Hermes and OpenClaw as AutoMage runtime layers.

## Concepts

Hermes is the Agent and Skill runtime. It loads Agent profiles, prepares Skill contexts, invokes registered Skills, and returns normalized results.

OpenClaw is the event and channel gateway. It receives user text from CLI, Feishu, mock scripts, or future HTTP webhooks, parses the command, maps the actor identity, invokes Hermes, and formats a reply.

## Runtime flow

```text
CLI / Feishu / Mock / HTTP
        -> OpenClawEvent
        -> LocalOpenClawClient
        -> OpenClawCommandParser
        -> HermesInvokeRequest
        -> LocalHermesClient
        -> Skill Registry
        -> Staff / Manager / Executive Skill
        -> AutoMageApiClient or MockAutoMageApiClient
```

## Configuration files

### `configs/hermes.example.toml`

Controls how Hermes loads Agents and contexts.

Important fields:

- `hermes.enabled`
- `hermes.runtime_name`
- `hermes.mode`
- `hermes.settings_path`
- `hermes.use_mock_api`
- `hermes.agents.staff.profile_path`
- `hermes.agents.manager.profile_path`
- `hermes.agents.executive.profile_path`

### `configs/openclaw.example.toml`

Controls channels, routing names, and command keywords.

Important fields:

- `openclaw.default_channel`
- `openclaw.reply_enabled`
- `openclaw.channels.cli.enabled`
- `openclaw.channels.feishu.enabled`
- `openclaw.commands.task_query.keywords`
- `openclaw.commands.daily_report.keywords`
- `openclaw.commands.executive_decision.keywords`
- `openclaw.commands.markdown_import.keywords`

### `.env`

Only secrets and environment-specific values belong in `.env`.

For local mock CLI, no Feishu secret is required.

For real Feishu websocket listener, set:

```env
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
FEISHU_EVENT_MODE=websocket
```

Do not commit `.env`.

## Local CLI usage

Submit a daily report:

```powershell
python scripts/openclaw_cli.py "今天完成了客户跟进，遇到的问题是报价周期不明确，明天继续推进。"
```

Query tasks:

```powershell
python scripts/openclaw_cli.py "查任务"
```

Submit an executive decision:

```powershell
python scripts/openclaw_cli.py "决策 A，先稳定本地 Hermes/OpenClaw 契约。" --actor executive-open-id
```

Import a formal Markdown daily report:

```powershell
python scripts/openclaw_cli.py "导入日报 # 日报\n今日完成正式日报入库验证。"
```

Print full JSON response:

```powershell
python scripts/openclaw_cli.py "查任务" --json
```

## Real Feishu listener

After Feishu app credentials are configured in `.env`, run:

```powershell
python scripts/feishu_event_listener.py
```

Then send private messages to the bot in Feishu.

## Current boundary

The current implementation is a local client/runtime implementation:

- `LocalHermesClient`
- `LocalOpenClawClient`
- `HermesOpenClawRuntime`

It does not require an external Hermes or OpenClaw service. If Hermes/OpenClaw are later split into independent services, add HTTP clients beside the local clients without changing CLI/Feishu command semantics.
