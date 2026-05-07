# Feishu Knowledge Base Integration

The Feishu Wiki knowledge base replaces the previous Feishu cloud-drive source for Agent-readable project knowledge.

The old cloud-drive files are not exposed through external Feishu APIs. The Wiki structure can be routed through node tokens and fetched through the Feishu docs CLI/API path.

## Entry protocol

Agent usage protocol:

1. Read `00 Agent 入口与索引协议`.
2. Select a section by task type.
3. Enter the section index and locate the target document token.
4. Fetch document body with:

```powershell
lark-cli docs +fetch --api-version v2 --doc <token>
```

## Local routing config

The local routing table is represented by:

```text
configs/feishu_knowledge.example.toml
```

It maps project questions to Feishu Wiki section `node_token` values.

## Local route check

Example:

```powershell
python scripts/knowledge_route_cli.py "数据库 API 接口在哪里"
```

Expected route:

```text
07 数据库与后端 API
```

Full JSON:

```powershell
python scripts/knowledge_route_cli.py "Agent Skill 编排规范" --json
```

## Current boundary

The current implementation routes a query to the correct Wiki section and prints the CLI fetch command.

The local wrapper executes `lark-cli docs +fetch --api-version v2`, then caches fetched content under `_cache/feishu_wiki/`.

Before fetching real documents, initialize and authenticate the official Feishu CLI:

```powershell
lark-cli config init --new
lark-cli auth login --domain docs
```

Wrapper usage:

```powershell
python scripts/feishu_knowledge_fetch.py --query "数据库 API 接口在哪里"
python scripts/feishu_knowledge_fetch.py --doc YeX0wA2NLiueeXktCLQcnKOTnMh
python scripts/feishu_knowledge_fetch.py --query "Agent Skill 编排规范" --dry-run --json
```

Batch sync:

```powershell
python scripts/feishu_knowledge_sync.py
python scripts/feishu_knowledge_sync.py --no-linked-docs --json
```

Local cache search:

```powershell
python scripts/feishu_knowledge_search.py "数据库 API" --limit 3
python scripts/feishu_knowledge_context.py "OpenAPI 契约" --limit 2
python scripts/agent_runtime_context.py "OpenAPI 契约" --json
python scripts/agent_prompt_preview.py "OpenAPI 契约" --role staff
python scripts/knowledge_business_flow.py "OpenAPI 契约"
python scripts/knowledge_auto_skill_flow.py "OpenAPI 契约"
python scripts/openclaw_cli.py "查知识库 数据库 API" --json
```

Hermes Skill:

```text
search_feishu_knowledge
```

The Skill reads `_cache/feishu_wiki/manifest.json` and returns ranked cached snippets.

It also returns a prompt-ready block at:

```text
data.knowledge_context.context_text
```

After `search_feishu_knowledge` runs, the current Agent runtime context also contains:

```text
runtime.input_refs.feishu_knowledge.context_text
```

For standalone runtime payload generation:

```powershell
python scripts/agent_runtime_context.py "OpenAPI 契约" --json
```

For local prompt preview before the Hermes official template format is finalized:

```powershell
python scripts/agent_prompt_preview.py "OpenAPI 契约" --role staff
```

Business Skills use the runtime context to write lightweight source references into structured outputs:

```text
staff_report.meta.knowledge_refs.feishu_knowledge
manager_report.meta.knowledge_refs.feishu_knowledge
dream_decision.data.knowledge_refs.feishu_knowledge
decision_payload.meta.knowledge_refs.feishu_knowledge
```

The business payload only stores lightweight references. The full prompt block stays in:

```text
runtime.input_refs.feishu_knowledge.context_text
```

Business Skills also auto-retrieve knowledge when no `runtime.input_refs.feishu_knowledge` exists yet:

```text
post_daily_report
generate_manager_report
dream_decision_engine
commit_decision
```

The auto query is built from semantic business fields, then the cached Feishu context is attached to runtime before schema coercion or decision commit.

The same context is used to enrich concrete Skill parameters:

```text
staff_report.artifacts[]                    # context artifact with knowledge refs
manager_report.next_day_adjustment[]        # execution alignment adjustment
dream_decision.input.external_variables     # knowledge query/source metadata
decision_payload.task_candidates[].meta     # task-level knowledge refs
```

Validate the no-manual-injection path with:

```powershell
python scripts/knowledge_auto_skill_flow.py "OpenAPI 契约"
```

The block format is:

```xml
<feishu_knowledge_context>
<query>...</query>
<source id="1" title="..." token="..." score="...">
...
</source>
</feishu_knowledge_context>
```

## Current sync status

The latest verified sync result:

```text
section indexes: 10/10
linked docs: 9/12
file tokens recorded: 3
```

Failed linked docs are kept in `manifest.json` with their Feishu error messages:

- `GhIywTehziymJckhr1acgYY0ndg` 里程碑交付
- `ModewBap5i5zdckLJUFc6QVmn2e` 基础架构补齐
- `MGxfbX3FGoWS43xD0rpccFnrn9d` 杨卓项目计划 v1.0.0 (PDF 附件)

## Suggested runtime flow

```text
User question
  -> OpenClaw command parser
  -> Hermes knowledge Skill
  -> Feishu knowledge router
  -> section node_token
  -> lark-cli docs +fetch --api-version v2 --doc <token>
  -> cached document body
  -> Agent answer or downstream Skill input
```

## Section routing

- `01` 项目总览与边界
- `02` 里程碑与交付计划
- `03` 会议纪要与决策记录
- `04` 架构设计
- `05` Agent 编排与 Skill
- `06` Schema DAG Workflow
- `07` 数据库与后端 API
- `08` 日报模板与试点样例
- `09` WebUI Landing Page 企业交付
- `99` 原始资料归档
