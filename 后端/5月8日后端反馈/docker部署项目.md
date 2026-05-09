# Docker 部署指南

本文用于说明如何在本地或团队环境中用 Docker 启动 AutoMage 后端。

## 一、部署目标

本项目支持两种部署方式：

1. 本地 Docker 自部署
2. 远程数据库 / 生产模式部署

团队成员只需要拉取代码并准备 `.env` 文件，即可直接启动。

## 二、前置条件

请先确认本机已安装：

- Docker
- Docker Compose

## 三、获取代码

```powershell
git pull origin main
```

如果是第一次拉取：

```powershell
git clone https://github.com/HWT-CPU/automage-agent-customization
```

## 四、本地自部署

适合每个人在自己的电脑上直接测试和启动。

### 1. 复制环境变量文件

```powershell
copy .env.example .env
```

### 2. 启动服务

```powershell
docker compose up -d --build
```

### 3. 访问地址

- Swagger：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/healthz`

本地模式会同时启动：

- API 容器
- Postgres 容器

## 五、远程数据库 / 生产模式

适合连接公司已有远程数据库，不启用本地 Postgres 容器。

### 1. 复制环境变量文件

```powershell
copy .env.example .env
```

### 2. 按需修改数据库配置

如果需要连接远程数据库，只需修改 `.env` 中的 `AUTOMAGE_DB_*` 配置。

### 3. 启动服务

```powershell
docker compose -f docker-compose.yml up -d --build
```

## 六、配置说明

### 1. 本地模式

- 使用 `docker-compose.override.yml`
- 自动切换到 `configs/automage.docker.toml`
- 默认起本地 Postgres 容器

### 2. 远程模式

- 只使用 `docker-compose.yml`
- 默认读取 `configs/automage.local.toml`
- 通过 `.env` 里的 `AUTOMAGE_DB_*` 连接远程数据库

### 3. 配置覆盖

如果要手动指定配置文件，可以设置：

```powershell
AUTOMAGE_CONFIG_PATH=...
```

## 七、常用排查

### 1. 先检查数据库连接

```powershell
python scripts\check_postgres.py
```

### 2. 查看容器状态

```powershell
docker compose ps
```

### 3. 查看日志

```powershell
docker compose logs -f api
```

## 八、补充说明

- 这套方案的目标是让团队成员在各自电脑上也能稳定启动。
- 如果后续有公司服务器资源，可以直接沿用同一套镜像和配置迁移部署。
