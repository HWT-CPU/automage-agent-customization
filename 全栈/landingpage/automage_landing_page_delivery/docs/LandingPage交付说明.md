# AutoMage-2 Landing Page 交付说明

## 页面定位

本页面是 **AutoMage-2 老板侧 Landing Page P0 / Executive Dashboard Demo**，用于展示：

1. AutoMage-2 在 MVP 阶段的组织闭环能力；
2. Staff -> Manager -> Executive -> Task -> 回流 的主链路状态；
3. 当前联调可信度与已知风险（仅 1 项非阻塞 RBAC 风险）；
4. 今日可演示、可复核、可继续扩展到 P1/P2 的状态。

## 技术栈

- React + TypeScript + Vite
- Tailwind CSS
- Recharts（任务状态图）
- Framer Motion（轻动效）
- Lucide React（图标能力，当前页面可继续扩展）

## 如何启动

```bash
cd automage_landing_page
npm install
npm run dev
```

构建：

```bash
npm run build
```

## Demo / API 切换

在 `automage_landing_page` 下配置 `.env`：

```env
VITE_AUTOMAGE_API_BASE=http://localhost:8000
VITE_AUTOMAGE_AUTH_TOKEN=dev-token
VITE_AUTOMAGE_DEMO_MODE=true
```

- `VITE_AUTOMAGE_DEMO_MODE=true`：纯 Mock 展示；
- `VITE_AUTOMAGE_DEMO_MODE=false`：优先请求 API（`/healthz`、`/api/v1/report/staff`、`/api/v1/report/manager`、`/api/v1/tasks`），失败自动 fallback 到 demo data。

## 页面模块

1. 顶部导航（含状态徽标）
2. Hero（定位 + 核心状态）
3. 主链路 Workflow
4. 三层 Agent 卡片
5. 老板侧 Dashboard
6. Executive 决策卡
7. Manager 汇总面板
8. Staff 日报与任务回流
9. 任务看板
10. 风险与异常面板
11. API/DB/Schema 可信证明
12. Roadmap（P0/P1/P2）
13. 技术详情折叠区（统一联调 ID）
14. Footer（风险与联调口径）

## 今日演示建议

推荐按以下顺序演示：

1. Hero：先讲定位（不是普通日报系统）；
2. Workflow：讲清闭环步骤与表/API对应；
3. Dashboard：讲老板每天看什么；
4. Decision Card：演示 A/B 方案确认交互；
5. TaskBoard：展示任务状态流转与回流；
6. 可信证明区：强调 schema、API、表与联调结论；
7. Roadmap：说明 P1/P2 增量范围。

## 当前限制

1. Dream 归并在前端展示层仍以 Mock 输出为主；
2. 决策按钮当前为 Demo 交互，默认未直连 `POST /api/v1/decision/commit`；
3. 已知唯一风险明确展示：`manager_cross_dept` 跨部门提交未拒绝（非阻塞，里程碑三前关闭）；
4. 未包含任何数据库密码或真实 token。
