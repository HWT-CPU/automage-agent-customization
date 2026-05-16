import { appEnv } from '../config/env'
import type { IdentityProfile } from '../config/identities'
import { unwrapApiBody } from './apiEnvelope'
import { buildHeaders } from './requestHeaders'
import { useRuntimeStore } from '../store/useRuntimeStore'
import { mockTasks } from '../data/mockTasks'

export interface ApiResult<T = unknown> {
  ok: boolean
  status: number
  data: T
  raw: unknown
  request_id: string
  idempotency_key: string
  fallback: boolean
  blocked?: boolean
  msg?: string
}

type HttpMethod = 'GET' | 'POST' | 'PATCH'

function compactQuery(params?: Record<string, string | undefined>): string {
  if (!params) return ''
  const q = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== '') q.set(k, v)
  }
  const s = q.toString()
  return s ? `?${s}` : ''
}

export class AutomageApiClient {
  private mockInnerData(path: string, method: HttpMethod): unknown {
    if (path.startsWith('/healthz')) return { status: 'ok', service: 'automage-api' }
    if (path.includes('/api/v1/tasks') && method === 'GET') return { tasks: mockTasks }
    if (path.includes('/api/v1/report/staff') && method === 'GET')
      return {
        reports: [],
      }
    if (path.includes('/api/v1/report/manager') && method === 'GET')
      return {
        reports: [],
      }
    if (path.includes('/api/v1/report/staff') && method === 'POST')
      return {
        record: {
          work_record_public_id: 'wr_demo_placeholder',
          staff_report_id: 0,
        },
      }
    if (path.includes('/api/v1/report/manager') && method === 'POST')
      return {
        record: {
          summary_public_id: 'SUM-DEMO-PLACEHOLDER',
        },
      }
    if (path.includes('/internal/dream/run'))
      return {
        summary_public_id: 'SUM-DEMO-PLACEHOLDER',
        contract_status: 'pending_dream_confirmation',
        manager_summary: { title: 'Demo summary', content: 'Demo', summary_date: '2026-05-09' },
        decision_options: [
          {
            option_id: 'A',
            title: '保守方案（演示）',
            summary: '优先控制风险',
            task_candidates: [
              {
                task_id: 'TSK-DEMO-A',
                title: 'Demo task A',
                description: '演示任务',
                assignee_user_id: 'zhangsan',
                status: 'pending',
                priority: 'high',
                source_summary_id: 'SUM-DEMO-PLACEHOLDER',
              },
            ],
          },
          {
            option_id: 'B',
            title: '进取方案（演示）',
            summary: '加快闭环',
            task_candidates: [
              {
                task_id: 'TSK-DEMO-B',
                title: 'Demo task B',
                description: '演示任务',
                assignee_user_id: 'zhangsan',
                status: 'pending',
                priority: 'medium',
                source_summary_id: 'SUM-DEMO-PLACEHOLDER',
              },
            ],
          },
        ],
      }
    if (path.includes('/decision/commit'))
      return {
        decision: {},
        tasks: mockTasks,
        task_ids: mockTasks.map((t) => t.task_id),
      }
    if (path.includes('/api/v1/tasks') && method === 'POST') return { tasks: mockTasks.slice(0, 1) }
    if (path.includes('/api/v1/incidents')) return { incidents: [] }
    return { ok: true }
  }

  private async request<T>(
    method: HttpMethod,
    path: string,
    identity: IdentityProfile,
    options: {
      payload?: unknown
      write?: boolean
      query?: Record<string, string | undefined>
    } = {},
  ): Promise<ApiResult<T>> {
    const { demoMode, enableRealWrite, pushApiLog, setLastPayloads } = useRuntimeStore.getState()
    const write = options.write ?? false
    const { headers, requestId, idempotencyKey } = buildHeaders(identity, method !== 'GET')
    const start = performance.now()
    const urlPath = `${path}${compactQuery(options.query)}`

    if (demoMode) {
      const inner = this.fixMock(path, method) as T
      const raw = { code: 200, data: inner, msg: 'demo_mode' }
      pushApiLog({
        timestamp: new Date().toISOString(),
        method,
        path: urlPath,
        status: 200,
        role: identity.role,
        requestId,
        idempotencyKey,
        durationMs: Math.round(performance.now() - start),
        fallback: true,
      })
      setLastPayloads(options.payload, raw)
      return {
        ok: true,
        status: 200,
        data: inner,
        raw,
        request_id: requestId,
        idempotency_key: idempotencyKey,
        fallback: true,
        msg: 'demo_mode',
      }
    }

    if (!demoMode && write && !enableRealWrite) {
      const raw = {
        code: 403,
        msg: 'Real write disabled. Turn on “Real Write ON” in the top bar before calling write APIs.',
        data: null,
      }
      pushApiLog({
        timestamp: new Date().toISOString(),
        method,
        path: urlPath,
        status: 403,
        role: identity.role,
        requestId,
        idempotencyKey,
        durationMs: Math.round(performance.now() - start),
        fallback: false,
        errorMessage: raw.msg,
      })
      setLastPayloads(options.payload, raw)
      return {
        ok: false,
        status: 403,
        data: null as T,
        raw,
        request_id: requestId,
        idempotency_key: idempotencyKey,
        fallback: false,
        blocked: true,
        msg: raw.msg,
      }
    }

    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 30_000)

