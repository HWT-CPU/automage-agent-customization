# 全栈前端集成指南

本文档说明全栈前端团队如何集成和使用客制化团队提供的 Agent Runtime API。

## 概述

客制化团队提供了完整的 HTTP API 服务，前端可以通过标准的 REST API 调用 Agent Skills。

## API 基础信息

- **Base URL**: `http://localhost:8000`
- **认证方式**: Header 传递用户身份
- **数据格式**: JSON

## 认证 Headers

所有 API 请求需要携带以下 Headers：

```typescript
{
  "Content-Type": "application/json",
  "Authorization": "Bearer <token>",  // 可选，当前版本未强制
  "X-User-Id": "zhangsan",            // 必需
  "X-Role": "staff",                  // 必需：staff, manager, executive
  "X-Node-Id": "staff_agent_mvp_001"  // 必需
}
```

## API 端点

### 1. 运行 Agent Skill

**端点**: `POST /api/v1/agent/run`

**请求体**:

```typescript
interface AgentRunRequest {
  agent_type: 'staff' | 'manager' | 'executive'
  org_id: string
  department_id?: string
  user_id: string
  node_id: string
  run_date: string  // YYYY-MM-DD
  input: {
    skill_name: string
    skill_args: Record<string, any>
  }
  context?: Record<string, any>
}
```

**响应**:

```typescript
interface AgentRunResponse {
  ok: boolean
  agent_type: string
  node_id: string
  output_schema_id: string
  output: Record<string, any>
  warnings: string[]
  trace_id: string
  fallback: boolean
}
```

**示例**:

```typescript
// 提交员工日报
const response = await fetch('http://localhost:8000/api/v1/agent/run', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-User-Id': 'zhangsan',
    'X-Role': 'staff',
    'X-Node-Id': 'staff_agent_mvp_001',
  },
  body: JSON.stringify({
    agent_type: 'staff',
    org_id: 'org_automage_mvp',
    user_id: 'zhangsan',
    node_id: 'staff_agent_mvp_001',
    run_date: '2026-05-13',
    input: {
      skill_name: 'post_daily_report',
      skill_args: {
        timestamp: '2026-05-13T10:00:00+08:00',
        work_progress: '完成了客户跟进',
        issues_faced: '报价周期不明确',
        solution_attempt: '已联系产品经理确认',
        need_support: false,
        next_day_plan: '继续推进合同签订',
        resource_usage: {},
      },
    },
  }),
})

const result: AgentRunResponse = await response.json()
```

### 2. 查询可用 Skills

**端点**: `GET /api/v1/agent/skills?agent_type={type}`

**参数**:
- `agent_type`: staff | manager | executive

**响应**:

```typescript
interface SkillListResponse {
  agent_type: string
  skills: SkillInfo[]
}

interface SkillInfo {
  name: string
  description: string
  category: string
}
```

**示例**:

```typescript
const response = await fetch(
  'http://localhost:8000/api/v1/agent/skills?agent_type=staff',
  {
    headers: {
      'X-User-Id': 'zhangsan',
      'X-Role': 'staff',
    },
  }
)

const result: SkillListResponse = await response.json()
console.log(result.skills)
```

### 3. 健康检查

**端点**: `GET /api/v1/agent/health`

**响应**:

```typescript
interface HealthCheckResponse {
  status: string
  service: string
  timestamp: string
  hermes_enabled: boolean
  available_skills: number
}
```

## TypeScript 集成示例

### 1. 创建 Agent Client

```typescript
// src/lib/agentClient.ts

export interface AgentRunRequest {
  agent_type: 'staff' | 'manager' | 'executive'
  org_id: string
  department_id?: string
  user_id: string
  node_id: string
  run_date: string
  input: {
    skill_name: string
    skill_args: Record<string, any>
  }
  context?: Record<string, any>
}

export interface AgentRunResponse {
  ok: boolean
  agent_type: string
  node_id: string
  output_schema_id: string
  output: Record<string, any>
  warnings: string[]
  trace_id: string
  fallback: boolean
}

export class AgentClient {
  constructor(
    private baseUrl: string = 'http://localhost:8000',
    private identity: {
      user_id: string
      role: string
      node_id: string
    }
  ) {}

  async runSkill(request: AgentRunRequest): Promise<AgentRunResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/agent/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': this.identity.user_id,
        'X-Role': this.identity.role,
        'X-Node-Id': this.identity.node_id,
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      throw new Error(`Agent API error: ${response.status}`)
    }

    return response.json()
  }

  async listSkills(agentType: string) {
    const response = await fetch(
      `${this.baseUrl}/api/v1/agent/skills?agent_type=${agentType}`,
      {
        headers: {
          'X-User-Id': this.identity.user_id,
          'X-Role': this.identity.role,
        },
      }
    )

    if (!response.ok) {
      throw new Error(`Agent API error: ${response.status}`)
    }

    return response.json()
  }

  async healthCheck() {
    const response = await fetch(`${this.baseUrl}/api/v1/agent/health`)
    return response.json()
  }
}
```

