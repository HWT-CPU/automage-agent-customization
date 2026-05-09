# AutoMage-2 MVP 架构设计文档使用 Skill

## 1. 文档定位

本知识包来自《AutoMage_2_MVP_架构设计文档v1.0.0.pdf》。  
该 PDF 在 `00_SOURCE/` 中为唯一事实源；`01_PAGES/` 为页级结构化抽取；`02_CHAPTERS/` 为按一级书签重组的全文层（原文不删，仅追加结构化占位）。

## 2. 使用优先级

1. `03_INDEX/00_总导航.md`
2. `03_INDEX/01_章节目录索引.md`
3. 与问题相关的专项索引（Schema / API / DB 等）
4. `02_CHAPTERS/` 对应章节
5. `01_PAGES/page_XXXX.md` 页级原文与块锚点
6. 必要时打开 `00_SOURCE/` 下 PDF 核对版式、图表细部

## 3. 回答规则

- 设计结论须带页码或块锚点（见页内 `### block_`）。
- 章节与页级冲突时，以页级与 PDF 为准。
- 原文未写明须标注「文档未明确说明」；禁止将推测写为事实。

## 4. 禁止行为

- 禁止删除原文信息；禁止仅保留摘要替代全文。
- 禁止合并概念导致定义丢失；禁止擅自改写术语。

## 5. 相关文件

- `agent_reading_rules.md`、`citation_policy.md`、`answer_policy.md`、`task_templates.md`
