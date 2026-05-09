import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../lib/apiClient'
import { useIdentityStore } from '../../store/useIdentityStore'
import { useRuntimeStore } from '../../store/useRuntimeStore'

function extractIncidentList(data: unknown): unknown[] {
  if (!data || typeof data !== 'object') return []
  const d = data as Record<string, unknown>
  if (Array.isArray(d.incidents)) return d.incidents
  if (Array.isArray(d.items)) return d.items
  if (Array.isArray(d.data)) return d.data as unknown[]
  return []
}

export function IncidentBoard() {
  const { identity } = useIdentityStore()
  const demoMode = useRuntimeStore((s) => s.demoMode)

  const fallback = [
    {
      id: 'INC-20260506-API-SKILL-001',
      severity: 'high',
      status: 'open',
      source: 'manager_summary',
      title: '示例：API/Skill 端到端链路未完成（本地占位）',
    },
  ]

  const q = useQuery({
    queryKey: ['incidents', identity.userId],
    queryFn: async () => {
      const res = await apiClient.getIncidents(identity)
      if (!res.ok) throw new Error(res.msg ?? 'GET /api/v1/incidents 失败')
      return extractIncidentList(res.data)
    },
    enabled: !demoMode,
  })

  const list = demoMode ? fallback : ((q.data as Array<Record<string, unknown>>) ?? [])

  return (
    <div className="console-panel p-4">
      <p className="console-title mb-3">异常中心</p>
      {demoMode ? <p className="mb-2 text-xs text-amber-800">Demo 模式：显示占位列表。关闭 Demo 后走 GET /api/v1/incidents。</p> : null}
      {!demoMode && q.isLoading ? <p className="text-sm text-slate-500">加载中…</p> : null}
      {!demoMode && q.isError ? <p className="text-sm text-rose-600">{(q.error as Error).message}</p> : null}
      {list.map((inc) => {
        const row = inc as Record<string, unknown>
        const id = String(row.id ?? row.incident_id ?? row.incident_public_id ?? 'unknown')
        const title = String(row.title ?? row.name ?? '（无标题）')
        const severity = String(row.severity ?? '—')
        const status = String(row.status ?? '—')
        const source = String(row.source ?? row.source_type ?? '—')
        return (
          <div key={id} className="mt-2 rounded-lg bg-rose-50 p-3 text-sm text-rose-700">
            <p className="font-semibold">{title}</p>
            <p className="mt-1 text-xs">
              {id} | {source} | {severity} | {status}
            </p>
          </div>
        )
      })}
      {!demoMode && !q.isLoading && list.length === 0 ? <p className="text-sm text-slate-500">暂无异常记录。</p> : null}
    </div>
  )
}
