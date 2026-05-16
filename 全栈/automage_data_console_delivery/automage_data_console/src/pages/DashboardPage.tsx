import { useQuery } from '@tanstack/react-query'
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { PageHeader } from '../components/common/PageHeader'
import { IntegrationStatusMatrix } from '../components/monitor/IntegrationStatusMatrix'
import { AuditTimeline } from '../components/monitor/AuditTimeline'
import { apiClient } from '../lib/apiClient'
import { useAuth } from '../contexts/AuthContext'
import { useRunContextStore } from '../store/useRunContextStore'
import { identityProfiles } from '../config/identities'
import { normalizeApiTask } from '../lib/taskUtils'

const PIE_COLORS = ['#0f172a', '#475569', '#94a3b8']

const statusLabel: Record<string, string> = {
  pending: '待处理',
  in_progress: '进行中',
  done: '已完成',
  completed: '已完成',
}

export function DashboardPage() {
  const { user } = useAuth()
  const { runDate } = useRunContextStore()
  const isAdmin = (user?.meta as any)?.is_admin === true

  // Build identity from logged-in user
  const myIdentity = {
    userId: user?.username ?? 'system',
    role: (user?.role ?? 'staff') as 'staff' | 'manager' | 'executive',
    nodeId: 'console',
    level: (user?.level ?? 'l1_staff') as 'l1_staff' | 'l2_manager' | 'l3_executive',
    managerNodeId: '',
    orgId: user?.org_id ?? 'org_automage_mvp',
    departmentId: user?.department_id ?? 'dept_mvp_core',
  }

  // For staff report aggregation, use manager identity if admin, else own
  const mgrIdentity = isAdmin ? identityProfiles.manager : myIdentity

  const health = useQuery({
    queryKey: ['healthz'],
    queryFn: () => apiClient.healthz(myIdentity),
    refetchInterval: 60_000,
  })

  const tasks = useQuery({
    queryKey: ['tasks', 'dashboard', user?.username],
    queryFn: async () => {
      const res = await apiClient.getTasks(myIdentity)
      if (!res.ok) throw new Error(res.msg ?? 'tasks')
      const list = (res.data as { tasks?: unknown[] })?.tasks ?? []
      return list.map(normalizeApiTask).filter((t): t is NonNullable<typeof t> => Boolean(t))
    },
  })

  const staffCount = useQuery({
    queryKey: ['staffReports', 'dash', runDate],
    queryFn: async () => {
      const res = await apiClient.getStaffReports(mgrIdentity, {
        org_id: mgrIdentity.orgId,
        department_id: mgrIdentity.departmentId,
        record_date: runDate,
      })
      if (!res.ok) throw new Error(res.msg ?? 'staff')
      return ((res.data as { reports?: unknown[] })?.reports ?? []).length
    },
    enabled: isAdmin || user?.role === 'manager',
    refetchInterval: 120_000,
  })

  const taskRows = tasks.data ?? []
  const taskStats = [
    { name: statusLabel.pending ?? '待处理', value: taskRows.filter((t) => t.status === 'pending').length, color: PIE_COLORS[0] },
    { name: statusLabel.in_progress ?? '进行中', value: taskRows.filter((t) => t.status === 'in_progress').length, color: PIE_COLORS[1] },
    { name: '其他', value: taskRows.filter((t) => t.status !== 'pending' && t.status !== 'in_progress').length, color: PIE_COLORS[2] },
  ]

  const totalTasks = taskStats.reduce((s, x) => s + x.value, 0)

  return (
    <div className="space-y-8">
      <PageHeader
        title="运行总览"
        description={`运行日 ${runDate} · ${user?.display_name ?? user?.username} · ${isAdmin ? '管理员视图' : user?.role === 'executive' ? '老板视图' : '员工视图'}`}
      />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Metric title="后端 /healthz" value={health.isLoading ? '…' : health.data?.ok ? '正常' : health.data?.msg ?? '异常'} hint={health.isError ? (health.error as Error).message : undefined} />
        {(isAdmin || user?.role === 'manager') && (
          <Metric title={`员工日报 (${runDate})`} value={staffCount.isLoading ? '…' : String(staffCount.data ?? '—')} hint={staffCount.isError ? '需管理权限' : undefined} />
        )}
        <Metric title="可见任务" value={tasks.isLoading ? '…' : String(taskRows.length)} />
        <Metric title="运行模式" value="生产环境" hint="Docker · PostgreSQL · Redis" />
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <div className="console-panel p-5">
          <p className="console-title mb-4">任务状态分布</p>
          {totalTasks === 0 ? (
            <p className="py-8 text-center text-sm text-slate-400">暂无任务数据</p>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={taskStats} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} innerRadius={50} label={({ name, value }) => `${name} ${value}`}>
                  {taskStats.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
        <AuditTimeline />
      </section>

      <IntegrationStatusMatrix />
    </div>
  )
}

function Metric({ title, value, hint }: { title: string; value: string; hint?: string }) {
  return (
    <div className="stat-card-accent">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{title}</p>
      <p className="mt-2 text-2xl font-semibold tabular-nums text-slate-900">{value}</p>
      {hint ? <p className="mt-1 text-xs text-amber-700">{hint}</p> : null}
    </div>
  )
}
