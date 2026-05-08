# Docker 部署指南

本文档用于说明 AutoMage 后端当前的 Docker 容器化部署方式，内容已经对齐 2026-05-08 最新项目状态。

当前文档重点覆盖：

- API 容器部署
- Postgres 容器联动
- Redis 7.0 容器接入
- 远程数据库部署方式
- Redis 版限流 / 幂等接入方式
- 常用验证命令

---

## 1. 当前容器化范围

当前项目已经具备以下容器化基础：

- API 服务可通过 Docker 启动
- 本地联调可通过 `docker compose` 同时拉起 API + Postgres + Redis
- 可切换为连接远程 PostgreSQL
- Redis 版限流 / 幂等已经接入容器化部署

当前仓库内已有文件：

- `Dockerfile`
- `docker-compose.yml`
- `docker-compose.override.yml`
- `configs/automage.docker.toml`

说明：

- `docker-compose.yml` 负责基础服务编排
- `docker-compose.override.yml` 在本地联调模式下额外挂起 Postgres
- Redis 已纳入默认 Compose 编排，镜像固定为 `redis:7.0`
- Scheduler 目前仍建议单独进程启动，尚未并入默认 Compose 方案

---

## 2. 部署模式

项目当前建议分为两种 Docker 部署方式：

### 模式 A：本地联调模式

适用场景：

- 本地开发
- 接口联调
- Swagger 验证
- 本地数据库联调

特点：

- 使用 `docker compose up -d --build`
- 会自动应用 `docker-compose.override.yml`
- 会拉起：
  - `api`
  - `postgres`
  - `redis`

### 模式 B：远程数据库模式

适用场景：

- 连接公司或测试环境数据库
- 本地只跑 API 和 Redis 容器
- 不启本地 Postgres 容器

特点：

- 使用 `docker compose -f docker-compose.yml up -d --build`
- 会拉起：
  - `api`
  - `redis`
- 数据库通过配置连接远程 PostgreSQL

---

## 3. 前置条件

开始之前请确认本机已安装：

- Docker
- Docker Compose

建议确认版本：

```bash
docker --version
docker compose version
```

---

## 4. 项目文件说明

### 4.1 Dockerfile

作用：

- 构建 API 镜像
- 安装 Python 依赖
- 复制 `automage_agents / scripts / configs`

### 4.2 docker-compose.yml

作用：

- 定义基础 `api` 服务
- 定义 `redis` 服务
- API 默认连到 Compose 内部 Redis

### 4.3 docker-compose.override.yml

作用：

- 本地开发时自动生效
- 注入：
  - `AUTOMAGE_CONFIG_PATH=/app/configs/automage.docker.toml`
- 额外挂起本地 `postgres` 容器

### 4.4 configs/automage.docker.toml

作用：

- Docker 本地联调默认配置
- 默认使用容器内 `postgres` 主机名
- 默认启用 Redis 版限流 / 幂等

---

## 5. 本地联调模式部署

### 5.1 复制环境变量文件

```bash
cp .env.example .env
```

### 5.2 启动服务

```bash
docker compose up -d --build
```

### 5.3 启动后包含的容器

- `api`
- `postgres`
- `redis`

### 5.4 访问地址

