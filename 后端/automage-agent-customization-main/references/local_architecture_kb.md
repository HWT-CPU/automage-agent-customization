# Local Architecture KB

## Scope

This document registers `AutoMage_2_MVP_KB_v1.0.0` as the local architecture knowledge package for AutoMage-2 MVP.

The package is derived from `AutoMage_2_MVP_架构设计文档v1.0.0.pdf` and is intended for Agent-friendly architecture lookup.

## Location

```text
AutoMage_2_MVP_KB_v1.0.0/
```

Important entry points:

```text
AutoMage_2_MVP_KB_v1.0.0/05_AGENT_SKILL/SKILL.md
AutoMage_2_MVP_KB_v1.0.0/03_INDEX/00_总导航.md
AutoMage_2_MVP_KB_v1.0.0/03_INDEX/01_章节目录索引.md
AutoMage_2_MVP_KB_v1.0.0/02_CHAPTERS/
AutoMage_2_MVP_KB_v1.0.0/01_PAGES/
AutoMage_2_MVP_KB_v1.0.0/00_SOURCE/
```

## Reading order

Use the package in this order:

1. `03_INDEX/00_总导航.md`
2. `03_INDEX/01_章节目录索引.md`
3. Relevant special index, such as Schema, API, DB, Agent responsibility, or task flow index
4. `02_CHAPTERS/` matching chapter
5. `01_PAGES/page_XXXX.md` page-level source text and block anchors
6. `00_SOURCE/` PDF only when page layout or figures must be verified

## Conflict policy

`AutoMage_2_MVP_KB_v1.0.0` is the baseline architecture fact source.

If it conflicts with later milestone documents, database alignment reports, or current implementation files, use the later and more specific document as the operational source.

Priority order:

```text
Current implementation / validated scripts
> Later milestone delivery documents
> Database alignment reports
> AutoMage_2_MVP_KB_v1.0.0
> Earlier summary notes
```

## Citation policy

When using the KB to answer architecture questions, cite a chapter, page file, or block anchor whenever possible.

If the KB does not explicitly state an answer, mark it as not specified instead of treating an inference as fact.

## Current project usage

The KB package currently helps with:

- Architecture Q&A
- Schema / API / DB concept lookup
- Agent responsibility and workflow clarification
- Design traceability during Milestone 2 and Milestone 3 handoff

The KB is not yet indexed into the Feishu local cache pipeline. For now, use it as a local structured reference package.

## Validation

Run the local readiness check together with Yang Zhuo mock workflow validation:

```powershell
python scripts/test_yang_mock_workflow.py
```

Expected result:

```json
{
  "ok": true,
  "local_architecture_kb": {
    "ready": true
  }
}
```
