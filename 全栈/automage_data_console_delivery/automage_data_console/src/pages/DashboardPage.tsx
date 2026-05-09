import { useQuery } from '@tanstack/react-query'
import { Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { IntegrationStatusMatrix } from '../components/monitor/IntegrationStatusMatrix'
import { AuditTimeline } from '../components/monitor/AuditTimeline'
import { apiClient } from '../lib/apiClient'
import { useIdentityStore } from '../store/useIdentityStore'
import { useRunContextStore } from '../store/useRunContextStore'
import { identityProfiles } from '../config/identities'
import { normalizeApiTask } from '../lib/taskUtils'

export function DashboardPage() {
  const { identity } = useIdentityStore()
  const { runDate } = useRunContextStore()

  const health = useQuery({
    queryKey: ['healthz'],
    queryFn: () => apiClient.healthz(identity),
    refetchInterval: 60_000,
  })

  const tasks = useQuery({
    queryKey: ['tasks', 'dashboard', identity.userId],
    queryFn: async () => {
      const res = await apiClient.getTasks(identity)
      if (!res.ok) throw new Error(res.msg ?? 'tasks')
      const list = (res.data as { tasks?: unknown[] })?.tasks ?? []
      return list.map(normalizeApiTask).filter((t): t is NonNullable<typeof t> => Boolean(t))
    },
  })

  const staffCount = useQuery({
    queryKey: ['staffReports', 'dash', runDate],
    queryFn: async () => {
      const mgr = identityProfiles.manager
      const res = await apiClient.getStaffReports(mgr, {
        org_id: mgr.orgId,
        department_id: mgr.departmentId,
        record_date: runDate,
      })
      if (!res.ok) throw new Error(res.msg ?? 'staff')
      return ((res.data as { reports?: unknown[] })?.reports ?? []).length
    },
    refetchInterval: 120_000,
  })

  const taskRows = tasks.data ?? []
  const taskStats = [
    { name: 'pending', value: taskRows.filter((t) => t.status === 'pending').length },
    { name: 'in_progress', value: taskRows.filter((t) => t.status === 'in_progress').length },
    { name: '其他', value: taskRows.filter((t) => t.status !== 'pending' && t.status !== 'in_progress').length },
  ]

  return (
    <div className="space-y-4">
      <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <Metric
          title="后端 /healthz"
          value={health.isLoading ? '…' : health.data?.ok ? 'OK' : health.data?.msg ?? '异常'}
          hint={health.isError ? (health.error as Error).message : undefined}
        />
        <Metric title={`Staff 日报条数 (${runDate})`} value={staffCount.isLoading ? '…' : String(staffCount.data ?? '—')} hint={staffCount.isError ? '需 Manager 查询权限与真实后端' : undefined} />
        <Metric title="当前身份可见任务" value={tasks.isLoading ? '…' : String(taskRows.length)} />
        <Metric title="主链路" value="以真实 API 为准" hint="关闭 Demo 后本页数据来自后端" />
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <div className="console-panel h-72 p-4">
          <p className="console-title mb-2">任务状态分布（当前身份）</p>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={taskStats} dataKey="value" nameKey="name" outerRadius={90} fill="#2563eb" />
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <AuditTimeline />
      </section>

      <IntegrationStatusMatrix />
    </div>
  )
}

function Metric({ title, value, hint }: { title: string; value: string; hint?: string }) {
  return (
    <div className="console-panel p-4">
      <p className="text-sm text-slate-500">{title}</p>
      <p className="mt-2 text-2xl font-semibold text-slate-900">{value}</p>
      {hint ? <p className="mt-1 text-xs text-amber-700">{hint}</p> : null}
    </div>
  )
}
