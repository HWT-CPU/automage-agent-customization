# AutoMage-2 Data Console (Full-Stack)

AutoMage-2 数据中台 / 组织运行控制台。  
前端（React + Vite）+ 后端（Python FastAPI）一体化项目。

## 项目结构

```
├── src/                 # 前端源码 (React + TypeScript + Vite)
├── backend/             # 后端源码 (Python FastAPI)
│   ├── automage_agents/ # FastAPI 应用包
│   ├── scripts/         # CLI 入口 (run_api, init_db, demo_mock_flow, ...)
│   └── configs/         # TOML 配置文件
├── docker-compose.yml   # 全栈容器化部署
├── Dockerfile           # 前端 Nginx 镜像
├── nginx.conf           # Nginx 代理配置
└── package.json
```

## 本地开发

### 1. 后端 (Conda yz 环境)

```bash
cd backend
cp .env.example .env        # 配置数据库等环境变量
conda activate yz           # 使用 conda yz 环境
pip install -e .            # 安装依赖
python scripts/init_db.py   # 初始化数据库表
python scripts/run_api.py   # 启动 API (localhost:8000)
```

### 2. 前端 (另一个终端)

```bash
cp .env.example .env
npm install
npm run dev               # 启动 Vite 开发服务器 (localhost:5174)
```

前端默认通过 `VITE_AUTOMAGE_API_BASE=http://localhost:8000` 直接调用后端。
Vite 也已配置代理，可设置 `VITE_AUTOMAGE_API_BASE=`（空字符串）走 Vite 代理。

## Docker 全栈部署

```bash
docker compose up -d --build
```

访问 `http://localhost:8080`，前端 Nginx 会自动将 `/api/` 请求代理到后端。

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
