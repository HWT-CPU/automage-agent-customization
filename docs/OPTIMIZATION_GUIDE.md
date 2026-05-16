# 客制化代码优化指南

## 📊 已实现的优化

### 1. **API 中间件层**（新增）

**文件**: `automage_agents/api/middleware.py`

**优化内容**:
- ✅ **请求日志中间件**: 自动记录所有 API 请求，包含请求 ID、耗时、状态码
- ✅ **错误处理中间件**: 统一捕获和格式化异常，返回标准错误响应
- ✅ **性能监控中间件**: 自动检测慢请求（默认阈值 1000ms）

**优点**:
- 统一的日志格式，便于追踪和调试
- 标准化的错误响应，前端更容易处理
- 自动识别性能瓶颈

**使用方法**:
```python
# 已在 server/app.py 中自动启用
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(PerformanceMonitoringMiddleware, slow_request_threshold_ms=1000.0)
app.add_middleware(RequestLoggingMiddleware)
```

---

### 2. **缓存层**（新增）

**文件**: `automage_agents/api/cache.py`

**优化内容**:
- ✅ **Skill 结果缓存**: 自动缓存只读 Skill 的结果（如 `fetch_my_tasks`）
- ✅ **简单内存缓存**: 轻量级的 TTL 缓存实现
- ✅ **缓存装饰器**: 方便为任何函数添加缓存

**优点**:
- 减少重复的数据库查询
- 提升只读操作的响应速度
- 降低后端 API 压力

**可缓存的 Skills**:
- `fetch_my_tasks` - 查询任务
- `read_staff_daily_report` - 读取日报
- `search_feishu_knowledge` - 搜索知识库
- `analyze_team_reports` - 分析团队日报

**使用方法**:
```python
from automage_agents.api.cache import skill_result_cache

# 获取缓存
result = skill_result_cache.get(skill_name, actor_user_id, payload)

# 设置缓存
skill_result_cache.set(skill_name, actor_user_id, payload, result, ttl_seconds=60)

# 清空缓存
skill_result_cache.clear()
```

---

### 3. **带缓存的 Hermes Client**（新增）

**文件**: `automage_agents/integrations/hermes/cached_client.py`

**优化内容**:
- ✅ **自动缓存**: 透明地缓存只读 Skill 结果
- ✅ **性能统计**: 记录缓存命中率、平均响应时间
- ✅ **智能失效**: 支持按 Skill 和用户失效缓存

**优点**:
- 无需修改现有代码，直接替换 `LocalHermesClient`
- 自动优化性能
- 提供详细的性能指标

**使用方法**:
```python
from automage_agents.integrations.hermes.cached_client import CachedHermesClient

# 创建带缓存的客户端
cached_client = CachedHermesClient(
    staff_context,
    manager_context,
    executive_context,
    enable_cache=True,
    cache_ttl_seconds=60,
)

# 使用方式与 LocalHermesClient 完全相同
response = cached_client.invoke_skill(request)

# 查看性能统计
stats = cached_client.get_stats()
print(f"缓存命中率: {stats['cache_hit_rate']:.2%}")
print(f"平均响应时间: {stats['avg_duration_ms']:.2f}ms")
```

---

### 4. **配置和数据验证**（新增）

**文件**: `automage_agents/utils/validation.py`

**优化内容**:
- ✅ **配置文件验证**: 检查配置文件是否存在和格式正确
- ✅ **Skill 参数验证**: 验证 Skill 必需参数是否完整
- ✅ **身份认证验证**: 验证 HTTP Headers 是否包含必需字段
- ✅ **请求数据验证**: 验证 AgentRunRequest 格式

**优点**:
- 提前发现配置错误
- 减少运行时异常
- 提供清晰的错误提示

**使用方法**:
```python
from automage_agents.utils.validation import (
    validate_config_file,
    validate_skill_payload,
    validate_identity_headers,
    validate_agent_run_request,
)

# 验证配置文件
result = validate_config_file("configs/hermes.example.toml")
if not result["valid"]:
    print(f"配置文件无效: {result['error']}")

# 验证 Skill 参数
result = validate_skill_payload("post_daily_report", payload)
if not result["valid"]:
    print(f"缺少参数: {result['missing_params']}")

# 验证请求数据
result = validate_agent_run_request(request_data)
if not result["valid"]:
    print(f"请求无效: {result['error']}")
```

---

## 🚀 性能提升预期

### 缓存优化

| 场景 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 查询任务（重复） | ~200ms | ~5ms | **40x** |
| 读取日报（重复） | ~150ms | ~5ms | **30x** |
| 搜索知识库（重复） | ~300ms | ~5ms | **60x** |

### 中间件优化

| 功能 | 优化前 | 优化后 |
|------|--------|--------|
| 错误追踪 | 手动查日志 | 自动记录请求 ID |
| 性能监控 | 无 | 自动检测慢请求 |
| 错误格式 | 不统一 | 标准化 JSON 格式 |

---

## 📋 建议的进一步优化

### 1. **数据库连接池优化**

**当前状态**: 使用默认连接池配置

**优化建议**:
```python
# automage_agents/db/connection.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    connection_string,
    poolclass=QueuePool,
    pool_size=20,          # 连接池大小
    max_overflow=10,       # 最大溢出连接数
    pool_timeout=30,       # 获取连接超时时间
    pool_recycle=3600,     # 连接回收时间（1小时）
    pool_pre_ping=True,    # 连接前检查可用性
)
```

**预期提升**: 减少数据库连接开销，提升并发性能

---

### 2. **异步 Skill 执行**

**当前状态**: 同步执行 Skills