- Swagger：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/healthz`

---

## 6. 远程数据库模式部署

### 6.1 复制环境变量文件

```bash
cp .env.example .env
```

### 6.2 修改数据库连接

将 `.env` 中以下配置改成目标环境：

```env
AUTOMAGE_DB_HOST=182.92.93.16
AUTOMAGE_DB_PORT=5432
AUTOMAGE_DB_NAME=automage
AUTOMAGE_DB_USER=automage
AUTOMAGE_DB_PASSWORD=automage
AUTOMAGE_DB_SSLMODE=prefer
```

### 6.3 启动服务

```bash
docker compose -f docker-compose.yml up -d --build
```

说明：

- 这条命令只使用基础 Compose 文件
- 不会自动拉起本地 Postgres 容器

---

## 7. Redis 版限流 / 幂等部署

### 7.1 当前实现状态

当前后端已经支持：

- `memory` 版限流 / 幂等
- `redis` 版限流 / 幂等

推荐口径：

- 简单本地调试可用 `memory`
- 容器化联调和多实例更建议用 `redis`

### 7.2 Compose 默认已包含 Redis

当前 `docker-compose.yml` 已经包含 Redis 服务，镜像固定为：

```text
redis:7.0
```

当前 Redis 服务特征：

- 服务名：`redis`
- 密码：`automage`
- 已开启 AOF 持久化
- 已挂载数据卷：`automage_redis_data`

### 7.3 Redis 连接验证

```bash
docker compose exec redis redis-cli -a automage ping
```

预期返回：

```text
PONG
```

### 7.4 API 默认 Redis 配置

当前 Compose 默认已经给 API 注入以下配置：

```env
AUTOMAGE_ABUSE_PROTECTION_ENABLED=true
AUTOMAGE_ABUSE_PROTECTION_BACKEND=redis
AUTOMAGE_RATE_LIMIT_WINDOW_SECONDS=60
AUTOMAGE_RATE_LIMIT_MAX_REQUESTS=60
AUTOMAGE_IDEMPOTENCY_TTL_SECONDS=300
AUTOMAGE_REDIS_URL=redis://:automage@redis:6379/0
AUTOMAGE_REDIS_KEY_PREFIX=automage
```

如果你的 API 不是容器内运行，而是宿主机本地运行，则可使用：

```env
AUTOMAGE_REDIS_URL=redis://:automage@127.0.0.1:6379/0
```

说明：

- 容器内访问 Compose 中的 Redis，直接使用服务名 `redis`
- 如果 Redis 不可用，当前实现会自动降级回内存版，不会直接让接口启动失败

---

## 8. Docker 配置切换规则

### 8.1 本地联调模式

- 使用 `docker-compose.override.yml`
- 自动切到 `configs/automage.docker.toml`
- 默认数据库主机为 `postgres`
- 默认 Redis 主机为 `redis`

### 8.2 远程数据库模式

- 只使用 `docker-compose.yml`
- 默认读取 `.env`
- 可通过 `AUTOMAGE_DB_*` 指向远程数据库

### 8.3 手动覆盖配置文件

如果你想显式指定配置文件，可以设置：

```env
AUTOMAGE_CONFIG_PATH=/app/configs/automage.docker.toml
```

---

## 9. 常用验证命令

### 9.1 查看容器状态

```bash
docker compose ps
```

### 9.2 查看 API 日志

```bash
docker compose logs -f api
```

### 9.3 查看 Redis 日志

```bash
docker compose logs -f redis
```

### 9.4 查看 Postgres 日志

```bash
docker compose logs -f postgres
```

### 9.5 检查数据库连通性

```bash
python scripts/check_postgres.py
```

### 9.6 检查接口是否存活

```bash
curl http://localhost:8000/healthz
```

---

## 10. 当前部署边界

当前 Docker 化方案已经能满足：

- API 容器启动
- 本地 Postgres 联调
- 远程 PostgreSQL 连接
- Redis 7.0 容器接入
- Redis 版限流 / 幂等接入

但以下内容当前仍未纳入默认容器编排：

1. Scheduler 独立容器
2. 完整生产环境多服务编排
3. 监控、告警、日志采集

---

## 11. 建议部署口径

如果用于当前阶段提交或群内同步，建议统一说明为：

1. 项目已具备基础 Docker 容器化部署能力。
2. 当前支持本地联调模式和远程数据库模式两种部署方式。
3. Redis 版限流 / 幂等已经支持，并且已纳入默认 Compose 编排。
4. 当前默认 Compose 以 API + Redis 为基础，本地联调模式下再额外挂起 Postgres，Scheduler 仍采用独立部署方式。
