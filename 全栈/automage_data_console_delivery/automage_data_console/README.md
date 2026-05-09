# AutoMage-2 Data Console

AutoMage-2 数据中台 / 组织运行控制台。  
该工程用于里程碑三联调入口，不是 Landing Page。

## 启动

```bash
npm install
npm run dev
```

## 构建

```bash
npm run build
```

## 模式说明

- `VITE_AUTOMAGE_DEMO_MODE=true`：默认使用 Demo/Fallback 数据
- `VITE_AUTOMAGE_DEMO_MODE=false`：优先调真实 API，失败自动回退
- `VITE_AUTOMAGE_ENABLE_REAL_WRITE=false`：默认禁止真实写入

## 关键能力

- Staff / Manager / Executive 身份切换（请求头自动注入）
- Workflow DAG + Trace Drawer
- Staff/Manager/Executive 工作台
- 任务中心 / 异常中心
- Agent Adapter 控制台（当前 mock fallback）
- API / DB 监控 + 审计页

## 当前已知风险

`manager_cross_dept` 当前未拒绝，返回 200，里程碑三前需要关闭。