**优化建议**:
```python
# 使用 asyncio 并发执行多个 Skill
import asyncio

async def execute_skills_concurrently(requests: list[HermesInvokeRequest]):
    tasks = [execute_skill_async(req) for req in requests]
    return await asyncio.gather(*tasks)
```

**适用场景**:
- Manager 分析多个员工日报
- Executive 生成多个决策方案
- 批量查询任务

**预期提升**: 并发执行可提升 3-5x 性能

---

### 3. **Redis 缓存替代内存缓存**

**当前状态**: 使用内存缓存（单机）

**优化建议**:
```python
# automage_agents/api/redis_cache.py
import redis

class RedisCache:
    def __init__(self, redis_url: str):
        self.client = redis.from_url(redis_url)
    
    def get(self, key: str) -> Any:
        value = self.client.get(key)
        return json.loads(value) if value else None
    
    def set(self, key: str, value: Any, ttl_seconds: int):
        self.client.setex(key, ttl_seconds, json.dumps(value))
```

**优点**:
- 支持分布式部署
- 缓存持久化
- 更大的缓存容量

**预期提升**: 支持多实例部署，缓存共享

---

### 4. **批量 API 调用**

**当前状态**: 单个请求单个调用

**优化建议**:
```python
# 新增批量端点
@router.post("/api/v1/agent/batch-run")
async def batch_run_agents(requests: list[AgentRunRequest]):
    results = []
    for req in requests:
        result = await run_agent(req)
        results.append(result)
    return {"results": results}
```

**适用场景**:
- 前端批量查询多个用户的任务
- Manager 批量分析多个部门

**预期提升**: 减少网络往返，提升 2-3x 性能

---

### 5. **Skill 执行超时控制**

**当前状态**: 无超时控制

**优化建议**:
```python
import asyncio

async def execute_skill_with_timeout(request: HermesInvokeRequest, timeout_seconds: int = 30):
    try:
        return await asyncio.wait_for(
            execute_skill_async(request),
            timeout=timeout_seconds
        )
    except asyncio.TimeoutError:
        return HermesInvokeResponse(
            ok=False,
            skill_name=request.skill_name,
            actor_user_id=request.actor_user_id,
            result=SkillResult(
                ok=False,
                message=f"Skill execution timeout after {timeout_seconds}s",
                error_code="timeout",
            ),
            trace=request.trace,
        )
```

**优点**:
- 防止慢 Skill 阻塞整个系统
- 提升系统稳定性

---

### 6. **结构化日志**

**当前状态**: 使用 `print()` 输出日志

**优化建议**:
```python
import structlog

logger = structlog.get_logger()

# 结构化日志
logger.info(
    "skill_executed",
    skill_name=skill_name,
    actor_user_id=actor_user_id,
    duration_ms=duration_ms,
    success=response.ok,
)
```

**优点**:
- 便于日志分析和查询
- 支持 ELK、Splunk 等日志系统
- 更好的可观测性

---

### 7. **健康检查增强**

**当前状态**: 简单的状态检查

**优化建议**:
```python
@router.get("/api/v1/agent/health/detailed")
async def detailed_health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "hermes_runtime": check_hermes_health(),
            "database": check_database_health(),
            "redis": check_redis_health(),
            "skills": check_skills_health(),
        },
        "metrics": {
            "total_requests": get_total_requests(),
            "cache_hit_rate": get_cache_hit_rate(),
            "avg_response_time_ms": get_avg_response_time(),
        },
    }
```

**优点**:
- 更详细的健康状态
- 便于监控和告警
- 快速定位问题

---

## 🔧 如何启用优化

### 1. 启用缓存（推荐）

在 `server/app.py` 中使用 `CachedHermesClient`:

```python
from automage_agents.integrations.hermes.cached_client import CachedHermesClient

# 在 lifespan 中
runtime = HermesOpenClawRuntime.from_settings(settings)

# 使用带缓存的客户端
cached_client = CachedHermesClient(
    runtime.staff_context,
    runtime.manager_context,
    runtime.executive_context,
    enable_cache=True,
    cache_ttl_seconds=60,
)

initialize_agent_runtime(cached_client)
```

### 2. 启用中间件（已自动启用）

中间件已在 `server/app.py` 中自动启用，无需额外配置。

### 3. 启用参数验证

在 `agent_runtime.py` 中添加验证:

```python
from automage_agents.utils.validation import validate_agent_run_request

@router.post("/run")
async def run_agent(request: AgentRunRequest, ...):
    # 验证请求
    validation_result = validate_agent_run_request(request.dict())
    if not validation_result["valid"]:
        raise HTTPException(status_code=400, detail=validation_result["error"])
    
    # 继续处理...
```

---

## 📊 性能监控

### 查看缓存统计

```python
# 在 agent_runtime.py 中添加端点
@router.get("/stats/cache")
async def get_cache_stats():
    if isinstance(_runtime_state.hermes_client, CachedHermesClient):
        return _runtime_state.hermes_client.get_stats()
    return {"error": "Cache not enabled"}
```

### 查看慢请求日志

慢请求会自动输出到控制台:

```
⚠️  SLOW REQUEST: POST /api/v1/agent/run took 1234.56ms (threshold: 1000ms)
```

---

## ✅ 优化清单

- [x] API 中间件（日志、错误处理、性能监控）
- [x] Skill 结果缓存
- [x] 带缓存的 Hermes Client
- [x] 配置和数据验证工具
- [ ] 数据库连接池优化
- [ ] 异步 Skill 执行
- [ ] Redis 缓存
- [ ] 批量 API 调用
- [ ] Skill 执行超时控制
- [ ] 结构化日志
- [ ] 健康检查增强

---

## 📞 反馈

如有优化建议或遇到问题，请联系客制化团队。

**文档更新日期**: 2026-05-13
