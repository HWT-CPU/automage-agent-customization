---
name: automage-knowledge
description: Use when the user asks to search AutoMage project knowledge, Feishu wiki cache, project documents, OpenAPI contracts, backend API docs, database specs, Agent skills, or says 查知识库/查询知识库/项目资料/项目文档/查文档/查询文档.
user-invocable: true
---

# AutoMage Knowledge

Use this skill when the user asks for AutoMage project knowledge or project documentation.

## Required Tool

Always call the OpenClaw plugin tool `automage_openclaw_event` for this skill.

Use these arguments:

```json
{
  "text": "<user message>",
  "actorExternalId": "staff-open-id",
  "channel": "openclaw"
}
```

Do not answer AutoMage project-documentation questions from general model memory, `memory_search`, web search, or local files unless `automage_openclaw_event` is unavailable.

## Local Bridge

AutoMage exposes the OpenClaw bridge at:

```text
http://127.0.0.1:8000/openclaw/events
```

Forward the user's message to AutoMage instead of answering from general model memory.

## Request Shape

```json
{
  "channel": "openclaw",
  "message": {
    "id": "openclaw-agent-message",
    "text": "<user message>",
    "from": {
      "id": "staff-open-id",
      "name": "OpenClaw Agent"
    },
    "attachments": []
  }
}
```

## Expected Behavior

Return the `reply_text` or `reply.text` from AutoMage to the user.

If the HTTP bridge is unavailable, report that AutoMage bridge is not reachable and include the URL above.