    try {
      const response = await fetch(`${appEnv.apiBase}${urlPath}`, {
        method,
        headers,
        body: options.payload !== undefined ? JSON.stringify(options.payload) : undefined,
        signal: controller.signal,
      })
      let json: unknown = {}
      const text = await response.text()
      try {
        json = text ? JSON.parse(text) : {}
      } catch {
        json = { parse_error: text }
      }
      const { data: inner, msg, code, isEnvelope } = unwrapApiBody(json)
      pushApiLog({
        timestamp: new Date().toISOString(),
        method,
        path: urlPath,
        status: response.status,
        role: identity.role,
        requestId,
        idempotencyKey,
        durationMs: Math.round(performance.now() - start),
        fallback: false,
        errorMessage: response.ok ? undefined : (msg as string | undefined) ?? `HTTP ${response.status}`,
      })
      setLastPayloads(options.payload, json)
      const businessOk = response.ok && (!isEnvelope || code === 200)
      return {
        ok: businessOk,
        status: response.status,
        data: inner as T,
        raw: json,
        request_id: requestId,
        idempotency_key: idempotencyKey,
        fallback: false,
        msg,
      }
    } catch (error) {
      pushApiLog({
        timestamp: new Date().toISOString(),
        method,
        path: urlPath,
        status: 0,
        role: identity.role,
        requestId,
        idempotencyKey,
        durationMs: Math.round(performance.now() - start),
        fallback: false,
        errorMessage: error instanceof Error ? error.message : String(error),
      })
      setLastPayloads(options.payload, { error: String(error) })
      return {
        ok: false,
        status: 0,
        data: null as T,
        raw: { error: String(error) },
        request_id: requestId,
        idempotency_key: idempotencyKey,
        fallback: false,
        msg: error instanceof Error ? error.message : String(error),
      }
    } finally {
      clearTimeout(timeout)
    }
  }

  private fixMock(path: string, method: HttpMethod): unknown {
    try {
      return this.mockInnerData(path, method)
    } catch {
      return { ok: true }
    }
  }

  healthz(identity: IdentityProfile) {
    return this.request<unknown>('GET', '/healthz', identity)
  }

  getStaffReports(
    identity: IdentityProfile,
    query: { org_id: string; department_id: string; record_date: string; user_id?: string },
  ) {
    return this.request<{ reports?: unknown[] }>('GET', '/api/v1/report/staff', identity, {
      query: {
        org_id: query.org_id,
        department_id: query.department_id,
        record_date: query.record_date,
        user_id: query.user_id,
      },
    })
  }

  postStaffReport(payload: unknown, identity: IdentityProfile) {
    return this.request<unknown>('POST', '/api/v1/report/staff', identity, { payload, write: true })
  }

  getManagerReports(
    identity: IdentityProfile,
    query: { org_id: string; dept_id: string; summary_date: string; manager_user_id: string },
  ) {
    return this.request<{ reports?: unknown[] }>('GET', '/api/v1/report/manager', identity, {
      query: {
        org_id: query.org_id,
        dept_id: query.dept_id,
        summary_date: query.summary_date,
        manager_user_id: query.manager_user_id,
      },
    })
  }

  postManagerReport(payload: unknown, identity: IdentityProfile) {
    return this.request<unknown>('POST', '/api/v1/report/manager', identity, { payload, write: true })
  }

  runDream(payload: unknown, identity: IdentityProfile) {
    return this.request<unknown>('POST', '/internal/dream/run', identity, { payload, write: true })
  }

  commitDecision(payload: unknown, identity: IdentityProfile) {
    return this.request<unknown>('POST', '/api/v1/decision/commit', identity, { payload, write: true })
  }

  getTasks(identity: IdentityProfile) {
    return this.request<{ tasks?: unknown[] }>('GET', '/api/v1/tasks', identity)
  }

  createTask(payload: unknown, identity: IdentityProfile) {
    return this.request<unknown>('POST', '/api/v1/tasks', identity, { payload, write: true })
  }

  updateTask(taskId: string, payload: unknown, identity: IdentityProfile) {
    return this.request<unknown>('PATCH', `/api/v1/tasks/${encodeURIComponent(taskId)}`, identity, { payload, write: true })
  }

  getIncidents(identity: IdentityProfile) {
    return this.request<unknown>('GET', '/api/v1/incidents', identity)
  }

  createIncident(payload: unknown, identity: IdentityProfile) {
    return this.request<unknown>('POST', '/api/v1/incidents', identity, { payload, write: true })
  }
}

export const apiClient = new AutomageApiClient()
