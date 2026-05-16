# AutoMage-2 Landing Page 交付说明（P0 v1.2）

本目录用于存放 AutoMage-2 老板侧 Landing Page（Executive Dashboard Demo）相关的交付物、联调资料和数据库对齐资料。

## 目录结构

- `automage_landing_page_delivery/`：Landing Page 主交付目录（含源码、文档、截图）
- `automage_landing_page_delivery_v1.0.0.zip`：历史归档包
- `Mock 与联调资料/`：接口联调、Mock 相关资料
- `数据库与后端/`：数据库字段对齐、后端接口相关资料
- `核心架构与业务逻辑/`：MVP 核心业务逻辑与架构文档

## 当前版本说明

- 版本定位：P0 展示版（v1.2 Scroll + Visual Upgrade）
- 页面目标：用于老板侧演示 AutoMage-2 从 Staff/Manager 报告到 Executive 决策、任务回流与审计追踪的闭环
- 核心特性：
  - Hero 主视觉 + 状态浮层
  - Workflow 叙事化滚动区
  - Agent 三层职责与 API/数据映射
  - Executive Dashboard 与决策面板
  - Integration Status / Data Trust / Risk Disclosure
  - Premium Footer（完整产品信息架构）

## 本地运行（源码位置）

源码目录：

`automage_landing_page_delivery/automage_landing_page`

运行步骤：

```bash
cd automage_landing_page_delivery/automage_landing_page
npm install
npm run dev
```

生产构建：

```bash
cd automage_landing_page_delivery/automage_landing_page
npm run build
```

## 环境变量（可选）

在 `automage_landing_page_delivery/automage_landing_page` 下创建 `.env`：

```env
VITE_AUTOMAGE_API_BASE=http://localhost:8000
VITE_AUTOMAGE_AUTH_TOKEN=dev-token
VITE_AUTOMAGE_DEMO_MODE=true
```

- `VITE_AUTOMAGE_DEMO_MODE=true`：仅使用 mock 数据
- `VITE_AUTOMAGE_DEMO_MODE=false`：优先请求 API，失败时自动回退 mock

## 文档与截图

推荐重点查看：

- `automage_landing_page_delivery/automage_landing_page/docs/设计升级说明_v1.2.md`
- `automage_landing_page_delivery/automage_landing_page/docs/LandingPage验收清单.md`
- `automage_landing_page_delivery/screenshots/`

## 交付建议

- 演示前先执行一次 `npm run build`，确认构建通过
- 演示时建议使用 1440 宽度优先展示视觉节奏，再补充 13 寸与移动端截图
- 对外打包建议在 `automage_landing_page_delivery/` 基础上生成版本化 zip 归档
