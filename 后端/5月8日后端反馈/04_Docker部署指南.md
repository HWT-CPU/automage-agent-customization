# Docker 部署指南
日期：2026-05-08

## 一、文档目的

本文档用于说明 AutoMage 后端当前的 Docker 容器化部署方式，内容已对齐 2026-05-08 的最新项目状态。

---

## 二、当前支持范围

当前项目已经具备以下容器化基础能力：

- API 服务可通过 Docker 启动
- 本地联调可通过 `docker compose` 同时启动 API、PostgreSQL 和 Redis
- 可切换为连接远程 PostgreSQL
- Redis 7.0 已纳入默认编排，并用于限流与幂等能力

当前仓库内已有文件：

- `Dockerfile`
- `docker-compose.yml`
- `docker-compose.override.yml`
- `configs/automage.docker.toml`

---

## 三、部署模式

### 1. 本地联调模式

适用场景：

- 本地开发
- 接口联调
- Swagger 验证
- 本地数据库联调

特点：

- 使用 `docker compose up -d --build`
- 会自动应用 `docker-compose.override.yml`
- 会启动：
  - `api`
  - `postgres`
  - `redis`

### 2. 远程数据库模式

适用场景：

- 连接公司或测试环境数据库
- 本地仅运行 API 和 Redis 容器
- 不启本地 PostgreSQL 容器

特点：

- 使用 `docker compose -f docker-compose.yml up -d --build`
- 会启动：
  - `api`
  - `redis`
- 数据库通过配置连接远程 PostgreSQL

---

## 四、前置条件

开始之前请确认本机已安装：

- Docker
- Docker Compose

建议确认版本：

```bash
docker --version
docker compose version
```

---

## 五、项目文件说明

### 1. Dockerfile

作用：

- 构建 API 镜像
- 安装 Python 依赖
- 复制 `automage_agents / scripts / configs`

### 2. docker-compose.yml

作用：

- 定义基础 `api` 服务
- 定义 `redis` 服务
- API 默认连接 Compose 内部 Redis

### 3. docker-compose.override.yml

作用：

- 本地开发时自动生效
- 注入：
  - `AUTOMAGE_CONFIG_PATH=/app/configs/automage.docker.toml`
- 额外挂起本地 `postgres` 容器

### 4. configs/automage.docker.toml

作用：

- Docker 本地联调默认配置
- 默认使用容器内 `postgres` 主机名
- 默认启用 Redis 版限流与幂等

---

## 六、本地联调模式部署

### 1. 复制环境变量文件

```bash
cp .env.example .env
```

### 2. 启动服务

```bash
docker compose up -d --build
```

### 3. 启动后容器

- `api`
- `postgres`
- `redis`

### 4. 访问地址

- Swagger：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/healthz`

---

## 七、远程数据库模式部署

### 1. 复制环境变量文件

```bash
cp .env.example .env
```

### 2. 修改数据库连接

将 `.env` 中以下配置改为目标环境：

```env
AUTOMAGE_DB_HOST=182.92.93.16
AUTOMAGE_DB_PORT=5432
AUTOMAGE_DB_NAME=automage
AUTOMAGE_DB_USER=automage
AUTOMAGE_DB_PASSWORD=automage
AUTOMAGE_DB_SSLMODE=prefer
```

### 3. 启动服务

```bash
docker compose -f docker-compose.yml up -d --build
```

说明：

- 该命令只使用基础 Compose 文件
- 不会自动启动本地 PostgreSQL 容器

---

## 八、Redis 版限流与幂等

### 1. 当前状态

当前后端已支持两种防滥用后端：

- `memory`
- `redis`

建议：

- 简单本地调试可使用 `memory`
- 容器化联调及多实例环境建议使用 `redis`

### 2. Compose 默认 Redis 服务

当前 `docker-compose.yml` 已包含 Redis 服务，镜像版本固定为：

```text
redis:7.0
```

当前 Redis 服务特征：

- 服务名：`redis`
- 密码：`automage`
- 已开启 AOF 持久化
- 已挂载数据卷：`automage_redis_data`

### 3. Redis 连接验证

```bash
docker compose exec redis redis-cli -a automage ping
```

预期返回：

```text
PONG
```

### 4. API 默认 Redis 配置

当前 Compose 默认已为 API 注入以下配置：

```env
AUTOMAGE_ABUSE_PROTECTION_ENABLED=true
AUTOMAGE_ABUSE_PROTECTION_BACKEND=redis
AUTOMAGE_RATE_LIMIT_WINDOW_SECONDS=60
AUTOMAGE_RATE_LIMIT_MAX_REQUESTS=60
AUTOMAGE_IDEMPOTENCY_TTL_SECONDS=300
AUTOMAGE_REDIS_URL=redis://:automage@redis:6379/0
AUTOMAGE_REDIS_KEY_PREFIX=automage
```

如果 API 在宿主机本地运行，可使用：

```env
AUTOMAGE_REDIS_URL=redis://:automage@127.0.0.1:6379/0
```

---

## 九、常用验证命令

### 1. 查看容器状态

```bash
docker compose ps
```

### 2. 查看 API 日志

```bash
docker compose logs -f api
```

### 3. 查看 Redis 日志

```bash
docker compose logs -f redis
```

### 4. 查看 PostgreSQL 日志

```bash
docker compose logs -f postgres
```

### 5. 检查数据库连通性

```bash
python scripts/check_postgres.py
```

### 6. 检查接口存活状态

```bash
curl http://localhost:8000/healthz
```

---

## 十、当前边界

当前 Docker 化方案已经能满足：

- API 容器启动
- 本地 PostgreSQL 联调
- 远程 PostgreSQL 连接
- Redis 7.0 接入
- Redis 版限流与幂等接入

当前尚未纳入默认容器编排的内容包括：

1. Scheduler 独立容器
2. 完整生产环境多服务编排
3. 监控、告警与日志采集

---

## 十一、结论

当前项目已经具备基础 Docker 容器化部署能力，可支持本地联调和远程数据库两种场景，并已纳入 Redis 7.0 作为默认防滥用组件。
