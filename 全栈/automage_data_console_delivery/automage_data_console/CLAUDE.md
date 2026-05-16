# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AutoMage-2 数据中台/组织运行控制台 — React 18 + Vite 前端 + Python FastAPI 后端，全栈一体化。支持三身份（Staff / Manager / Executive）的 RBAC 隔离工作台，Workflow DAG 追踪，任务/异常中心，Agent Adapter 控制台。

## Commands

```bash
# Frontend
npm install                       # 安装前端依赖
npm run dev                       # Vite 开发服务器 localhost:5174
npm run build                     # TypeScript 编译 + Vite 生产构建
npm run typecheck                 # 仅类型检查（不构建）
npm run lint                      # ESLint 检查
npm run smoke:api                 # API 冒烟测试
npm run check:secrets             # 密码泄露检查

# Backend (必须先 conda activate yz)
cd backend && pip install -e .    # 安装后端依赖
cd backend && python scripts/init_db.py    # 初始化数据库
cd backend && python scripts/run_api.py    # 启动 API localhost:8000
cd backend && python scripts/demo_mock_flow.py  # mock 全流程
cd backend && python scripts/render_agents.py --user examples/user.staff.example.toml --output /tmp/agents.md

# Docker 全栈部署
docker compose up -d --build      # 访问 localhost:8080
```

## Architecture

### 前端 `src/`

```
src/
├── pages/          # 路由页面（10个），每个对应一条侧边栏导航
├── components/     # 按域分组的业务组件
│   ├── layout/     # AppShell, Sidebar, Topbar, RoleSwitcher
│   ├── staff/      # StaffReportComposer, StaffTaskInbox, StaffReportPreview
│   ├── manager/    # DepartmentReportTable, RiskAggregationPanel, ManagerSummaryBuilder
│   ├── executive/  # ExecutiveDecisionCenter, DreamRunPanel, DecisionCard
│   ├── workflow/   # WorkflowGraph, DataTraceDrawer, WorkflowRunConsole
│   ├── tasks/      # TaskBoard, TaskDetailDrawer, TaskUpdateForm
│   ├── incidents/  # IncidentBoard, IncidentDetailDrawer
│   ├── monitor/    # ApiLogViewer, AuditTimeline, ApiHealthPanel, IntegrationStatusMatrix
│   └── common/     # StatusBadge, EmptyState, JsonViewer, ConfirmDialog
├── store/          # Zustand stores (useRuntimeStore, useIdentityStore, useWorkflowStore, etc.)
├── lib/            # apiClient, payloadBuilders, requestHeaders, idempotency, schemaValidator
├── agent/          # Agent adapter + mock fallback（staff/manager/executive）
├── config/         # env 配置，identity profiles，常量
├── data/           # Mock 数据（mockTasks, mockStaffReports, demoWorkflow 等）
└── router/         # React Router v6 路由定义
```

- **状态管理**: Zustand，无额外封装。各自 store 独立，通过 selector 使用。
- **API 调用**: `AutomageApiClient` 单例 (`src/lib/apiClient.ts`)，内置 demo 模式（`VITE_AUTOMAGE_DEMO_MODE=true` 直接返回 mock 数据）、真实写入开关（`VITE_AUTOMAGE_ENABLE_REAL_WRITE`）、幂等键注入、30s 超时。
- **身份系统**: `useIdentityStore` 管理当前身份切换，`buildHeaders()` 自动注入 `X-Actor-Role` / `X-Actor-User-Id` / `X-Node-Id` / `X-Request-Id`。
- **环境变量**: 以 `VITE_AUTOMAGE_` 为前缀，在 `src/config/env.ts` 集中读取。

### 后端 `backend/automage_agents/`

```
backend/automage_agents/
├── server/         # FastAPI app + CRUD routes + RBAC + middleware + audit
│   ├── app.py      # 所有 API 路由（report, dream, decision, tasks, audit-logs, generic CRUD）
│   ├── auth.py     # 身份断言、RBAC scope 过滤
│   ├── service.py  # 业务逻辑（create_staff_report, create_manager_report, commit_decision 等）
│   ├── crud.py     # 通用 CRUD（MODEL_REGISTRY 动态表路由）
│   ├── middleware.py # RequestTracking + AbuseProtection（限流 + 幂等）
│   └── rbac.py     # RBAC 执行引擎
├── db/             # SQLAlchemy ORM (20+ 表), session 管理
├── skills/         # Per-tier 技能实现（staff.py, manager.py, executive.py）
├── schemas/        # 日报 schema 解析/持久化/渲染
├── api/            # HTTP client / mock client / SQLAlchemy client
├── integrations/   # Feishu (Lark), Hermes, OpenClaw 适配器 + event router
├── knowledge/      # 飞书知识库同步、自动上下文、payload enrichment
├── scheduler/      # 后台 cron (staff_daily_reminder, manager_summary_auto_generate)
├── templates/      # Agent prompt 模板 + prompt_builder
└── config/         # RuntimeSettings + PostgresSettings（env/TOML 驱动）
```

- **配置加载**: 优先读取 `AUTOMAGE_` 环境变量，其次 `configs/automage.local.toml` 和 `.env`。
- **API envelope**: 所有响应包裹在 `{ code, data, msg }` 中，冲突用 409 + `error` 字段。
- **中间件**: `RequestTrackingMiddleware`（注入 request_id）→ `AbuseProtectionMiddleware`（速率限制 + 写路径幂等）。
- **鉴权模型**: `get_current_actor()` 从请求头 `X-Actor-Role` / `X-Actor-User-Id` 解析身份，业务路由通过 `assert_actor_has_role()` / `assert_identity_matches_actor()` 校验。

### 关键数据流

1. **Staff 日报**: POST `/api/v1/report/staff` → conflict check (org_id, user_id, record_date) → 写入 work_record + items + incident + audit log
2. **Manager 汇总**: POST `/api/v1/report/manager` → 聚合 staff reports → 创建 SummaryModel + summary_source_links + snapshot
3. **Dream 决策**: POST `/internal/dream/run` → 从 manager summary 生成 A/B 决策选项
4. **Decision Commit**: POST `/api/v1/decision/commit` → 创建 decision_record → 创建 tasks + task_assignments + task_queue

### Docker 网络

- `frontend` (Nginx, :8080) → 代理 `/api/` `/internal/` 到 `api:8000`
- `api` (FastAPI) → 依赖 `postgres` (:5432) + `redis` (:6379)
- Redis 用于 Abuse Protection（限流 + 幂等），需密码认证
