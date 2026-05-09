# Source Of Truth

Use these files as the primary alignment references for AutoMage:

- `D:/Code/AutoMage/输出文档/13数据库规范.md`
  - naming, key style, timestamps, indexes, general SQL conventions
- `D:/Code/AutoMage/输出文档/14数据模型概览.md`
  - fast overview of the current entity model
- `D:/Code/AutoMage/输出文档/15业务表DDL.sql`
  - authoritative table, column, constraint, trigger, and index definitions
- `D:/Code/AutoMage/输出文档/16接口契约.md`
  - authoritative API request/response and pagination contracts
- `D:/Code/AutoMage/输出文档/19数据库ER图.md`
  - relationship and cross-module flow reference
- `D:/Code/AutoMage/输出文档/7职责边界.md`
  - module boundaries when deciding where code should live

## Quick Lookup

- Work record schema: `form_templates`, `work_records`, `work_record_items`
- Summaries: `summaries`, `summary_source_links`
- Decision panel: `decision_records`, `decision_logs`
- External identity mapping: `external_identities`
- Audit trail: `audit_logs`

## Expected Update Set

If a change affects persistence:

- update DDL first
- then update ER or data model
- then update interface contract if API-visible

If a change affects only implementation details without changing behavior:

- still verify against DDL and interface contract before coding