### 2. 在组件中使用

```typescript
// src/components/staff/DailyReportForm.tsx

import { useState } from 'react'
import { AgentClient } from '@/lib/agentClient'
import { useIdentityStore } from '@/store/useIdentityStore'

export function DailyReportForm() {
  const identity = useIdentityStore((state) => state.identity)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (formData: any) => {
    setLoading(true)
    try {
      const client = new AgentClient('http://localhost:8000', {
        user_id: identity.user_id,
        role: identity.role,
        node_id: identity.node_id,
      })

      const response = await client.runSkill({
        agent_type: 'staff',
        org_id: identity.org_id,
        department_id: identity.department_id,
        user_id: identity.user_id,
        node_id: identity.node_id,
        run_date: new Date().toISOString().split('T')[0],
        input: {
          skill_name: 'post_daily_report',
          skill_args: {
            timestamp: new Date().toISOString(),
            work_progress: formData.work_progress,
            issues_faced: formData.issues_faced,
            solution_attempt: formData.solution_attempt,
            need_support: formData.need_support,
            next_day_plan: formData.next_day_plan,
            resource_usage: {},
          },
        },
      })

      if (response.ok) {
        alert('日报提交成功！')
        console.log('返回数据:', response.output)
      } else {
        alert(`提交失败: ${response.warnings.join(', ')}`)
      }
    } catch (error) {
      console.error('提交日报失败:', error)
      alert('网络错误，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* 表单字段 */}
      <button type="submit" disabled={loading}>
        {loading ? '提交中...' : '提交日报'}
      </button>
    </form>
  )
}
```

### 3. 适配现有的 AgentAdapter 接口

如果你们已经有 `AgentAdapter` 接口定义，可以创建一个适配器：

```typescript
// src/agent/customizationAgentClient.ts

import type { AgentAdapter, AgentRunRequest, AgentRunResponse } from './agentAdapter'

export class CustomizationAgentClient implements AgentAdapter {
  constructor(private baseUrl: string = 'http://localhost:8000') {}

  async run(req: AgentRunRequest): Promise<AgentRunResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/agent/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': req.user_id,
        'X-Role': req.agent_type,
        'X-Node-Id': req.node_id,
      },
      body: JSON.stringify(req),
    })

    if (!response.ok) {
      // 降级到 Mock
      return {
        ok: false,
        agent_type: req.agent_type,
        node_id: req.node_id,
        output_schema_id: `schema_v1_${req.agent_type}`,
        output: {},
        warnings: [`API error: ${response.status}`],
        trace_id: `fallback-${Date.now()}`,
        fallback: true,
      }
    }

    return response.json()
  }
}
```

然后在 `agentAdapterFactory.ts` 中注册：

```typescript
// src/agent/agentAdapterFactory.ts

import { CustomizationAgentClient } from './customizationAgentClient'
import { StaffAgentClient } from './staffAgentClient'

export function createAgentAdapter(agentType: string, useReal: boolean) {
  if (useReal) {
    return new CustomizationAgentClient('http://localhost:8000')
  }
  
  // 降级到 Mock
  return new StaffAgentClient()
}
```

## 常用 Skills 参数说明

### Staff Skills

#### 1. post_daily_report (提交日报)

```typescript
{
  skill_name: 'post_daily_report',
  skill_args: {
    timestamp: string          // ISO 8601 格式
    work_progress: string      // 今日完成的工作
    issues_faced: string       // 遇到的问题
    solution_attempt: string   // 尝试的解决方案
    need_support: boolean      // 是否需要支持
    next_day_plan: string      // 明日计划
    resource_usage: object     // 资源使用情况（可选）
  }
}
```

#### 2. fetch_my_tasks (查询任务)

```typescript
{
  skill_name: 'fetch_my_tasks',
  skill_args: {
    status?: 'pending' | 'in_progress' | 'completed'  // 可选
  }
}
```

#### 3. update_my_task (更新任务)

```typescript
{
  skill_name: 'update_my_task',
  skill_args: {
    task_id: string
    status?: 'pending' | 'in_progress' | 'completed'
    title?: string
    description?: string
    task_payload?: object
  }
}
```

### Manager Skills

#### 1. generate_manager_report (生成汇总)

