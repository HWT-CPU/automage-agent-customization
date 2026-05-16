# AutoMage-2 Landing Page (P0 v1.2)

用于展示 AutoMage-2 MVP 老板侧闭环演示页面（Executive Dashboard Demo）。

v1.2 在原工程基础上完成 scroll 与版式升级：首屏以下引入胶片式滚动、sticky workflow、视觉资料库、完整企业级 footer。

## 技术栈

- React + TypeScript + Vite
- Tailwind CSS
- Recharts
- Framer Motion
- Lucide React

## 快速启动

```bash
npm install
npm run dev
```

构建：

```bash
npm run build
```

## 环境变量

创建 `.env`（可选）：

```env
VITE_AUTOMAGE_API_BASE=http://localhost:8000
VITE_AUTOMAGE_AUTH_TOKEN=dev-token
VITE_AUTOMAGE_DEMO_MODE=true
```

- `VITE_AUTOMAGE_DEMO_MODE=true`：强制使用 mock fallback。
- `VITE_AUTOMAGE_DEMO_MODE=false`：优先请求 API，不可用时自动回退 mock。

## 模块说明

页面包含：

1. 顶部导航与联调状态徽标
2. Hero（白底大标题 + 产品主视觉 mockup + 浮动状态卡）
3. 一句话定位区（三层职责分栏）
4. Workflow 闭环（视觉化 + 步骤明细）
5. 三层 Agent 卡片（hover 展开 API/表）
6. 老板侧 P0 Dashboard（深色产品截图风格）
7. Executive 决策卡（本地状态交互）
8. Manager / Staff / Task / Risk / Audit 运行细节面板
9. 真实联调状态矩阵（含风险披露）
10. 数据可信链路（Schema -> API -> Database -> Audit）
11. Roadmap（P0/P1/P2）
12. Final CTA

## 本地视觉资产

位于 `src/assets`：

- `hero-product-mockup.svg`
- `agent-network-visual.svg`
- `workflow-loop-visual.svg`
- `dashboard-preview-dark.svg`
