import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../../contexts/AuthContext'
import { apiClient } from '../../lib/apiClient'
import { useRunContextStore } from '../../store/useRunContextStore'
import { identityProfiles } from '../../config/identities'
import { AlertTriangle, CheckCircle, ClipboardList, TrendingUp } from 'lucide-react'
import { PageHeader } from '../../components/common/PageHeader'

export function StrategyDashboard() {
  const { user } = useAuth()
  const { runDate } = useRunContextStore()

  const execIdentity = {
    ...identityProfiles.executive,
    userId: user?.username ?? 'chenzong',
    orgId: user?.org_id ?? 'org_automage_mvp',
  }

  const managerReports = useQuery({
    queryKey: ['managerReports', 'exec', runDate],
    queryFn: async () => {
      const res = await apiClient.getManagerReports(execIdentity, {
        org_id: execIdentity.orgId,
        dept_id: execIdentity.departmentId || 'dept_mvp_core',
        summary_date: runDate,
        manager_user_id: execIdentity.userId,
      })
      if (!res.ok) throw new Error(res.msg ?? '查询汇总失败')
      return (res.data as { reports?: unknown[] })?.reports ?? []
    },
    refetchInterval: 60_000,
  })

  const tasks = useQuery({
    queryKey: ['tasks', 'exec', runDate],
    queryFn: async () => {
      const res = await apiClient.getTasks(execIdentity)
      if (!res.ok) throw new Error(res.msg ?? '查询任务失败')
      return (res.data as { tasks?: unknown[] })?.tasks ?? []
    },
    refetchInterval: 60_000,
  })

  const reports = Array.isArray(managerReports.data) ? managerReports.data : []
  const yellowOrRed = reports.filter((r: any) => {
    const h = r?.overall_health || r?.report?.overall_health
    return h === 'yellow' || h === 'red'
  }).length
  const taskList = Array.isArray(tasks.data) ? tasks.data : []
  const pending = taskList.filter((t: any) => t.status === 'pending').length

  return (
    <div className="space-y-8">
      <PageHeader
        title="战略视图"
        description={`运行日 ${runDate} · 组织 ${user?.org_id ?? 'org_automage_mvp'}`}
      />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <BossCard icon={<ClipboardList size={18} />} label="今日汇总" value={String(reports.length)} color="blue" />
        <BossCard icon={<AlertTriangle size={18} />} label="需关注部门" value={String(yellowOrRed)} color={yellowOrRed > 0 ? 'amber' : 'emerald'} />
        <BossCard icon={<TrendingUp size={18} />} label="待处理任务" value={String(pending)} color={pending > 5 ? 'rose' : 'slate'} />
        <BossCard icon={<CheckCircle size={18} />} label="总任务数" value={String(taskList.length)} color="emerald" />
      </div>
    </div>
  )
}

function BossCard({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: string; color: string }) {
  const borders: Record<string, string> = {
    blue: 'border-l-blue-600',
    emerald: 'border-l-emerald-600',
    amber: 'border-l-amber-500',
    rose: 'border-l-rose-600',
    slate: 'border-l-slate-400',
  }
  return (
    <div className={`console-panel border-l-[3px] p-5 ${borders[color] ?? borders.slate}`}>
      <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-slate-500">
        <span className="text-slate-400">{icon}</span>
        <span>{label}</span>
      </div>
      <p className="mt-3 text-2xl font-semibold tabular-nums text-slate-900">{value}</p>
    </div>
  )
}