```typescript
{
  skill_name: 'generate_manager_report',
  skill_args: {
    dept_id: string
    overall_health: 'green' | 'yellow' | 'red'
    aggregated_summary: string
    top_3_risks: Array<{
      risk_title: string
      description: string
      severity: 'low' | 'medium' | 'high'
      suggested_action: string
    }>
    workforce_efficiency: number  // 0.0 - 1.0
    pending_approvals: number
  }
}
```

#### 2. delegate_task (分配任务)

```typescript
{
  skill_name: 'delegate_task',
  skill_args: {
    assignee_user_id: string
    task_title: string
    task_description: string
    priority: 'low' | 'medium' | 'high'
  }
}
```

### Executive Skills

#### 1. dream_decision_engine (生成决策方案)

```typescript
{
  skill_name: 'dream_decision_engine',
  skill_args: {
    summary_id: string  // Manager 汇总 ID
  }
}
```

#### 2. commit_decision (提交决策)

```typescript
{
  skill_name: 'commit_decision',
  skill_args: {
    summary_id: string
    selected_option_id: 'A' | 'B'
    task_candidates: Array<{
      assignee_user_id: string
      task_title: string
      task_description: string
      priority: 'low' | 'medium' | 'high'
      status: 'pending'
    }>
  }
}
```

## 错误处理

### HTTP 状态码

| 状态码 | 含义 | 处理建议 |
|--------|------|---------|
| 200 | 成功 | 正常处理响应 |
| 400 | 请求参数错误 | 检查请求体格式和必填字段 |
| 403 | 权限不足 | 检查用户角色和权限 |
| 503 | 服务不可用 | 降级到 Mock 或提示用户稍后重试 |

### 响应错误处理

```typescript
async function callAgentSkill(request: AgentRunRequest) {
  try {
    const response = await fetch('http://localhost:8000/api/v1/agent/run', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': request.user_id,
        'X-Role': request.agent_type,
        'X-Node-Id': request.node_id,
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      // HTTP 错误
      if (response.status === 503) {
        console.warn('Agent Runtime 服务不可用，降级到 Mock')
        return useMockFallback(request)
      }
      
      throw new Error(`HTTP ${response.status}: ${await response.text()}`)
    }

    const result: AgentRunResponse = await response.json()

    if (!result.ok) {
      // 业务逻辑错误
      console.error('Skill 执行失败:', result.warnings)
      throw new Error(result.warnings.join(', '))
    }

    return result
  } catch (error) {
    console.error('调用 Agent API 失败:', error)
    // 降级到 Mock
    return useMockFallback(request)
  }
}
```

## 环境配置

### 开发环境

```typescript
// src/config/env.ts

export const appEnv = {
  apiBase: import.meta.env.VITE_API_BASE || 'http://localhost:8000',
  agentApiBase: import.meta.env.VITE_AGENT_API_BASE || 'http://localhost:8000',
  useMockAgent: import.meta.env.VITE_USE_MOCK_AGENT === 'true',
}
```

### .env 文件

```bash
# .env.development
VITE_AGENT_API_BASE=http://localhost:8000
VITE_USE_MOCK_AGENT=false

# .env.production
VITE_AGENT_API_BASE=https://api.automage.com
VITE_USE_MOCK_AGENT=false
```

## 测试

### 单元测试

```typescript
// src/lib/__tests__/agentClient.test.ts

import { describe, it, expect, vi } from 'vitest'
import { AgentClient } from '../agentClient'

describe('AgentClient', () => {
  it('should call runSkill successfully', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        ok: true,
        agent_type: 'staff',
        node_id: 'staff_agent_mvp_001',
        output_schema_id: 'schema_v1_staff',
        output: { record_id: 'wr_123' },
        warnings: [],
        trace_id: 'trace-123',
        fallback: false,
      }),
    })

    const client = new AgentClient('http://localhost:8000', {
      user_id: 'zhangsan',
      role: 'staff',
      node_id: 'staff_agent_mvp_001',
    })

    const result = await client.runSkill({
      agent_type: 'staff',
      org_id: 'org_automage_mvp',
      user_id: 'zhangsan',
      node_id: 'staff_agent_mvp_001',
      run_date: '2026-05-13',
      input: {
        skill_name: 'fetch_my_tasks',
        skill_args: {},
      },
    })

    expect(result.ok).toBe(true)
    expect(result.output).toHaveProperty('record_id')
  })
})
```

## 联系方式

如有问题，请联系客制化团队：

- 技术负责人：[姓名]
- 邮箱：[邮箱]
- 文档仓库：`客制化/docs/`

## 更新日志

- **2026-05-13**: 初始版本，提供 Agent Runtime HTTP API
