# LandingPage 验收清单（v1.2）

## 首屏以下重构目标

- [x] 首屏以下 section 明显升级，不再只靠卡片堆叠
- [x] 页面加入斜向胶片式视觉段（FilmStrip）
- [x] 页面加入 sticky scroll narrative（WorkflowStory）
- [x] 页面加入视觉资料库段（VisualArchive）
- [x] 页面节奏有深浅切换与留白变化

## 资产与结构

- [x] 新增本地 SVG 资产（4 个）
- [x] `hero-product-mockup.svg` 已使用
- [x] `agent-network-visual.svg` 已使用
- [x] `workflow-loop-visual.svg` 已使用
- [x] `dashboard-preview-dark.svg` 已使用
- [x] 保留老板侧 P0 核心模块（未删除）
- [x] 保留三层 Agent、闭环流程、任务追踪、风险面板、Roadmap
- [x] Footer 升级为完整企业级信息结构

## 真实联调与风险披露

- [x] 保留真实联调状态：后端、`/healthz`、pytest、主链路、DB 核查
- [x] 明确披露风险：`manager_cross_dept` 当前未拒绝（非阻塞）
- [x] 数据可信链路保留：Schema -> API -> Database -> Audit

## 运行与质量

- [x] 本地 `npm install` 成功
- [x] `npm run build` 通过
- [x] Mock fallback 可用
- [x] API 不可用时不会崩溃
- [x] 移动端可用，导航不崩

## 安全

- [x] 未泄露数据库密码
- [x] 未泄露真实 token
- [x] 前端未直连 PostgreSQL
