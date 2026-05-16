# 权限 + Cron + 防滥用实现说明

## 1. 文档目的

本文档用于说明本轮新增的三项后端工程能力：

1. 权限与校验增强
2. Cron 调度器与真实扫描任务
3. 防滥用中间件

适用场景：

- 里程碑汇报
- 代码提交说明
- 后端交接
- 后续二次开发

---

## 2. 权限与校验实现说明

### 2.1 实现目标

本轮权限改造的目标是把原先“能调通接口”提升到“接口级 + 资源级可控”。

核心原则：

- 默认拒绝
- 显式放行
- 角色、资源、动作、归属一起判断

### 2.2 当前权限模型

当前统一角色模型为：

- `staff`
- `manager`
- `executive`

当前口径：

- `staff` 只能提交和读取本人允许范围内的数据
- `manager` 只能访问本人部门或本人管理范围内的数据
- `executive` 保留全局视图

### 2.3 已落地的校验点

已补齐的校验包括：

- 请求头身份校验
- `payload.identity` 与请求头一致性校验
- 创建类接口的归属字段校验
- 资源归属校验
- 关键枚举字段校验
- 访问拒绝审计/日志记录

已覆盖场景包括：

- Staff 日报详情读取
- Manager 汇总提交
- 任务创建
- 任务更新
- 审计日志查询

### 2.4 代码位置

- 鉴权入口：`automage_agents/server/auth.py`
- RBAC 策略层：`automage_agents/server/rbac.py`
- 接口接线：`automage_agents/server/app.py`
- Staff 详情接口：`automage_agents/server/daily_report_api.py`
- 请求模型：`automage_agents/server/schemas.py`

### 2.5 当前边界

本轮已经做成统一 RBAC 策略层，但边界需要明确：

- 当前是代码内固定策略
- 还不是数据库驱动的动态权限系统
- 还没有独立权限后台

---

## 3. Cron 实现说明

### 3.1 实现目标

本轮 Cron 的目标不是直接做复杂业务自动化，而是先把“可独立运行、可接真实扫描任务”的调度框架搭起来。

### 3.2 当前架构

已新增独立 Scheduler 模块，和 API 进程解耦：

- `automage_agents/scheduler/runtime.py`
- `automage_agents/scheduler/jobs.py`
- `automage_agents/scheduler/services.py`
- `scripts/run_scheduler.py`

当前支持：

- 独立启动
- 任务注册
- 配置开关
- 数据库会话注入

启动方式：

```powershell
python scripts/run_scheduler.py
```

### 3.3 当前已接入的真实任务

本轮已接入两个真实扫描任务：

1. `staff_daily_reminder_job`
   - 扫描当天未提交日报的员工
2. `manager_summary_reminder_job`
   - 扫描当天未生成汇总的经理
   - 同时扫描当前未完成任务

### 3.4 当前任务行为

当前任务会：

- 真实读取数据库
- 扫描业务数据
- 输出结果日志

当前任务不会：

- 自动发送飞书/短信
- 自动补写正式业务数据
- 自动创建正式汇总
- 自动提交正式决策

### 3.5 配置项

当前涉及配置包括：

- `scheduler_enabled`
- `scheduler_timezone`
- `scheduler_jobs`
- `scheduler_task_record_limit`

配置位置：

- `automage_agents/config/settings.py`
- `automage_agents/config/loader.py`
- `configs/automage.example.toml`

---

## 4. 防滥用实现说明

### 4.1 实现目标

本轮防滥用目标是先做到“联调环境可控”，不追求一次到位的分布式版本。

### 4.2 当前能力

当前已补齐：

- 基础限流
- 关键写接口幂等保护
- 重复写拦截
- 失败返回统一错误码

已保留原有：

- `RequestTrackingMiddleware`

新增：

- `AbuseProtectionMiddleware`

代码位置：

- `automage_agents/server/middleware.py`

### 4.3 限流策略

当前限流维度：

- 优先 `X-User-Id`
- 无身份时退化到客户端 IP

当前保护范围：

- `POST /api/v1/report/staff`
- `POST /api/v1/report/manager`
- `POST /api/v1/decision/commit`
- `POST /api/v1/tasks`
- `PATCH /api/v1/tasks/{task_id}`

### 4.4 幂等策略

当前支持请求头：

```http
Idempotency-Key: <unique-key>
```

当前规则：

- 相同用户 + 相同路径 + 相同幂等键
- 在 TTL 内重复提交时拦截重复写入

当前返回约定：

- 限流：`429`
- 重复提交：`409`

### 4.5 配置项

- `abuse_protection_enabled`
- `rate_limit_window_seconds`
- `rate_limit_max_requests`
- `idempotency_ttl_seconds`
- `write_protected_paths`

配置位置：

- `automage_agents/config/settings.py`
- `automage_agents/config/loader.py`
- `configs/automage.example.toml`

### 4.6 当前边界

当前版本边界需要明确：

- 仍是单进程内存版
- 适合本地验证和联调环境
- 还不适合多实例共享限流与幂等状态
- 后续应升级为 Redis 版

---

## 5. 本轮测试覆盖

本轮相关验证包括：

- `tests/test_daily_report_api.py`
- `tests/test_manager_decision_task_flow.py`
- `tests/test_rbac_policy.py`
- `tests/test_scheduler_jobs.py`

验证命令：

```powershell
python -m compileall automage_agents tests
python -m unittest tests.test_daily_report_api tests.test_manager_decision_task_flow tests.test_staff_daily_report_persistence tests.test_staff_daily_report_parser tests.test_rbac_policy tests.test_scheduler_jobs
```

验证结果：

- 共 `35` 个测试通过

---

## 6. 当前结论

本轮三项工程能力已经达到以下状态：

1. 权限已从简单角色放行升级为统一 RBAC 策略校验
2. Cron 已从空框架升级为真实业务扫描任务
3. 防滥用已具备基础限流和幂等保护

当前版本适合：

- 继续联调
- 阶段提交
- 后续继续做 Redis、通知渠道、动态权限的扩展
